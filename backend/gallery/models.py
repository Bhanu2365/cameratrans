import uuid
from django.db import models

class Batch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=120, default="Event photos")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    active = models.BooleanField(default=True)
    frame = models.ImageField(upload_to="frames/", blank=True)

    @property
    def is_available(self):
        from django.utils import timezone
        return self.active and self.expires_at > timezone.now()

    @property
    def photo_count(self):
        return self.photos.count()

    def delete(self, *args, **kwargs):
        # Django does not remove FileField files when a model row is deleted.
        for photo in self.photos.all():
            photo.image.delete(save=False)
            if photo.preview:
                photo.preview.delete(save=False)
            if photo.framed:
                photo.framed.delete(save=False)
        if self.frame:
            self.frame.delete(save=False)
        return super().delete(*args, **kwargs)

class Photo(models.Model):
    batch = models.ForeignKey(Batch, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="photos/originals/")
    preview = models.ImageField(upload_to="photos/previews/", blank=True)
    framed = models.ImageField(upload_to="photos/framed/", blank=True)
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.PositiveBigIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)
