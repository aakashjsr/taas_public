from abc import ABC, abstractmethod
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from common.serializers import FileUploadSerializer, FileSerializer


class DocumentListUploadView(ListCreateAPIView, ABC):
    @abstractmethod
    def get_is_public(self):
        pass

    @abstractmethod
    def get_model(self):
        pass

    @abstractmethod
    def get_sub_folder(self):
        pass

    def get_file_size_limit(self):
        """
        Returns file size limit for upload in Mb
        """
        return 50

    def get_queryset(self):
        return self.get_model().objects.all()

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = FileSerializer(obj.documents.all(), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        file_keys = list(request.FILES.keys())
        files = [request.FILES[k] for k in file_keys]

        obj = self.get_object()

        serializer = FileUploadSerializer(
            data={"files": files, "object_id": obj.id},
            context={
                "bucket_sub_folder": self.get_sub_folder(),
                "is_public": self.get_is_public(),
                "request": request,
                "file_size_limit": self.get_file_size_limit(),
            },
        )
        serializer.is_valid(raise_exception=True)
        file_objects = serializer.save()
        for f in file_objects:
            obj.documents.add(f)
        return Response({})
