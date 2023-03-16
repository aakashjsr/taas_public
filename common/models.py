from django.db import models
from .utils.aws_utils import delete_files_from_s3


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class File(models.Model):
    name = models.CharField(max_length=1024, null=True, blank=True)
    content_type = models.CharField(max_length=1024, null=True, blank=True)
    size_kb = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    uploaded_by = models.ForeignKey(
        "accounts.User",
        related_name="uploaded_files",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    s3_bucket = models.CharField(max_length=1024, null=True, blank=True)
    key = models.CharField(max_length=1024, null=True, blank=True)
    url = models.TextField(null=True, blank=True)
    hash = models.CharField(max_length=1000, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"File {self.id}"

    def delete(self, *args, **kwargs):
        delete_files_from_s3(self.key, self.s3_bucket)
        return super().delete(*args, **kwargs)
