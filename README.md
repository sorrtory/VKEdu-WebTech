# Tp-tasks

Технопарк Mail.Ru / 1-ый семестр / Web-технологии

## Source

<https://github.com/ziontab/tp-tasks>

## **[ HEADS UP. OUTDATED RN]** Check this out [sorrtory.ru](sorrtory.ru)

```sh
cd prod
docker compose --env-file ../.env up --build -d
```

Or you can try to build it on your own [(reference)](https://github.com/testdrivenio/django-on-docker/)

1. Clone the code

    ```bash
    git clone https://github.com/sorrtory/VKEdu-WebTech
    ```

2. Set up a virtual enviroment

    ```bash
    cd VKEdu-WebTech && python3 -m venv .venv && source .venv/bin/activate
    ```

3. Create `.env` file like

    ```sh
    POSTGRES_DB=db
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    DATABASE_HOST=db
    POSTGRES_PORT=5432

    DEBUG=True
    DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
    ```

4. Install the requirements

    ```bash
    pip install -r requirements.txt
    ```

5. Set up the database

    ```sh
    docker compose -f prod/docker-compose.yml up -d --build db  # Launch the database
    python askme_fedukov/manage.py remigrate   # Recreate tables (drop+make)
    python askme_fedukov/manage.py fill_db 50  # Add mock data with <ratio>
    ```

6. Launch the server

    ```bash
    python askme_fedukov/manage.py runserver
    ```

7. Open the [localhost](http://127.0.0.1:8000/)

## Status

### 1. Layout

[Reference](https://github.com/ziontab/tp-tasks/blob/master/files/markdown/task-1.md#6-%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80%D0%BD%D1%8B%D0%B9-%D0%B2%D0%BD%D0%B5%D1%88%D0%BD%D0%B8%D0%B9-%D0%B2%D0%B8%D0%B4-%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86)

### 2. Routing

Some examples of implemented resources:

| Page                              | URL                                    | Meaning                                    |
|-----------------------------------|----------------------------------------|--------------------------------------------|
| Index page                        | <http://127.0.0.1:8000/>               | список новых вопросов (главная страница)   |
| Hot questions page                | <http://127.0.0.1:8000/hot/>           | список “лучших” вопросов                   |
| Tag page                          | <http://127.0.0.1:8000/tag/blablabla/> | список вопросов по тэгу                    |
| Question page                     | <http://127.0.0.1:8000/question/5/>    | страница одного вопроса со списком ответов |
| Ask page                          | <http://127.0.0.1:8000/ask/>           | форма создания вопроса                     |
| Login page                        | <http://127.0.0.1:8000/login/>         | форм логина                                |
| Register page                     | <http://127.0.0.1:8000/signup/>        | форма регистрации                          |
| Settings page                     | <http://127.0.0.1:8000/settings/>      | настройки                                  |
| Profile page                      | <http://127.0.0.1:8000/profile/0/>     | публичная страница пользователя            |

### 3. Database

[Fill it](askme_fedukov/app/management/commands/fill_db.py) with test data using

```sh
# Before filling, you're likely to migrate with 
# python manage.py remigrate
# That'll DROP ALL public tables -> makemigrations -> migrate

python manage.py fill_db [ratio]

# To remove all data use django's flush
python manage.py flush
```

Where `[ratio]` is the fill factor for entities. After executing the command, the database should be populated with the following:

- Users: `ratio`
- Questions: `ratio * 10`
- Answers: `ratio * 100`
- Tags: `ratio`
- Likes: `ratio * 200`

### 4. Forms

Djano's [forms](askme_fedukov/app/forms.py) with my [form checker](/askme_fedukov/app/utils/form_checker.py)

- Login
- Register
- Profile settings
- New question
- New answer

### 5. Ajax

> Django REST Framework is nice but I realised it too late.

- Likes. User can like Answers and Questions but not his own ones.
- Correct. User can mark Answers to his own Questions.

Unauthorized user can't see this features, actually

### 6. WSGI

...

### 7. Extras

...

## Conclusion

### Outline

Django is really powerful when you need to create the app very fast.
It has a lot of in-built options almost for any case.

But is scales like shit. I was lost trying to organize it properly.

So, to sum up, if you need something simple the formula is `bootsrap+django+djangoREST`. \
Otherwise you **don't need** to chose this framework.

### Takes

#### This project

- Customizing Django is reinventing the wheel
- Customizing Bootsrap is a waste of time
- Creating class layer for frontend is overengineering (only in Django?)
- Creating dynamic layout with jinga is difficult
- Axios=isEven (although can be used in node.js and for progress bars)

#### General web dev

- Creating several types for one logic (AnswerLike, QuestionLike) is pointless
- Golang's "err"-check thing is a brilliant. Never skip this thing in other langs
- Format code as you write/generate it (so formatter won't fuck jinja's embeds)
