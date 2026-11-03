from rest_framework import serializers
from .models import Batch, Photo

class PhotoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    framed_url = serializers.SerializerMethodField()
    class Meta:
        model = Photo
        fields = ["id", "original_filename", "file_size", "url", "preview_url", "framed_url", "downloads"]
    def get_url(self, obj):
        return f"/api/photos/{obj.pk}/download/"
    def get_preview_url(self, obj):
        return f"/api/photos/{obj.pk}/preview/" if obj.preview else ""
    def get_framed_url(self, obj):
        return f"/api/photos/{obj.pk}/framed/" if obj.framed else ""

class BatchSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    photo_count = serializers.IntegerField(read_only=True)
    has_frame = serializers.SerializerMethodField()
    class Meta:
        model = Batch
        fields = ["id", "title", "created_at", "expires_at", "active", "photo_count", "has_frame", "photos"]
    def get_has_frame(self, obj):
        return bool(obj.frame)
