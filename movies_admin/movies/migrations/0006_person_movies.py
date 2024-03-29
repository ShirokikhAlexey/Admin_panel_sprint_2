# Generated by Django 3.1 on 2020-11-15 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0005_auto_20201115_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='movies',
            field=models.ManyToManyField(related_name='films', through='movies.PersonFilmWork', to='movies.FilmWork'),
        ),
    ]
