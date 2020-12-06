CREATE ROLE postgre SUPERUSER LOGIN PASSWORD '1234';

CREATE DATABASE movies_database WITH ENCODING = 'UTF8' OWNER = postgre;
 \connect movies_database;

-- Создаем отдельную схему для нашего контента, чтобы не перемешалось с сущностями Django
CREATE SCHEMA IF NOT EXISTS content;

CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = current_timestamp;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Жанры, которые могут быть у кинопроизведений
CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at timestamp with time zone default current_timestamp,
    updated_at timestamp with time zone default null
);

CREATE TRIGGER set_timestamp_genre
BEFORE UPDATE ON content.genre
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- Убраны актеры, жанры, режиссеры и сценаристы, так как они находятся в отношении m2m с этой таблицей
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    certificate TEXT,
    file_path TEXT,
    rating FLOAT,
    type TEXT not null,
    created_at timestamp with time zone default current_timestamp,
    updated_at timestamp with time zone
);

CREATE TRIGGER set_timestamp_film_work
BEFORE UPDATE ON content.film_work
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- Обобщение для актера, режиссера и сценариста
CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    birth_date DATE,
    created_at timestamp with time zone default current_timestamp,
    updated_at timestamp with time zone
);

CREATE TRIGGER set_timestamp_person
BEFORE UPDATE ON content.film_work
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- m2m таблица для связывания кинопроизведений с жанрами
CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    genre_id uuid NOT NULL,
    created_at timestamp with time zone default current_timestamp
);

-- Обязательно проверяется уникальность жанра и кинопроизведения, чтобы не появлялось дублей
CREATE UNIQUE INDEX film_work_genre ON content.genre_film_work (film_work_id, genre_id);

-- m2m таблица для связывания кинопроизведений с участниками
CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role TEXT NOT NULL,
    created_at timestamp with time zone default current_timestamp
);

-- Обязательно проверяется уникальность кинопроизведения, человека и роли человека, чтобы не появлялось дублей
-- Один человек может быть сразу в нескольких ролях (например, сценарист и режиссер)
CREATE UNIQUE INDEX film_work_person_role ON content.person_film_work (film_work_id, person_id, role);

