import os
import sqlite3
import uuid
from datetime import date
from dataclasses import dataclass
from typing import List

import psycopg2
from psycopg2.extras import execute_values
from psycopg2.extensions import connection as _connection
from psycopg2.extras import LoggingConnection
from dotenv import load_dotenv


psycopg2.extras.register_uuid()
load_dotenv()


# Класс для формирования объектов фильмов для дальнейшей записи в таблицу film_work
@dataclass()
class Movie:
    id: uuid
    title: str
    type: str
    description: str = None
    rating: float = None
    creation_date: date = None
    certificate: str = None
    file_path: str = None


# Класс для формирования объектов жанров для дальнейшей записи в таблицу genre
@dataclass()
class Genre:
    id: uuid
    name: str
    description: str = None


# Класс для формирования объектов персон для дальнейшей записи в таблицу person
@dataclass()
class Person:
    id: uuid
    full_name: str
    birth_date: date = None


# Класс для формирования объектов связи фильм-жанр для дальнейшей записи в таблицу genre_film_work
@dataclass()
class GenreFilm:
    id: uuid
    film_id: uuid
    genre_id: uuid


# Класс для формирования объектов связи фильм-персона для дальнейшей записи в таблицу person_film_work
@dataclass()
class PersonFilm:
    id: uuid
    film_id: uuid
    person_id: uuid
    role: str


uploaded_people = {}
uploaded_genres = {}


class PostgresSaver:
    """
    Класс для записи данных в базу postgresql
    """

    def __init__(self, pg_cursor, sqlite_cursor):
        self.pg_cursor = pg_cursor
        self.sqlite_cursor = sqlite_cursor

    def load_objects(self, values):
        """
        Загрузка данных в таблицы film_works, genre, people, genre_film_work, person_film_work
        :param values: словарь с ключами film_works, genres, people, genre_film_works, person_film_works.
        Значения словаря - списки объектов классов Movie, Genre, Person, GenreFilm, PersonFilm
        :return:
        """

        if values['film_works']:
            data = [(film.id, film.title, film.type, film.description, film.rating)
                    for film in values['film_works']]
            insert_query = 'insert into content.film_work (id, title, type, description, rating) values %s'
            execute_values(self.pg_cursor, insert_query, data, template=None)

        if values['genres']:
            data = [(genre.id, genre.name)
                    for genre in values['genres']]
            insert_query = 'insert into content.genre (id, name) values %s'
            execute_values(self.pg_cursor, insert_query, data, template=None)
            uploaded_genres.update({genre.name: genre for genre in values['genres']})

        if values['people']:
            data = [(person.id, person.full_name)
                    for person in values['people']]
            insert_query = 'insert into content.person (id, full_name) values %s'
            execute_values(self.pg_cursor, insert_query, data, template=None)
            uploaded_people.update({person.full_name: person for person in values['people']})

        if values['genre_film_works']:
            data = [(genre_film.id, genre_film.film_id, genre_film.genre_id)
                    for genre_film in values['genre_film_works']]
            insert_query = '''
                insert into content.genre_film_work (id, film_work_id, genre_id) 
                values %s
                on conflict (film_work_id, genre_id) do nothing
                '''
            execute_values(self.pg_cursor, insert_query, data, template=None)

        if values['person_film_works']:
            data = [(person_film.id, person_film.film_id, person_film.person_id, person_film.role)
                    for person_film in values['person_film_works']]
            insert_query = '''
                insert into content.person_film_work (id, film_work_id, person_id, role) 
                values %s
                on conflict (film_work_id, person_id, role) do nothing
                '''
            execute_values(self.pg_cursor, insert_query, data, template=None)

    def check_left_people(self, table: str):
        """
        Проверка, что перенесены все персоны из таблиц actors, writers. Вызывыется после переноса всех фильмов.
        При нахождении неперенесенных персон, добавляет их в таблицу person
        :param table: по какой таблице делать поиск - writers или actors
        :return:
        """
        self.pg_cursor.execute('select p.full_name from content.person p')
        rows = self.pg_cursor.fetchall()
        added = ['"{}"'.format(row[0]) for row in rows]

        self.sqlite_cursor.execute('select a.name from {} a where a.name not in ({})'.format(table, ','.join(added)))
        not_created_people = self.sqlite_cursor.fetchall()
        if not_created_people:
            people = [(uuid.uuid4(), row[0]) for row in not_created_people]
            insert_query = 'insert into content.person (id, full_name) values %s'
            execute_values(self.pg_cursor, insert_query, people, template=None)


