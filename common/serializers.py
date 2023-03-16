import uuid
import shutil
from pathlib import Path
from rest_framework import serializers
from django.conf import settings

from common.models import File
from common.utils.aws_utils import (
    upload_file_to_s3,
    get_resource_s3_url,
    escape_file_name,
    get_s3_signed_url,
)


class FileUploadSerializer(serializers.Serializer):
    object_id = serializers.IntegerField(write_only=True)
    files = serializers.ListField(child=serializers.FileField(), write_only=True)

    def validate(self, attrs):
        files = attrs["files"]
        for file in files:
            if file.size > self.context["file_size_limit"] * 1024**2:
                raise serializers.ValidationError(
                    f"Upload size is restricted to {self.context['file_size_limit']} Mb"
                )
        return attrs

    def create(self, data):
        files = data["files"]
        object_id = data["object_id"]

        temp_id = uuid.uuid4().hex
        # Create temporary upload folder
        base_file_path = f"/tmp/uploads/{temp_id}/"
        shutil.rmtree(base_file_path, ignore_errors=True)
        Path(base_file_path).mkdir(parents=True, exist_ok=True)
        # Save uploaded files into the folder
        bucket_sub_folder = self.context["bucket_sub_folder"]
        is_public = self.context["is_public"]
        uploaded_by = self.context["request"].user

        file_objects = []
        for file in files:
            if file:
                # Save file to a temp location
                file_name_components = file._name.split(".")
                file_ext = file_name_components.pop()
                file_name = ".".join(file_name_components).lower()
                file_name = f"{escape_file_name(file_name)}.{file_ext}".lower()
                file_path = f'{base_file_path}{file_name}'.lower()
                with open(file_path, "wb") as file_write:
                    file_write.write(file.file.getbuffer())
                s3_key = f"{bucket_sub_folder}/{object_id}/{file_name}"
                upload_file_to_s3(
                    key=s3_key,
                    local_file_path=file_path,
                    is_public=is_public,
                    bucket=settings.S3_FILES_BUCKET,
                )
                file_url = get_resource_s3_url(key=s3_key)

                file_objects.append(
                    File.objects.create(
                        name=file_name,
                        key=s3_key,
                        url=file_url,
                        s3_bucket=settings.S3_FILES_BUCKET,
                        uploaded_by=uploaded_by,
                        size_kb=file.size / 1024,
                        content_type=file.content_type,
                    )
                )
        return file_objects


class FileSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    def get_uploaded_by(self, instance):
        return instance.uploaded_by.username if instance.uploaded_by else None

    def get_download_url(self, instance):
        if instance.s3_bucket and instance.key:
            return get_s3_signed_url(instance.s3_bucket, instance.key)
        return ""

    class Meta:
        model = File
        fields = (
            "name",
            "size_kb",
            "id",
            "created_at",
            "uploaded_by",
            "url",
            "download_url",
        )
