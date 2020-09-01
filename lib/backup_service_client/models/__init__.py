# coding: utf-8

# flake8: noqa
"""
    Couchbase Backup Service API

    This is REST API allows users to remotely schedule and run backups, restores and merges as well as to explore various archives for all there Couchbase Clusters.  # noqa: E501

    OpenAPI spec version: 0.1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

# import models into model package
from backup_service_client.models.body import Body
from backup_service_client.models.body1 import Body1
from backup_service_client.models.body2 import Body2
from backup_service_client.models.body3 import Body3
from backup_service_client.models.body4 import Body4
from backup_service_client.models.body5 import Body5
from backup_service_client.models.body6 import Body6
from backup_service_client.models.cloud_credentials import CloudCredentials
from backup_service_client.models.error import Error
from backup_service_client.models.inline_response200 import InlineResponse200
from backup_service_client.models.inline_response2001 import InlineResponse2001
from backup_service_client.models.inline_response2002 import InlineResponse2002
from backup_service_client.models.inline_response2003 import InlineResponse2003
from backup_service_client.models.plan import Plan
from backup_service_client.models.repository import Repository
from backup_service_client.models.repository_bucket import RepositoryBucket
from backup_service_client.models.repository_cloud_info import RepositoryCloudInfo
from backup_service_client.models.repository_health import RepositoryHealth
from backup_service_client.models.repository_scheduled import RepositoryScheduled
from backup_service_client.models.service_configuration import ServiceConfiguration
from backup_service_client.models.services import Services
from backup_service_client.models.task_run import TaskRun
from backup_service_client.models.task_run_node_runs import TaskRunNodeRuns
from backup_service_client.models.task_template import TaskTemplate
from backup_service_client.models.task_template_options import TaskTemplateOptions
from backup_service_client.models.task_template_schedule import TaskTemplateSchedule
