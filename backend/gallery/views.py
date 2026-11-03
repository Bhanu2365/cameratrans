import io
import socket
import zipfile
from datetime import timedelta
from pathlib import Path
from django.core.files.base import ContentFile
from django.http import FileResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from PIL import Image, ImageOps
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import Batch, Photo
from .serializers import BatchSerializer

MAX_UPLOAD = 25 * 1024 * 1024
ALLOWED = {"JPEG", "PNG", "WEBP"}

def lan_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("192.0.2.1", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()

def save_photos(batch, files):
    saved = []
    for upload in files:
        if upload.size > MAX_UPLOAD:
            raise ValueError(f"{upload.name} is larger than 25 MB")
        try:
            upload.seek(0)
            source = Image.open(upload)
            image_format = source.format
            source.verify()
            if image_format not in ALLOWED:
                raise ValueError(f"{upload.name} is not a supported image (JPG, PNG, WebP)")
            upload.seek(0)
            image = ImageOps.exif_transpose(Image.open(upload))
            image.load()
        except (OSError, Image.DecompressionBombError):
            raise ValueError(f"{upload.name} is not a valid image")
        upload.seek(0)
        photo = Photo(batch=batch, original_filename=Path(upload.name).name, file_size=upload.size)
        photo.image.save(Path(upload.name).name, upload, save=False)
        preview = image.copy()
        preview.thumbnail((720, 720))
        if batch.frame:
            overlay = Image.open(batch.frame).convert("RGBA").resize(preview.size, Image.Resampling.LANCZOS)
            preview = Image.alpha_composite(preview.convert("RGBA"), overlay).convert("RGB")
        if preview.mode not in ("RGB", "L"):
            preview = preview.convert("RGB")
        out = io.BytesIO()
        preview.save(out, format="JPEG", quality=82, optimize=True)
        photo.preview.save(f"{photo.image.name.split('/')[-1]}.jpg", ContentFile(out.getvalue()), save=False)
        if batch.frame:
            overlay = Image.open(batch.frame).convert("RGBA").resize(image.size, Image.Resampling.LANCZOS)
            framed = Image.alpha_composite(image.convert("RGBA"), overlay)
            framed_bytes = io.BytesIO()
            framed.save(framed_bytes, format="PNG", optimize=True)
            photo.framed.save(f"{Path(upload.name).stem}-framed.png", ContentFile(framed_bytes.getvalue()), save=False)
        photo.save()
        saved.append(photo)
    return saved

@api_view(["GET", "POST"])
@parser_classes([MultiPartParser, FormParser])
def batches(request):
    if request.method == "GET":
        for expired in Batch.objects.filter(active=True, expires_at__lte=timezone.now()).iterator():
            expired.delete()
        rows = Batch.objects.filter(active=True).order_by("-created_at")
        return Response(BatchSerializer(rows, many=True, context={"request": request}).data)
    files = request.FILES.getlist("photos")
    if not files:
        return Response({"detail": "Choose at least one photo."}, status=400)
    try:
        title = request.data.get("title", "Event photos")[:120]
        minutes = max(1, min(int(request.data.get("expiry_minutes", 30)), 1440))
        batch = Batch.objects.create(title=title or "Event photos", expires_at=timezone.now() + timedelta(minutes=minutes))
        frame = request.FILES.get("frame")
        if frame:
            if frame.size > MAX_UPLOAD:
                raise ValueError("Frame file must be 25 MB or smaller")
            frame.seek(0)
            try:
                frame_image = Image.open(frame)
                frame_image.load()
            except OSError:
                raise ValueError("The frame file is not a valid PNG")
            if frame_image.format != "PNG" or frame_image.mode not in ("RGBA", "LA", "P"):
                raise ValueError("Use a transparent PNG frame")
            if frame_image.convert("RGBA").getchannel("A").getextrema()[0] != 0:
                raise ValueError("The PNG frame needs transparent areas so the photo shows through")
            frame.seek(0)
            batch.frame.save(Path(frame.name).name, frame, save=True)
        save_photos(batch, files)
    except (ValueError, TypeError) as exc:
        if "batch" in locals(): batch.delete()
        return Response({"detail": str(exc)}, status=400)
    return Response(BatchSerializer(batch, context={"request": request}).data, status=status.HTTP_201_CREATED)

@api_view(["GET", "DELETE"])
def batch_detail(request, batch_id):
    batch = get_object_or_404(Batch, pk=batch_id)
    if request.method == "DELETE":
        batch.delete()
        return Response(status=204)
    if not batch.is_available:
        batch.delete()
        return Response({"detail": "This gallery has expired or was closed."}, status=410)
    return Response(BatchSerializer(batch, context={"request": request}).data)

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def close_batch(request, batch_id):
    batch = get_object_or_404(Batch, pk=batch_id)
    batch.delete()
    return Response(status=204)

@api_view(["GET"])
def download_photo(request, photo_id):
    photo = get_object_or_404(Photo.objects.select_related("batch"), pk=photo_id)
    if not photo.batch.is_available:
        photo.batch.delete()
        raise Http404("Gallery expired")
    photo.downloads += 1
    photo.save(update_fields=["downloads"])
    response = FileResponse(photo.image.open("rb"), content_type="application/octet-stream")
    response["Content-Disposition"] = f'attachment; filename="{Path(photo.original_filename).name}"'
    return response

@api_view(["GET"])
def preview_photo(request, photo_id):
    photo = get_object_or_404(Photo.objects.select_related("batch"), pk=photo_id)
    if not photo.batch.is_available:
        photo.batch.delete()
        raise Http404("Gallery expired")
    return FileResponse(photo.preview.open("rb"), content_type="image/jpeg")

@api_view(["GET"])
def framed_photo(request, photo_id):
    photo = get_object_or_404(Photo.objects.select_related("batch"), pk=photo_id)
    if not photo.batch.is_available:
        photo.batch.delete()
        raise Http404("Gallery expired")
    if not photo.framed:
        raise Http404("No frame was applied")
    response = FileResponse(photo.framed.open("rb"), content_type="image/png")
    response["Content-Disposition"] = f'attachment; filename="{Path(photo.original_filename).stem}-framed.png"'
    return response

@api_view(["GET"])
def network_info(request):
    ip = lan_ip()
    return Response({"ip": ip, "api_url": f"http://{ip}:8000", "note": "Guests must be on a network that allows access to this laptop."})
