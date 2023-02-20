import json
import os

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevConfig(DefaultConfig):
    USE_LOCAL_DATA = False

    vcap_services = json.loads(os.environ["VCAP_SERVICES"])

    if "aws-s3-bucket" in vcap_services:
        bucket = next(
            (
                bucket
                for bucket in vcap_services["aws-s3-bucket"]
                if bucket["name"] == "form-uploads-dev"
            ),
            vcap_services["aws-s3-bucket"][0],
        )
        s3_credentials = bucket["credentials"]
        AWS_REGION = s3_credentials["aws_region"]
        AWS_ACCESS_KEY_ID = s3_credentials["aws_access_key_id"]
        AWS_SECRET_ACCESS_KEY = s3_credentials["aws_secret_access_key"]
        AWS_BUCKET_NAME = s3_credentials["bucket_name"]
