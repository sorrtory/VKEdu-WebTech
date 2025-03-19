# Tp-tasks

Технопарк Mail.Ru / 1-ый семестр / Web-технологии

## Source

<https://github.com/ziontab/tp-tasks>

## Check this out <sorrtory.ru>
Or you can try to build it on your own

Clone the code

```bash
git clone https://github.com/sorrtory/VKEdu-WebTech
```

Set up a virtual enviroment

```bash
cd VKEdu-WebTech && python3 -m venv .venv && source .venv/bin/activate
```

Install the requirements `django django-bootstrap-v5 django-livereload-server django-bootstrap-icons`

```bash
pip install -r requirements.txt
```

Launch the server

```bash
python askme_fedukov/manage.py runserver
```

And follow [the link](http://127.0.0.1:8000/)

## Status

1. First Hometask. Layout.

    > Question. Should I ignore the validation warning about h2 absence in article?

2. Routing:

    | Page           | URL                              |
    |----------------|----------------------------------|
    | Index page     | <http://127.0.0.1:8000/>           |
    | Question page  | <http://127.0.0.1:8000/question/>  |
    | Tag page       | <http://127.0.0.1:8000/tag/>       |
    | Ask page       | <http://127.0.0.1:8000/ask>        |
    | Login page     | <http://127.0.0.1:8000/login>      |
    | Register page  | <http://127.0.0.1:8000/signup>     |
    | Settings page  | <http://127.0.0.1:8000/settings>   |

3. Waiting for the next task...
