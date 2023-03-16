import requests
import uuid
import boto3
import logging

from django.conf import settings
from boto3.s3.transfer import S3Transfer
from botocore.client import Config


logger = logging.getLogger(__name__)


def upload_file_to_s3(
    key, local_file_path, is_public=False, bucket=settings.S3_BUCKET_NAME
):
    """
    Uploads file to s3
    :param key:
    :param local_file_path:
    :param is_public:
    :param bucket:
    :return:
    """
    print("shjould not be here:::::")
    transfer = S3Transfer(boto3.client('s3', settings.S3_REGION))
    options = {'ACL': 'public-read'} if is_public else {}
    transfer.upload_file(local_file_path, bucket, key, extra_args=options)


def get_resource_s3_url(key, bucket=settings.S3_FILES_BUCKET):
    """
    Returns s3 url
    :param key:
    :param bucket:
    :return:
    """
    return "https://{}.s3.amazonaws.com/{}".format(bucket, key)


def download_file_from_s3(bucket, key, local_path):
    """
    Downloads files from s3
    :param bucket:
    :param key:
    :param local_path:
    :return:
    """
    resource = boto3.resource('s3')
    my_bucket = resource.Bucket(bucket)
    my_bucket.download_file(key, local_path)


def delete_files_from_s3(key, bucket=settings.S3_BUCKET_NAME):
    """
    Deletes objects from s3
    :param key:
    :param bucket:
    :return:
    """
    s3 = boto3.resource('s3')
    s3.Object(bucket, key).delete()


def get_keys_to_delete_from_s3(old_image_list, new_image_list):
    """
    Returns keys to delete from s3 by difference
    :param old_image_list:
    :param new_image_list:
    :return:
    """
    new_keys = [item["key"] for item in new_image_list]
    old_keys = [item.key for item in old_image_list]
    difference_list = [item for item in old_keys if item not in new_keys]
    return difference_list


def get_s3_signed_url(bucket, key):
    s3 = boto3.client(
        's3', config=Config(signature_version='s3v4'), region_name=settings.S3_REGION
    )
    return s3.generate_presigned_url(
        ClientMethod='get_object', Params={'Bucket': bucket, 'Key': key}
    )


def download_file_from_url(url):
    """
    Used to download s3 files shared buy backmarket API
    :param url: s3 download url of the file
    :return:
    """
    r = requests.get(url, allow_redirects=True)
    if r.status_code == 200:
        abs_url = url.split("?")[0]
        filename = abs_url.split("/")[-1]
        f_path = f"/tmp/{uuid.uuid4().hex}_{filename}"
        open(f_path, "wb").write(r.content)
        return filename, f_path
    return None, None


def escape_file_name(name):
    name = name.replace(' ', '_')
    name = name.replace('ä', 'ae')
    name = name.replace('ö', 'oe')
    name = name.replace('ü', 'ue')
    name = name.replace('ß', 'ss')
    e_chars = [
        '!',
        '"',
        '§',
        '$',
        '%',
        '&',
        '/',
        '(',
        ')',
        '=',
        '?',
        '´',
        '`',
        '@',
        '{',
        '[',
        ']',
        '}',
        '\\',
        '<',
        '>',
        ',',
        '.',
        "'",
        '”',
    ]

    for e in e_chars:
        name = name.replace(e, '')

    return name
