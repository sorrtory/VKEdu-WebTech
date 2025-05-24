# Tp-tasks

Технопарк Mail.Ru / 1-ый семестр / Web-технологии

## Source

<https://github.com/ziontab/tp-tasks>

## **[ HEADS UP. OUTDATED RN]** Check this out [sorrtory.ru](sorrtory.ru)

Or you can try to build it on your own

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
    DATABASE_NAME=db
    DATABASE_USERNAME=user
    DATABASE_PASSWORD=password
    DATABASE_HOST=db
    DATABASE_PORT=5432

    DEBUG=True
    DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
    ```

4. Install the requirements

    ```bash
    pip install -r requirements.txt
    ```

5. Start the db

    ```sh
    docker compose up -d --build 'db'
    python askme_fedukov/manage.py remigrate
    python askme_fedukov/manage.py fill_db 50
    ```

6. Launch the server

    ```bash
    python askme_fedukov/manage.py runserver
    ```

7. Open the [localhost](http://127.0.0.1:8000/)

## Status

1. Layout

2. Routing:

    | Page                              | URL                                    | Meaning                                   |
    |-----------------------------------|----------------------------------------|-------------------------------------------|
    | Index page                        | <http://127.0.0.1:8000/>              | список новых вопросов (главная страница)  |
    | Hot questions page                | <http://127.0.0.1:8000/hot/>          | список “лучших” вопросов                  |
    | Tag page                          | <http://127.0.0.1:8000/tag/blablabla/> | список вопросов по тэгу                   |
    | Question page                     | <http://127.0.0.1:8000/question/5/>   | страница одного вопроса со списком ответов |
    | Ask page                          | <http://127.0.0.1:8000/ask/>          | форма создания вопроса                   |
    | Login page                        | <http://127.0.0.1:8000/login/>        | форм логина                              |
    | Register page                     | <http://127.0.0.1:8000/signup/>       | форма регистрации                        |
    | Settings page                     | <http://127.0.0.1:8000/settings/>     | настройки                                |
    | Profile page                     | <http://127.0.0.1:8000/profile/0>      | публичная страница пользователя                                |

3. Database:

    **Fill with test data**

    ```sh
    # Before filling, you\'re likely to migrate with
    # python manage.py remigrate
    # Which cleans up db -> makemigrations -> migrate
    
    python manage.py fill_db [ratio]
    # To remove all data use this
    python manage.py flush
    ```

    Where `ratio` is the fill factor for entities. After executing the command, the database should be populated with the following:

    - Users: equal to `ratio`
    - Questions: `ratio * 10`
    - Answers: `ratio * 100`
    - Tags: `ratio`
    - User ratings: `ratio * 200`
4. Forms
