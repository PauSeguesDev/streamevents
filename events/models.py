from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from io import BytesIO
import os
import re

try:
    from PIL import Image
except ImportError:
    Image = None

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('gaming', 'Gaming'),
        ('music', 'Música'),
        ('talk', 'Xerrades'),
        ('education', 'Educació'),
        ('sports', 'Esports'),
        ('entertainment', 'Entreteniment'),
        ('technology', 'Tecnologia'),
        ('art', 'Art i Creativitat'),
        ('other', 'Altres')
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Programat'),
        ('live', 'En Directe'),
        ('finished', 'Finalitzat'),
        ('cancelled', 'Cancel·lat')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    thumbnail = models.ImageField(upload_to='events/thumbnails/', blank=True, null=True)
    max_viewers = models.PositiveIntegerField(default=100)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=500, blank=True)
    stream_url = models.URLField(max_length=500, blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    duration = models.DurationField(null=True, blank=True)

    class Meta:
        verbose_name = 'Esdeveniment'
        verbose_name_plural = 'Esdeveniments'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('events:event_detail', kwargs={'pk': self.pk})

    def update_status(self):
        """
        Updates the status based on the scheduled date and current time.
        Scheduled -> Live (if time passed)
        """
        now = timezone.now()
        if self.status == 'scheduled' and self.scheduled_date <= now:
            self.status = 'live'
            self.save(update_fields=['status'])
            return True
        return False

    @property
    def is_live(self):
        return self.status == 'live'

    @property
    def is_finished(self):
        return self.status == 'finished'

    def get_stream_embed_url(self):
        """
        Returns the embed URL for YouTube or Twitch based on stream_url.
        """
        if not self.stream_url:
            return None
        
        youtube_regex = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        match = re.search(youtube_regex, self.stream_url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}"
        twitch_regex = r'(?:https?:\/\/)?(?:www\.)?twitch\.tv\/([a-zA-Z0-9_]+)'
        match = re.search(twitch_regex, self.stream_url)
        if match:
            channel_name = match.group(1)
            return f"https://player.twitch.tv/?channel={channel_name}&parent=localhost&parent=127.0.0.1"

        return self.stream_url

    def get_tags_list(self):
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def save(self, *args, **kwargs):
        if not self.thumbnail:
            pass

        if self.thumbnail and Image:
            super().save(*args, **kwargs)
            try:
                img = Image.open(self.thumbnail.path)
                if img.height > 720 or img.width > 1280:
                    output_size = (1280, 720)
                    img.thumbnail(output_size)
                    img.save(self.thumbnail.path, quality=85, optimize=True)
            except Exception as e:
                pass
        else:
            super().save(*args, **kwargs)
