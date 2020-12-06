import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class GenreFilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work_id = models.ForeignKey('FilmWork', on_delete=models.CASCADE, db_column='film_work_id')
    genre_id = models.ForeignKey('Genre', on_delete=models.CASCADE, db_column='genre_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = [
            ("film_work_id", "genre_id"),
        ]
        unique_together = ('film_work_id', 'genre_id',)
        verbose_name = _('жанр-фильм')
        verbose_name_plural = _('жанры-фильмы')
        db_table = u'"content\".\"genre_film_work"'


class PersonFilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work_id = models.ForeignKey('FilmWork', on_delete=models.CASCADE, db_column='film_work_id')
    person_id = models.ForeignKey('Person', on_delete=models.CASCADE, db_column='person_id')
    role = models.CharField(_('профессия'), max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = [
            ("film_work_id", "person_id", 'role'),
        ]
        unique_together = ('film_work_id', 'person_id', 'role')
        verbose_name = _('персона-фильм')
        verbose_name_plural = _('персоны-фильмы')
        db_table = u'"content\".\"person_film_work"'


class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('название'), max_length=255, unique=True)
    description = models.TextField(_('описание'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')
        db_table = u'"content\".\"genre"'

    def __str__(self):
        return self.name


class FilmworkType(models.TextChoices):
    MOVIE = 'movie', _('фильм')
    TV_SHOW = 'tv_show', _('шоу')


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(_('полное имя'), max_length=255)
    birth_date = models.DateField(_('дата рождения'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    movies = models.ManyToManyField("FilmWork", related_name='films', through='PersonFilmWork',
                                    through_fields=('person_id', 'film_work_id'))

    class Meta:
        verbose_name = _('персона')
        verbose_name_plural = _('персоны')
        db_table = u'"content\".\"person"'

    def __str__(self):
        return self.full_name


class FilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'))
    creation_date = models.DateField(_('дата создания фильма'))
    certificate = models.TextField(_('сертификат'))
    file_path = models.FileField(_('файл'), upload_to='film_works/')
    rating = models.FloatField(_('рейтинг'), validators=[MinValueValidator(0)])
    type = models.CharField(_('тип'), max_length=20, choices=FilmworkType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    genre = models.ManyToManyField(Genre, related_name='genres', through='GenreFilmWork',
                                   through_fields=('film_work_id', 'genre_id'))
    people = models.ManyToManyField(Person, related_name='people', through='PersonFilmWork',
                                    through_fields=('film_work_id', 'person_id'))

    class Meta:
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')
        db_table = u'"content\".\"film_work"'

    def __str__(self):
        return self.title


class PersonRole(models.TextChoices):
    ACTOR = 'actor', _('актер')
    DIRECTOR = 'director', _('режиссер')
    WRITER = 'writer', _('сценарист')


class ActorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(personfilmwork__role='actor').distinct()


class DirectorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(personfilmwork__role='director').distinct()


class WriterManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(personfilmwork__role='writer').distinct()


class MovieManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type='movie')


class TvShowManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type='tv_show')


class Actor(Person):
    class Meta:
        verbose_name = _('актер')
        verbose_name_plural = _('актеры')
        proxy = True

    objects = ActorManager()


class Director(Person):
    class Meta:
        verbose_name = _('режиссер')
        verbose_name_plural = _('режиссеры')
        proxy = True

    objects = DirectorManager()


class Writer(Person):
    class Meta:
        verbose_name = _('сценарист')
        verbose_name_plural = _('сценаристы')
        proxy = True

    objects = WriterManager()


class Movie(FilmWork):
    class Meta:
        verbose_name = _('фильм')
        verbose_name_plural = _('фильмы')
        proxy = True

    objects = MovieManager()


class TvShow(FilmWork):
    class Meta:
        verbose_name = _('телешоу')
        verbose_name_plural = _('телешоу')
        proxy = True

    objects = TvShowManager()
