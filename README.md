# Tp-tasks

Технопарк Mail.Ru / 1-ый семестр / Web-технологии

## Source

<https://github.com/ziontab/tp-tasks>

## Check this out [sorrtory.ru](sorrtory.ru)

Or you can try to build it on your own

Clone the code

```bash
git clone https://github.com/sorrtory/VKEdu-WebTech
```

Set up a virtual enviroment

```bash
cd VKEdu-WebTech && python3 -m venv .venv && source .venv/bin/activate
```

Install the requirements

```bash
pip install -r requirements.txt
```

Launch the server

```bash
python askme_fedukov/manage.py runserver
```

And follow [the link](http://127.0.0.1:8000/)

## Status

1. Layout

2. Routing:

    | Page                              | URL                                    | Meaning                                   |
    |-----------------------------------|----------------------------------------|-------------------------------------------|
    | Index page                        | <http://127.0.0.1:8000/>              | список новых вопросов (главная страница)  |
    | Hot questions page                | <http://127.0.0.1:8000/hot/>          | список “лучших” вопросов                  |
    | Tag page                          | <http://127.0.0.1:8000/tag/blablabla/> | список вопросов по тэгу                   |
    | Question page                     | <http://127.0.0.1:8000/question/35/>  | страница одного вопроса со списком ответов |
    | Ask page                          | <http://127.0.0.1:8000/ask/>          | форма создания вопроса                   |
    | Login page                        | <http://127.0.0.1:8000/login/>        | форма логина                              |
    | Register page                     | <http://127.0.0.1:8000/signup/>       | форма регистрации                        |
    | Settings page                     | <http://127.0.0.1:8000/settings/>     | настройки                                |

3. Database:

    **Fill with test data**

    ```sh
    python manage.py fill_db [ratio]
    ```

    Where `ratio` is the fill factor for entities. After executing the command, the database should be populated with the following:

    - Users: equal to `ratio`
    - Questions: `ratio * 10`
    - Answers: `ratio * 100`
    - Tags: `ratio`
    - User ratings: `ratio * 200`
4. Waiting for the new task...
