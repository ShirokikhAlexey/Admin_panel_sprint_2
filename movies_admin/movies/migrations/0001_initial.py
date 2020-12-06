# Generated by Django 3.1 on 2020-11-14 21:31

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FilmWork',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255, verbose_name='название')),
                ('description', models.TextField(blank=True, verbose_name='описание')),
                ('creation_date', models.DateField(blank=True, verbose_name='дата создания фильма')),
                ('certificate', models.TextField(blank=True, verbose_name='сертификат')),
                ('file_path', models.FileField(blank=True, upload_to='film_works/', verbose_name='файл')),
                ('rating', models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='рейтинг')),
                ('type', models.CharField(choices=[('movie', 'фильм'), ('tv_show', 'шоу')], max_length=20, verbose_name='тип')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'кинопроизведение',
                'verbose_name_plural': 'кинопроизведения',
                'db_table': '"content"."film_work"',
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='название')),
                ('description', models.TextField(blank=True, verbose_name='описание')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'жанр',
                'verbose_name_plural': 'жанры',
                'db_table': '"content"."genre"',
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=255, verbose_name='полное имя')),
                ('birth_date', models.DateField(blank=True, verbose_name='дата рождения')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'персона',
                'verbose_name_plural': 'персоны',
                'db_table': '"content"."person"',
            },
        ),
        migrations.CreateModel(
            name='PersonFilmWork',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(max_length=255, verbose_name='профессия')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('film_work_id', models.ForeignKey(db_column='film_work_id', on_delete=django.db.models.deletion.CASCADE, to='movies.filmwork')),
                ('person_id', models.ForeignKey(db_column='person_id', on_delete=django.db.models.deletion.CASCADE, to='movies.person')),
            ],
            options={
                'verbose_name': 'персона-фильм',
                'verbose_name_plural': 'персоны-фильмы',
                'db_table': '"content"."person_film_work"',
                'unique_together': {('film_work_id', 'person_id', 'role')},
                'index_together': {('film_work_id', 'person_id', 'role')},
            },
        ),
        migrations.CreateModel(
            name='GenreFilmWork',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('film_work_id', models.ForeignKey(db_column='film_work_id', on_delete=django.db.models.deletion.CASCADE, to='movies.filmwork')),
                ('genre_id', models.ForeignKey(db_column='genre_id', on_delete=django.db.models.deletion.CASCADE, to='movies.genre')),
            ],
            options={
                'verbose_name': 'жанр-фильм',
                'verbose_name_plural': 'жанры-фильмы',
                'db_table': '"content"."genre_film_work"',
                'unique_together': {('film_work_id', 'genre_id')},
                'index_together': {('film_work_id', 'genre_id')},
            },
        ),
    ]