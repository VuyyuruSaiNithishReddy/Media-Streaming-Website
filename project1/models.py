from django.db import models


# Create your models here.
class Movie(models.Model):
    name = models.CharField(max_length=50)
    location = models.FileField()
    cover_pic = models.FileField(upload_to='coverpics/')
    desc = models.TextField()

class Document(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='UserUploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)