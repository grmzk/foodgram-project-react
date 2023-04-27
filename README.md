![Workflow Result](https://github.com/grmzk/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# Foodgram (docker-container)
Docker-контейнер для развертывания проекта Foodgram (ресурс для публикации 
кулинарных рецептов)

##### Технологии
- Python 3.10
- Django 4.1
- Django REST Framework 3.14.0
- Docker
- PostgreSQL 13.0
- Nginx 1.21.3

##### Как запустить проект:

Клонировать репозиторий и перейти в директорию `infra` в командной строке:

```
git clone git@github.com:grmzk/foodgram-project-react.git
```

```
cd foodgram-project-react/infra/
```

Для работы с другой СУБД отредактировать `.env`

```
DB_ENGINE=django.db.backends.postgresql # СУБД 
DB_NAME=postgres                        # название БД
POSTGRES_USER=postgres                  # имя пользователя БД
POSTGRES_PASSWORD=postgres              # пароль пользователя БД
DB_HOST=db                              # адрес хоста с БД
DB_PORT=5432                            # порт для подключения к БД
```

Собрать контейнер и запустить YaMDb:

```
docker-compose up -d
```


Выполнить поочереди (только после первой сборки):

```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```

##### Эндпоинты

Получить список всех рецептов:
```
GET /api/recipes/
```

Получить конкретный рецепт по id:
```
GET /api/recipes/{id}/
```

Регистрация нового пользователя:
```
JSON в теле запроса
{
"email": "string",
"username": "string",
"first_name": "string",
"last_name": "string",
"password": "string"
}

POST /api/users/
```

[Полный список эндпоинтов](http://62.84.120.127/api/docs/)

##### Авторы
- Игорь Музыка [mailto:igor@mail.fake]
- Yandex LLC