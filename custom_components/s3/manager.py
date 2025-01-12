import boto3
import botocore
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import (
    CONF_REGION,
    CONF_ACCESS_KEY_ID,
    CONF_SECRET_ACCESS_KEY,
    CONF_ENDPOINT_URL,
    CONF_DEFAULT_BUCKET,
)


class S3ClientError(Exception):
    def __init__(self, text):
        self.txt = text


class S3Client:
    def __init__(self, entry: ConfigEntry):
        self.init_config(entry)

    def init_config(self, entry: ConfigEntry):
        aws_config = {
            CONF_REGION: entry.data[CONF_REGION],
            CONF_ACCESS_KEY_ID: entry.data[CONF_ACCESS_KEY_ID],
            CONF_SECRET_ACCESS_KEY: entry.data[CONF_SECRET_ACCESS_KEY],
        }

        # optional settings
        if CONF_ENDPOINT_URL in entry.data:
            aws_config[CONF_ENDPOINT_URL] = entry.data[CONF_ENDPOINT_URL]

        self._aws_config = aws_config

        self._default_bucket = None
        if CONF_DEFAULT_BUCKET in entry.data:
            self._default_bucket = entry.data[CONF_DEFAULT_BUCKET]

    async def init_client(self, hass: HomeAssistant):
        def boto_client(aws_config: dict):
            return boto3.client("s3", **aws_config)  # Will not raise error.

        self._boto_client = await hass.async_add_executor_job(
            boto_client, self._aws_config
        )

    async def update_listener(self, hass: HomeAssistant, entry: ConfigEntry):
        """Handle options update."""
        self.init_config(entry)
        await self.init_client(hass)

    def get_bucket_name(self, bucket):
        if bucket is None:
            bucket = self._default_bucket

        return bucket

    def upload_file(self, Filename, Bucket, Key, ExtraArgs):
        bucket = self.get_bucket_name(Bucket)

        if bucket is None:
            raise S3ClientError("bucket is None")

        try:
            return self._boto_client.upload_file(
                Filename=Filename, Bucket=bucket, Key=Key, ExtraArgs=ExtraArgs
            )
        except botocore.exceptions.ClientError as err:
            raise S3ClientError(err)

    def copy(self, copy_source, bucket_destination, key_destination):
        if copy_source["Bucket"] is None:
            raise S3ClientError("copy_source is None")

        if bucket_destination is None:
            raise S3ClientError("bucket_destination is None")

        try:
            return self._boto_client.copy(
                copy_source, bucket_destination, key_destination
            )
        except botocore.exceptions.ClientError as err:
            raise S3ClientError(err)

    def delete_object(self, Key, Bucket):
        bucket = self.get_bucket_name(Bucket)

        if bucket is None:
            raise S3ClientError("bucket is None")

        try:
            return self._boto_client.delete_object(Key=Key, Bucket=bucket)
        except botocore.exceptions.ClientError as err:
            raise S3ClientError(err)

    def generate_presigned_url(self, action, Params, ExpiresIn):
        if "Bucket" not in Params or Params["Bucket"] is None:
            Params["Bucket"] = self._default_bucket

        if Params["Bucket"] is None:
            raise S3ClientError("bucket is None")

        try:
            return self._boto_client.generate_presigned_url(action, Params, ExpiresIn)
        except botocore.exceptions.ClientError as err:
            raise S3ClientError(err)