class SQLiteLoader:
    """
    Класс для получения данных из базы db.sqlite
    """
    def __init__(self, pg_cursor, sqlite_cursor):
        self.pg_cursor = pg_cursor
        self.sqlite_cursor = sqlite_cursor

    def get_movies_full_info(self, limit: int, offset: int):
        """
        Получение данных о фильмах из базы db.sqlite
        :param limit: число выводимых строк из таблицы
        :param offset: с какой строки выводить
        :return: список словарей для каждого полученного фильма со значениями:
        id: str - id фильма в таблице movies
        genres: list - жанры фильма
        director: str - режиссер
        title: str - название фильма
        description: str - описание
        rating: str - рейтинг фильма
        actors: list - список актеров
        writers: list - список сценаристов
        """
        sql = '''
            WITH x as (
            SELECT m.id, group_concat(a.name) as actors_names
            FROM movies m
                     LEFT JOIN movie_actors ma on m.id = ma.movie_id
                     LEFT JOIN actors a on ma.actor_id = a.id
            GROUP BY m.id
        ),
    y as (
            SELECT m.id, group_concat(w.name) as writers_names
            FROM movies m
            left join writers w on 
            case WHEN m.writer != '' and m.writer not null THEN m.writer = w.id else m.writers like '%"'||w.id||'"%' end
            GROUP BY m.id
        )
        SELECT m.id, genre, director, title, plot, imdb_rating, x.actors_names, y.writers_names
        FROM movies m
        LEFT JOIN x ON m.id = x.id
        left join y on m.id = y.id
        limit {} OFFSET {};
            '''
        movies_list = []
        self.sqlite_cursor.execute(sql.format(limit, offset))
        rows = self.sqlite_cursor.fetchall()
        for row in rows:
            if row[4] == 'N/A':
                desc = None
            else:
                desc = row[4]
            movie_dict = {
                'id': row[0],
                'genres': [genre.strip() for genre in row[1].split(',')],
                'director': row[2],
                'title': row[3],
                'description': desc,
                'rating': row[5],
                'actors': [actor.strip() for actor in row[6].split(',')],
                'writers': [writer.strip() for writer in row[7].split(',')]
            }
            movies_list.append(movie_dict)
        return movies_list

    def create_objects(self, movies_list_objects: List[dict]):
        """
        Преобразует список словарей из get_movies_full_info в объекты для загрузки
        :param movies_list_objects: список словарей для фильмов со значениями:
                                    id: str - id фильма в таблице movies
                                    genres: list - жанры фильма
                                    director: str - режиссер
                                    title: str - название фильма
                                    description: str - описание
                                    rating: str - рейтинг фильма
                                    actors: list - список актеров
                                    writers: list - список сценаристов
        :return: словарь списков объектов для загрузки в соответсвующие таблицы:
            film_works: list - список объектов Movie для записи в film_work
            genres: list - список объектов Genre для записи в genre
            people: list - список объектов Person для записи в people
            genre_film_works: list - список объектов GenreFilm для записи в genre_film_work
            person_film_works: list - список объектов PersonFilm для записи в person_film_work
        """
        film_works = []
        pack_genres = {}
        pack_people = {}
        genre_film_works = []
        person_film_works = []
        for movie in movies_list_objects:
            try:
                rating = float(movie['rating'])
            except:
                rating = None

            new_movie = Movie(
                id=uuid.uuid4(),
                title=movie['title'],
                type='movie',
                description=movie['description'],
                rating=rating
            )
            film_works.append(new_movie)

            pack_genres, new_genre_film_works = self.create_genres(movie['genres'], new_movie.id, pack_genres)
            genre_film_works.extend(new_genre_film_works)

            person_role = {
                'director': [movie['director']],
                'actor': movie['actors'],
                'writer': movie['writers']
            }

            for role in person_role.keys():
                pack_people, new_people_fw = self.create_people(person_role[role], role, new_movie.id, pack_people)
                person_film_works.extend(new_people_fw)

        return {
            'film_works': film_works,
            'genres': list(pack_genres.values()),
            'people': list(pack_people.values()),
            'genre_film_works': genre_film_works,
            'person_film_works': person_film_works
        }

    def create_genres(self, genres, movie_id, pack_genres):
        """
        Создание объектов Genre и GenreFilm
        :param genres: список жанров
        :param movie_id: id фильма в новой таблице
        :param pack_genres: словарь жанров вида {название жанра: объект Genre}, содержащий жанры, которые будут
        загружены
        :return: измененный pack_genres с новыми жанрами и список GenreFilm для данного фильма
        """
        create_genre_film_work = []

        for genre in genres:
            if genre == 'N/A':
                continue

            existing_genre = self.check_genre(genre)
            if existing_genre:
                current_genre = existing_genre
            elif genre in pack_genres.keys():
                current_genre = pack_genres[genre]
            else:
                current_genre = Genre(id=uuid.uuid4(), name=genre)
                pack_genres[genre] = current_genre

            new_genre_film_work = GenreFilm(id=uuid.uuid4(), film_id=movie_id, genre_id=current_genre.id)
            create_genre_film_work.append(new_genre_film_work)

        return pack_genres, create_genre_film_work

    def create_people(self, people, role, movie_id, pack_people):
        """
        Создание объектов Person и PersonFilm для различных ролей
        :param people: список персон
        :param role: роль в фильме (director, actor, writer)
        :param movie_id: id фильма в новой таблице
        :param pack_people: словарь персон вида {имя: объект Person}, содержащий персон, которые будут
        загружены
        :return: измененный pack_people с новыми персонами и список объектов PersonFilm для данного фильма
        """

        create_person_film_work = []

        for person in people:
            if person == 'N/A':
                continue
            existing_person = self.check_person(person)
            if existing_person:
                current_person = existing_person
            elif person in pack_people.keys():
                current_person = pack_people[person]
            else:
                current_person = Person(id=uuid.uuid4(), full_name=person)
                pack_people[person] = current_person

            new_person_film_works = PersonFilm(
                id=uuid.uuid4(),
                film_id=movie_id,
                person_id=current_person.id,
                role=role
            )
            create_person_film_work.append(new_person_film_works)

        return pack_people, create_person_film_work

    def check_genre(self, genre_name: str):
        """
        Проверка, был ли данный жанр загружен в базу
        :param genre_name: название жанра
        :return: False, если жанр не был перенесен, объект Genre - если был перенесен
        """
        row = uploaded_genres.get(genre_name)
        if row:
            return row
        return False

    def check_person(self, person_name: str):
        """
        Проверка, был ли перенесен в базу данный человек
        :param person_name: полное имя
        :return: False, если человек не был перенесен, объект Person - если был перенесен
        """
        row = uploaded_people.get(person_name)
        if row:
            return row
        return False


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgres_saver = PostgresSaver(pg_conn.cursor(), connection.cursor())
    sqlite_loader = SQLiteLoader(pg_conn.cursor(), connection.cursor())

    count = connection.cursor().execute('select count(*) from movies')
    num_rows = count.fetchall()[0][0]
    package_size = int(os.getenv('PACKAGE_SIZE'))

    for i in range(int(num_rows) // package_size + 1):
        movies_list_prep = sqlite_loader.get_movies_full_info(10, 10 * i)
        data = sqlite_loader.create_objects(movies_list_prep)
        postgres_saver.load_objects(data)

    postgres_saver.check_left_people('actors')
    postgres_saver.check_left_people('writers')


if __name__ == '__main__':
    dsl = {
        'dbname': os.getenv('DBNAME'),
        'user': os.getenv('USER'),
        'password': os.getenv('PASSWORD'),
        'host': os.getenv('HOST'),
        'port': os.getenv('PORT')
    }
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "db.sqlite")
    with sqlite3.connect(db_path) as sqlite_conn, \
            psycopg2.connect(**dsl, connection_factory=LoggingConnection) as conn_psql, \
            open('upload.log', 'w') as upload_log, open('load.log', 'w') as load_log:
        conn_psql.initialize(upload_log)
        sqlite_conn.set_trace_callback(load_log.write)
        load_from_sqlite(sqlite_conn, conn_psql)
