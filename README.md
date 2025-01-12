# HASS-S3
This custom integration provides a service for interacting with S3, including uploading files to a bucket or copying them within and between buckets. Additionally, it supports the use of S3-compatible services, such as Backblaze or MinIO, through the optional endpoint_url parameter, allowing for seamless integration with alternative storage providers.

Create your S3 bucket via the AWS console, remember bucket names must be unique. I created a bucket with the default access settings (allpublic OFF) and created a bucket name with format `my-bucket-ransom_number` with `random_number` generated [on this website](https://onlinehashtools.com/generate-random-md5-hash).

**Note** for a local and self-hosted alternative checkout the official [Minio integration](https://www.home-assistant.io/integrations/minio/).

## Installation and configuration
Place the `custom_components` folder in your configuration directory (or add its contents to an existing custom_components folder). Add to your Home Assistant configuration UI or add to your `configuration.yaml`:
```yaml
s3:
  aws_access_key_id: AWS_ACCESS_KEY
  aws_secret_access_key: AWS_SECRET_KEY
  region_name: eu-west-1 # optional region, default is us-east-1
  endpoint_url: https://s3.eu-west-1.backblazeb2.com/ # optional, URL for S3-compatible services like Backblaze or MinIO
  default_bucket: my_bucket # optional temporary for old install, please setup this
```

## Services
### Put Service
The s3 entity exposes a `put` service for uploading files to S3.

Example data for service call:

```
{
  "bucket": "my_bucket", # optional, default get from default_bucket
  "key": "my_key/file.jpg",
  "file_path": "/some/path/file.jpg",
  "storage_class": "STANDARD_IA" # optional
  "content_type" : "image/jpeg" # optional
  "tags":  "tag1=aTagValue&tag2=anotherTagValue" # optional
}
```

### Copy Service
The s3 entity exposes a `copy` service for moving files around in S3.

Example data for service call:
```
{
  "bucket": "my_bucket", # optional, default get from default_bucket
  "key_source": "my_key/file_source.jpg",
  "key_destination": "my_key/file_destination.jpg"
}
```

If you need to move items between buckets use this syntax:
```
{
  "bucket_source": "my_source_bucket", # optional, default get from default_bucket
  "key_source": "my_key/file_source.jpg",
  "bucket_destintation": "my_destination_bucket", # optional, default get from default_bucket
  "key_destination": "my_key/file_destination.jpg"
}
```

### Delete Service
The s3 entity exposes a `delete` service for deleting files (objects) from S3.

Example data for service call:
```
{
  "bucket": "my_bucket", # optional, default get from default_bucket
  "key": "my_key/file_source.jpg",
}
```

### Sign URL Service
The S3 entity exposes a `signurl` service for generating pre-signed URLs with a defined validity period for accessing content already stored in S3 with a URL.  Run this action after you call the S3 copy service.  This service generates an event of type s3_signed_url which you can use as a trigger in a subsequent automation.  The event data returns a key-value pair of URL and the pre-signed URL.

Example data for service call:
```
{
  "bucket": "my_bucket", # optional, default get from default_bucket
  "key": "my_key/file_source.jpg",
  "duration": 300
}
```


## Example automation
The following automation uses the [folder_watcher](https://www.home-assistant.io/integrations/folder_watcher/) to automatically upload files created in the local filesystem to S3:

```yaml
- id: '1587784389530'
  alias: upload-file-to-S3
  description: 'When a new file is created, upload to S3'
  trigger:
    event_type: folder_watcher
    platform: event
    event_data:
      event_type: created
  action:
    service: s3.put
    data_template:
      bucket: "my_bucket"
      key: "input/{{ now().year }}/{{ (now().month | string).zfill(2) }}/{{ (now().day | string).zfill(2) }}/{{ trigger.event.data.file }}"
      file_path: "{{ trigger.event.data.path }}"
      storage_class: "STANDARD_IA"
```
Note you must configure `folder_watcher`.

## Accessing S3
I recommend [Filezilla](https://filezilla-project.org/) for connecting to your S3 bucket, free version is available.

## Supported S3 storages

| Provider     | Supported | Tested commands            |
| ------------ | --------- | -------------------------- |
| AWS          | Yes       | put, copy, delete, signurl |
| wasabi       | ?         | -                          |
| Backblaze    | ?         | -                          |
| Cloudflare   | ?         | -                          |
| Oracle OSI   | ?         | -                          |
| Yandex.Cloud | Yes       | put, copy, delete, signurl |
| MinIO        | ?         | -                          |