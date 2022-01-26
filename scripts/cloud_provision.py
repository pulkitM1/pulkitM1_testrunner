from argparse import ArgumentParser
import sys, json, subprocess
import boto3
import paramiko
from google.cloud.compute_v1 import ImagesClient, InstancesClient, ZoneOperationsClient
from google.cloud.compute_v1.types.compute import AccessConfig, AttachedDisk, AttachedDiskInitializeParams, BulkInsertInstanceRequest, BulkInsertInstanceResource, DeleteInstanceRequest, GetFromFamilyImageRequest, InstanceProperties, ListInstancesRequest, NetworkInterface, Operation
import time
"""
  Azure needs to install azure cli 'az' in dispatcher slave
"""

def post_provisioner(host, username, ssh_key_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, key_filename=ssh_key_path)
    ssh.exec_command("echo 'couchbase' | sudo passwd --stdin root",)
    ssh.exec_command("sudo sed -i '/#PermitRootLogin yes/c\PermitRootLogin yes' /etc/ssh/sshd_config")
    ssh.exec_command("sudo sed -i '/PermitRootLogin no/c\PermitRootLogin yes' /etc/ssh/sshd_config")
    ssh.exec_command("sudo sed -i '/PermitRootLogin forced-commands-only/c\#PermitRootLogin forced-commands-only' /etc/ssh/sshd_config")
    ssh.exec_command("sudo sed -i '/PasswordAuthentication no/c\PasswordAuthentication yes' /etc/ssh/sshd_config")
    ssh.exec_command("sudo service sshd restart")
    # terminate the instance after 12 hours
    ssh.exec_command("sudo shutdown -P +720")

def aws_terminate(name):
    ec2_client = boto3.client('ec2')
    instances = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    name
                ]
            }
        ]
    )
    instance_ids = []
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])
    if instance_ids:
        ec2_client.terminate_instances(
            InstanceIds=instance_ids
        )

AWS_AMI_MAP = {
    "couchbase": {
        "amzn2": {
            "aarch64": "ami-0289ff69e0069c2ed",
            "x86_64": "ami-070ac986a212c4d9b"
        }
    },
    "elastic-fts": "ami-0c48f8b3129e57beb",
    "localstack": "ami-0702052d7d7f58aad"
}

def aws_get_servers(name, count, os, type, ssh_key_path, architecture=None):
    instance_type = "t3.xlarge"
    ssh_username = "ec2-user"
    
    if type != "couchbase":
        image_id = AWS_AMI_MAP[type]
        ssh_username = "centos"
    else:
        image_id = AWS_AMI_MAP["couchbase"][os][architecture]
        if architecture == "aarch64":
            instance_type = "t4g.xlarge"

    ec2_resource = boto3.resource('ec2', region_name='us-east-1')
    ec2_client = boto3.client('ec2', region_name='us-east-1')

    instances = ec2_resource.create_instances(
        ImageId=image_id,
        MinCount=count,
        MaxCount=count,
        InstanceType=instance_type,
        LaunchTemplate={
            'LaunchTemplateName': 'TestrunnerCouchbase',
            'Version': '5'
        },
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': name
                    },
                    {
                        'Key': 'Owner',
                        'Value': 'ServerRegression'
                    }
                ]
            },
        ],
        InstanceInitiatedShutdownBehavior='terminate'
    )

    instance_ids = [instance.id for instance in instances]

    print("Waiting for instances: ", instance_ids)

    ec2_client.get_waiter('instance_status_ok').wait(InstanceIds=instance_ids)

    instances = ec2_client.describe_instances(InstanceIds=instance_ids)
    ips = [instance['PublicDnsName'] for instance in instances['Reservations'][0]['Instances']]

    for ip in ips:
        post_provisioner(ip, ssh_username, ssh_key_path)

    return ips

ZONE = "us-central1-a"
PROJECT = "couchbase-qe"
DISK_SIZE_GB = 40
SSH_USERNAME = "couchbase"

def gcp_terminate(name):
    client = InstancesClient()
    try:
        instances = client.list(ListInstancesRequest(project=PROJECT, zone=ZONE, filter=f"labels.name = {name}"))
        for instance in instances:
            client.delete(DeleteInstanceRequest(instance=instance.name, project=PROJECT, zone=ZONE))
    except Exception:
        return

GCP_TEMPLATE_MAP = {
    "couchbase": {
        "centos7": {
            "x86_64": { "project": "centos-cloud", "family": "centos-7" }
        }
    },
    # TODO
    "elastic-fts": { "project": "couchbase-qe", "image": "" },
    "localstack": { "project": "couchbase-qe", "image": "" }
}

def gcp_wait_for_operation(operation):
    print(f"Waiting for {operation} to complete")
    client = ZoneOperationsClient()
    while True:
        result = client.get(project=PROJECT, zone=ZONE, operation=operation)

        if result.status == Operation.Status.DONE:
            if result.error:
                raise Exception(result.error)
            return result

        time.sleep(1)

