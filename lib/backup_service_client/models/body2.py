# coding: utf-8

"""
    Couchbase Backup Service API

    This is REST API allows users to remotely schedule and run backups, restores and merges as well as to explore various archives for all there Couchbase Clusters.  # noqa: E501

    OpenAPI spec version: 0.1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six


class Body2(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'plan': 'str',
        'archive': 'str',
        'bucket_name': 'str',
        'cloud_credential_name': 'str',
        'cloud_staging_dir': 'str',
        'cloud_credentials_id': 'str',
        'cloud_credentials_key': 'str',
        'cloud_endpoint': 'str',
        'cloud_force_path_style': 'str'
    }

    attribute_map = {
        'plan': 'plan',
        'archive': 'archive',
        'bucket_name': 'bucket_name',
        'cloud_credential_name': 'cloud_credential_name',
        'cloud_staging_dir': 'cloud_staging_dir',
        'cloud_credentials_id': 'cloud_credentials_id',
        'cloud_credentials_key': 'cloud_credentials_key',
        'cloud_endpoint': 'cloud_endpoint',
        'cloud_force_path_style': 'cloud_force_path_style'
    }

    def __init__(self, plan=None, archive=None, bucket_name=None, cloud_credential_name=None, cloud_staging_dir=None, cloud_credentials_id=None, cloud_credentials_key=None, cloud_endpoint=None, cloud_force_path_style=None):  # noqa: E501
        """Body2 - a model defined in Swagger"""  # noqa: E501
        self._plan = None
        self._archive = None
        self._bucket_name = None
        self._cloud_credential_name = None
        self._cloud_staging_dir = None
        self._cloud_credentials_id = None
        self._cloud_credentials_key = None
        self._cloud_endpoint = None
        self._cloud_force_path_style = None
        self.discriminator = None
        self.plan = plan
        self.archive = archive
        if bucket_name is not None:
            self.bucket_name = bucket_name
        if cloud_credential_name is not None:
            self.cloud_credential_name = cloud_credential_name
        if cloud_staging_dir is not None:
            self.cloud_staging_dir = cloud_staging_dir
        if cloud_credentials_id is not None:
            self.cloud_credentials_id = cloud_credentials_id
        if cloud_credentials_key is not None:
            self.cloud_credentials_key = cloud_credentials_key
        if cloud_endpoint is not None:
            self.cloud_endpoint = cloud_endpoint
        if cloud_force_path_style is not None:
            self.cloud_force_path_style = cloud_force_path_style

    @property
    def plan(self):
        """Gets the plan of this Body2.  # noqa: E501

        The plan to use as base  # noqa: E501

        :return: The plan of this Body2.  # noqa: E501
        :rtype: str
        """
        return self._plan

    @plan.setter
    def plan(self, plan):
        """Sets the plan of this Body2.

        The plan to use as base  # noqa: E501

        :param plan: The plan of this Body2.  # noqa: E501
        :type: str
        """
        if plan is None:
            raise ValueError("Invalid value for `plan`, must not be `None`")  # noqa: E501

        self._plan = plan

    @property
    def archive(self):
        """Gets the archive of this Body2.  # noqa: E501

        The location to use as backup archive  # noqa: E501

        :return: The archive of this Body2.  # noqa: E501
        :rtype: str
        """
        return self._archive

    @archive.setter
    def archive(self, archive):
        """Sets the archive of this Body2.

        The location to use as backup archive  # noqa: E501

        :param archive: The archive of this Body2.  # noqa: E501
        :type: str
        """
        if False and archive is None:
            raise ValueError("Invalid value for `archive`, must not be `None`")  # noqa: E501

        self._archive = archive

    @property
    def bucket_name(self):
        """Gets the bucket_name of this Body2.  # noqa: E501

        Wheter or not this repository applies to one bucket or the whole cluster.  # noqa: E501

        :return: The bucket_name of this Body2.  # noqa: E501
        :rtype: str
        """
        return self._bucket_name

    @bucket_name.setter
    def bucket_name(self, bucket_name):
        """Sets the bucket_name of this Body2.

        Wheter or not this repository applies to one bucket or the whole cluster.  # noqa: E501

        :param bucket_name: The bucket_name of this Body2.  # noqa: E501
        :type: str
        """

        self._bucket_name = bucket_name

    @property
    def cloud_credential_name(self):
        """Gets the cloud_credential_name of this Body2.  # noqa: E501

        Use a set of already registered credentials. This option is mutually exclusive to the cloud_credentials_key and cloud_credentials_id and one of those sets must be provided for repositories in the cloud.  # noqa: E501

        :return: The cloud_credential_name of this Body2.  # noqa: E501
        :rtype: str
        """
        return self._cloud_credential_name

    @cloud_credential_name.setter
    def cloud_credential_name(self, cloud_credential_name):
        """Sets the cloud_credential_name of this Body2.

        Use a set of already registered credentials. This option is mutually exclusive to the cloud_credentials_key and cloud_credentials_id and one of those sets must be provided for repositories in the cloud.  # noqa: E501

        :param cloud_credential_name: The cloud_credential_name of this Body2.  # noqa: E501
        :type: str
        """

        self._cloud_credential_name = cloud_credential_name

    @property
    def cloud_staging_dir(self):
        """Gets the cloud_staging_dir of this Body2.  # noqa: E501

        The location to use as a staging directory. It is required for repositories in the cloud.  # noqa: E501

        :return: The cloud_staging_dir of this Body2.  # noqa: E501
        :rtype: str
        """
        return self._cloud_staging_dir

    @cloud_staging_dir.setter
    def cloud_staging_dir(self, cloud_staging_dir):
        """Sets the cloud_staging_dir of this Body2.

        The location to use as a staging directory. It is required for repositories in the cloud.  # noqa: E501

        :param cloud_staging_dir: The cloud_staging_dir of this Body2.  # noqa: E501
        :type: str
        """

        self._cloud_staging_dir = cloud_staging_dir

    @property
    def cloud_credentials_id(self):
        """Gets the cloud_credentials_id of this Body2.  # noqa: E501

        The ID used to connect to object store.  # noqa: E501

        :return: The cloud_credentials_id of this Body2.  # noqa: E501
        :rtype: str
        """
        return self._cloud_credentials_id

    @cloud_credentials_id.setter
    def cloud_credentials_id(self, cloud_credentials_id):
        """Sets the cloud_credentials_id of this Body2.

        The ID used to connect to object store.  # noqa: E501

        :param cloud_credentials_id: The cloud_credentials_id of this Body2.  # noqa: E501
        :type: str
        """

        self._cloud_credentials_id = cloud_credentials_id

    @property
    def cloud_credentials_key(self):
        """Gets the cloud_credentials_key of this Body2.  # noqa: E501

        The secret key used to connect to object store.  # noqa: E501

        :return: The cloud_credentials_key of this Body2.  # noqa: E501
        :rtype: str
        """
        return self._cloud_credentials_key

    @cloud_credentials_key.setter
    def cloud_credentials_key(self, cloud_credentials_key):
        """Sets the cloud_credentials_key of this Body2.

        The secret key used to connect to object store.  # noqa: E501

        :param cloud_credentials_key: The cloud_credentials_key of this Body2.  # noqa: E501
        :type: str
        """

        self._cloud_credentials_key = cloud_credentials_key

    @property
    def cloud_endpoint(self):
        """Gets the cloud_endpoint of this Body2.  # noqa: E501

        If provided it overrides the default endpoint use for the cloud provider.  # noqa: E501

        :return: The cloud_endpoint of this Body2.  # noqa: E501
        :rtype: str
        """
        return self._cloud_endpoint

    @cloud_endpoint.setter
    def cloud_endpoint(self, cloud_endpoint):
        """Sets the cloud_endpoint of this Body2.

        If provided it overrides the default endpoint use for the cloud provider.  # noqa: E501

        :param cloud_endpoint: The cloud_endpoint of this Body2.  # noqa: E501
        :type: str
        """

        self._cloud_endpoint = cloud_endpoint

    @property
    def cloud_force_path_style(self):
        """Gets the cloud_force_path_style of this Body2.  # noqa: E501

        When provided and using S3 or S3 compatible storages it will use the old S3 path style.  # noqa: E501

        :return: The cloud_force_path_style of this Body2.  # noqa: E501
        :rtype: str
        """
        return self._cloud_force_path_style

    @cloud_force_path_style.setter
    def cloud_force_path_style(self, cloud_force_path_style):
        """Sets the cloud_force_path_style of this Body2.

        When provided and using S3 or S3 compatible storages it will use the old S3 path style.  # noqa: E501

        :param cloud_force_path_style: The cloud_force_path_style of this Body2.  # noqa: E501
        :type: str
        """

        self._cloud_force_path_style = cloud_force_path_style

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(Body2, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Body2):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
