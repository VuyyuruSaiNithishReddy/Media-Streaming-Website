# Generated by Django 3.0.5 on 2020-07-10 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project1', '0002_remove_movie_cover_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='cover_pic',
            field=models.FileField(default=0, upload_to='coverpics/'),
            preserve_default=False,
        ),
    ]