# returns two lists, external ips and internal ips
def gcp_get_servers(name, count, os, type, ssh_key_path, architecture):
    machine_type = "e2-standard-4"

    if type != "couchbase":
        image_descriptor = GCP_TEMPLATE_MAP[type]
    else:
        image_descriptor = GCP_TEMPLATE_MAP["couchbase"][os][architecture]

    if "family" in image_descriptor:
        image = ImagesClient().get_from_family(GetFromFamilyImageRequest(project=image_descriptor["project"], family=image_descriptor["family"]))
    else:
        image = ImagesClient().get(project=image_descriptor["project"], image=image_descriptor["image"])

    disk = AttachedDisk(auto_delete=True, boot=True, initialize_params=AttachedDiskInitializeParams(source_image=image.self_link, disk_size_gb=DISK_SIZE_GB))
    network_interface = NetworkInterface(network="global/networks/default", access_configs=[AccessConfig(type_=AccessConfig.Type.ONE_TO_ONE_NAT)])
    instances = BulkInsertInstanceResource(name_pattern=f"{name}-####", count=count, instance_properties=InstanceProperties(labels={ "name": name }, machine_type=machine_type, disks=[disk], network_interfaces=[network_interface]))
    op = InstancesClient().bulk_insert(BulkInsertInstanceRequest(project=PROJECT, zone=ZONE, bulk_insert_instance_resource_resource=instances))

    gcp_wait_for_operation(op.name)

    instances = list(InstancesClient().list(ListInstancesRequest(project=PROJECT, zone=ZONE, filter=f"labels.name = {name}")))

    internal_ips = [instance.network_interfaces[0].network_i_p for instance in instances]
    ips = [instance.network_interfaces[0].access_configs[0].nat_i_p for instance in instances]

    for ip in ips:
        post_provisioner(ip, SSH_USERNAME, ssh_key_path)

    return ips, internal_ips

AZ_TEMPLATE_MAP = {
    "couchbase"  : "qe-image-20211129",
    "elastic-fts": "qe-es-image-20211129",
    "localstack" : "qe-localstack-image-20211129"
}
def az_get_servers(name, count, os, type, ssh_key_path, architecture):
    vm_type = "Standard_B4ms"
    security_group_name = "qe-test-nsg"
    group_name = "qe-test"
    ips = []
    internal_ips = []

    if type != "couchbase":
        image_name = AZ_TEMPLATE_MAP[type]
    else:
        image_name = AZ_TEMPLATE_MAP["couchbase"]

    """ az vm create -g qe-test -n from-w22 --image 'qe-test-image-20211112-westus2' --nsg qe-test-nsg
           --size Standard_B4ms --output json  --count 2 --public-ip-sku Standard
        image_name = "qe-test-image-20211112-westus2"
    """
    for x in range(1, count + 1):
        cmd = "az vm create -g {0} -n {1}{2} --image {3} --nsg {4} --size {5} --public-ip-sku Standard --output json "\
              .format(group_name, name, x, image_name, security_group_name, vm_type)
        print("\ncreate vm {0}{1}".format(name, x))
        stdout = subprocess.check_output(cmd, shell=True)
        if isinstance(stdout, bytes):
            # convert to string to load json
            stdout = stdout.decode('utf-8')
        if isinstance(stdout, str):
            stdout = json.loads(stdout)
            ips.append(stdout["publicIpAddress"])
            internal_ips.append(stdout["privateIpAddress"])
    """ no need post_provisioner run on azure """
    print("public ips of vms: ", ips)
    print("private ips of vms: ", internal_ips)
    return ips, internal_ips

def az_terminate(name):
    group_name = "qe-test"
    cmd = "az vm list |  grep -o '\"computerName\": \"[^\"]*' | grep -o '[^\"]*$' | grep ^{}".format(name)
    vms = subprocess.check_output(cmd, shell=True).decode('utf-8')
    vms = vms.split("\n")
    vms = [s for s in vms if s]
    for vm_name in vms:
        cmd1 = "az vm delete -g {0} -n {1} -y "\
               .format(group_name, vm_name)
        cmd2 = "az network nic delete -g {0} -n {1}VMNic --no-wait"\
                .format(group_name, vm_name)
        cmd3 = "az network public-ip delete -g {0} -n {1}PublicIP"\
                .format(group_name, vm_name)
        print("\ndelete vm {0}".format(name))
        subprocess.check_output(cmd1, shell=True)
        print("\ndelete network of vm {0}".format(name))
        subprocess.check_output(cmd2, shell=True)
        print("\ndelete public ip of vm {0}".format(name))
        subprocess.check_output(cmd3, shell=True)


if __name__ == "__main__":
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="provider")

    providers = ["aws", "gcp", "az"]

    for provider in providers:
        provider_parser = subparsers.add_parser(provider)
        provider_subparsers = provider_parser.add_subparsers(dest="cmd")
        provider_terminate_parser = provider_subparsers.add_parser("terminate")
        provider_terminate_parser.add_argument("name", type=str)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.provider == "aws":
        if args.cmd == "terminate":
            aws_terminate(args.name)
    elif args.provider == "gcp":
        if args.cmd == "terminate":
            gcp_terminate(args.name)
    elif args.provider == "az":
        if args.cmd == "terminate":
            az_terminate(args.name)
