from rest_framework import serializers
from . import models


class Video(serializers.ModelSerializer):

    class Meta:
        model = models.Video
        fields = '__all__'


class VideoFile(serializers.Serializer):
    file = serializers.FileField()

    class Meta:
        fields = ['file']
    # class Meta:
    #     model = models.VideoFile
    #     fields = '__all__'
