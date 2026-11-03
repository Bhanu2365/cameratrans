import django.db.models.deletion
import uuid
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Batch", fields=[
            ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ("title", models.CharField(default="Event photos", max_length=120)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("expires_at", models.DateTimeField()),
            ("active", models.BooleanField(default=True)),
            ("frame", models.ImageField(blank=True, upload_to="frames/")),
        ]),
        migrations.CreateModel(name="Photo", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("image", models.ImageField(upload_to="photos/originals/")),
            ("preview", models.ImageField(blank=True, upload_to="photos/previews/")),
            ("framed", models.ImageField(blank=True, upload_to="photos/framed/")),
            ("original_filename", models.CharField(max_length=255)),
            ("uploaded_at", models.DateTimeField(auto_now_add=True)),
            ("file_size", models.PositiveBigIntegerField(default=0)),
            ("downloads", models.PositiveIntegerField(default=0)),
            ("batch", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="photos", to="gallery.batch")),
        ]),
    ]
