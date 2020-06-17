#!/usr/bin/python3

import boto3
import botocore

from . import provider

class S3(provider.Provider):
    def __init__(self, access_key_id, bucket, endpoint, region, secret_access_key, staging_directory):
        """Create a new S3 provider which allows interaction with S3 masked behind the common 'Provider' interface. All
        required parameters should be those parsed from the ini.
        """
        super().__init__(access_key_id, bucket, endpoint, region, secret_access_key, staging_directory)

        # boto3 will raise an exception if given an empty string as the endpoint_url so we must construct a kwargs
        # dictionary and conditionally populate it.
        kwargs = {}
        if self.endpoint != '':
            kwargs['endpoint_url'] = self.endpoint

        self.resource = boto3.resource('s3', **kwargs)

    def schema_prefix(self):
        """See super class"""
        return 's3://'

    def setup(self):
        """See super class"""
        configuration = {}

        if self.region:
            configuration['LocationConstraint'] = self.region

        try:
            self.resource.create_bucket(Bucket=self.bucket, CreateBucketConfiguration=configuration)
        except botocore.exceptions.ClientError as error:
            error_code = error.response['Error']['Code']
            if error_code != "BucketAlreadyExists":
                raise error

    def teardown(self, info, remote_client):
        """See super class"""
        bucket = self.resource.Bucket(self.bucket)

        for obj in bucket.objects.all():
            obj.delete()

        self._remove_staging_directory(info, remote_client)

provider.Provider.register(S3)
