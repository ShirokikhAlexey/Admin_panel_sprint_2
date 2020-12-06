from django.contrib import admin
from .models import Genre, Actor, Director, Writer, Movie, TvShow


class ActorInline(admin.TabularInline):
    model = Actor.movies.through
    verbose_name = "Фильм"
    verbose_name_plural = "Фильмы"

    def get_queryset(self, request):
        return self.model.objects.get_queryset().filter(role='actor')


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date',)

    fields = (
        'full_name', 'birth_date',
    )

    inlines = [ActorInline]


class DirectorInline(admin.TabularInline):
    model = Director.movies.through
    verbose_name = "Фильм"
    verbose_name_plural = "Фильмы"

    def get_queryset(self, request):
        return self.model.objects.get_queryset().filter(role='director')


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date',)

    fields = (
        'full_name', 'birth_date',
    )

    inlines = [DirectorInline]


class WriterInline(admin.TabularInline):
    model = Writer.movies.through
    verbose_name = "Фильм"
    verbose_name_plural = "Фильмы"

    def get_queryset(self, request):
        return self.model.objects.get_queryset().filter(role='writer')


@admin.register(Writer)
class WriterAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date',)

    fields = (
        'full_name', 'birth_date',
    )

    inlines = [WriterInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

    fields = (
        'name', 'description'
    )


class MovieActorsInline(admin.TabularInline):
    model = Movie.people.through
    verbose_name = "Актер"
    verbose_name_plural = "Актеры"

    def get_queryset(self, request):
        return self.model.objects.get_queryset().filter(role='actor')


class MovieDirectorInline(admin.TabularInline):
    model = Movie.people.through
    verbose_name = "Режиссер"
    verbose_name_plural = "Режиссеры"

    def get_queryset(self, request):
        return self.model.objects.get_queryset().filter(role='director')


class MovieWriterInline(admin.TabularInline):
    model = Movie.people.through
    verbose_name = "Сценарист"
    verbose_name_plural = "Сценаристы"

    def get_queryset(self, request):
        return self.model.objects.get_queryset().filter(role='writer')


class MovieGenreInline(admin.TabularInline):
    model = Movie.genre.through
    verbose_name = "Жанр"
    verbose_name_plural = "Жанры"


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'creation_date', 'certificate', 'file_path', 'rating')

    fields = (
        'title', 'description', 'creation_date', 'certificate', 'file_path', 'rating'
    )

    inlines = [MovieGenreInline ,MovieActorsInline, MovieDirectorInline, MovieWriterInline]


class TvShowActorsInline(admin.TabularInline):
    model = TvShow.people.through
    verbose_name = "Актер"
    verbose_name_plural = "Актеры"

    def get_queryset(self, request):
        return self.model.objects.get_queryset().filter(role='actor')


class TvShowDirectorInline(admin.TabularInline):
    model = TvShow.people.through
    verbose_name = "Режиссер"
    verbose_name_plural = "Режиссеры"

    def get_queryset(self, request):
        return self.model.objects.get_queryset().filter(role='director')


class TvShowWriterInline(admin.TabularInline):
    model = TvShow.people.through
    verbose_name = "Сценарист"
    verbose_name_plural = "Сценаристы"

    def get_queryset(self, request):
        return self.model.objects.get_queryset().filter(role='writer')


class TvShowGenreInline(admin.TabularInline):
    model = TvShow.genre.through
    verbose_name = "Жанр"
    verbose_name_plural = "Жанры"


@admin.register(TvShow)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'creation_date', 'certificate', 'file_path', 'rating')

    fields = (
        'title', 'description', 'creation_date', 'certificate', 'file_path', 'rating'
    )

    inlines = [TvShowGenreInline, TvShowActorsInline, TvShowDirectorInline, TvShowWriterInline]
