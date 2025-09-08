# AskPupkin

> Technopark Mail.Ru / 1st semester / Web Technologies

This is a default Q&A platform taking Stack Overflow as a reference.

Users have basic [features](#features) such as auth, ask, answer, like and some [extras](#7.Extras) as well.

The app is powered by Django, with use of PostgreSQL, Memcached, Centrifugo and Nginx, deployed with Docker as always.

## Source task

<https://github.com/ziontab/tp-tasks>

## Check this out [here](askme.sorrtory.ru)

### Run locally

```sh
git clone https://github.com/sorrtory/VKEdu-WebTech.git
cd VKEdu-WebTech
cp .env.example.prod .env
docker compose -f prod/docker-compose.yaml up --build
# You will have to wait utill the `web` script fill the example database.
```

Then you can go to [nginx page](http://localhost:1337)

### Step by step run

1. Clone the code

    ```bash
    git clone https://github.com/sorrtory/VKEdu-WebTech
    ```

2. Set up a virtual enviroment

    ```bash
    cd VKEdu-WebTech && python3 -m venv .venv && source .venv/bin/activate
    ```

3. Create [.env](.env.example.dev) file set for localhost

    ```sh
    cp .env.example.dev .env
    ```

4. Install python requirements

    ```bash
    pip install -r requirements.txt
    ```

5. Set up containers: `db`, `memcached`, `centrifugo`, `cron`

    ```sh
    docker compose -f prod/docker-compose.yaml up -d --build db memcached centrifugo cron
    ```

6. Fill the database

    ```sh
    # Ensure the database is ready
    docker exec prod-db-1 bash -c "pg_isready"
    # Ensure to have a proper environment
    # cp .env.example.dev .env

    # Create tables (script does drop+migrate)
    python askme_fedukov/manage.py remigrate
    # Clean old data with
    python askme_fedukov/manage.py flush
    # Add mock data with ratio 50
    python askme_fedukov/manage.py fill_db 50
    ```

7. Launch the server

    ```bash
    python askme_fedukov/manage.py runserver
    ```

8. Open the [localhost](http://127.0.0.1:8000/)

## Features

### 1. Layout

[Reference](https://github.com/ziontab/tp-tasks/blob/master/files/markdown/task-1.md#6-%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80%D0%BD%D1%8B%D0%B9-%D0%B2%D0%BD%D0%B5%D1%88%D0%BD%D0%B8%D0%B9-%D0%B2%D0%B8%D0%B4-%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86)

### 2. Routing

Some examples of implemented resources:

| Page              | URL                                    | Description                                      |
|-------------------|----------------------------------------|--------------------------------------------------|
| Index page        | <http://127.0.0.1:8000/>               | list of new questions (main page)                |
| Hot questions     | <http://127.0.0.1:8000/hot/>           | list of “hot” questions                          |
| Tag page          | <http://127.0.0.1:8000/tag/blablabla/> | list of questions by tag                         |
| Question page     | <http://127.0.0.1:8000/question/5/>    | single question page with answers                |
| Ask page          | <http://127.0.0.1:8000/ask/>           | question creation form                           |
| Login page        | <http://127.0.0.1:8000/login/>         | login form                                       |
| Register page     | <http://127.0.0.1:8000/signup/>        | registration form                                |
| Settings page     | <http://127.0.0.1:8000/settings/>      | user settings                                    |
| Profile page      | <http://127.0.0.1:8000/profile/0/>     | public user profile page                         |

### 3. Database

[Fill it](askme_fedukov/app/management/commands/fill_db.py) with test data using

```sh
# Before filling, you're likely need to migrate with 
# python manage.py remigrate
# That'll DROP ALL public tables -> makemigrations -> migrate

python manage.py fill_db [ratio]

# To remove all data use django's flush
python manage.py flush
```

Where `[ratio]` is the fill factor for entities.
After executing the command, the database should be populated with the following:

- Users: `ratio`
- Questions: `ratio * 10`
- Answers: `ratio * 100`
- Tags: `ratio`
- Likes: `ratio * 200`

### 4. Forms

Django's [forms](askme_fedukov/app/forms.py)
with my [form checker](/askme_fedukov/app/utils/form_checker.py) allows to:

- Login
- Register
- Edit Profile
- Ask new question
- Answer Questions

### 5. Ajax

With the help of [js](./askme_fedukov/app/static/ajax.js) and [POST](https://github.com/sorrtory/VKEdu-WebTech/blob/master/askme_fedukov/app/views.py#L297-L336)

- Likes. User can like Answers and Questions but not his own ones.
- Correct. User can mark Answers to his own Questions.

Unauthorized user can't see this features, actually

### 6. WSGI

Created [test](wsgi/test.py) script for parsing GET/POST params

Then the [gunicorn](./prod/gunicorn.conf.py) were used with the help of django.

### 7. Extras

- Set up [Centrifugo](./askme_fedukov/app/utils/notification.py) as a notification service. \
    If someone adds a new answer, everyone, who is on the question's page, will recieve a notification.
- Set up [cache](./askme_fedukov/app/utils/cache.py) for aside block. \
    By default cache expires after 30 sec, and every 1 min it's [filled](./prod/cron.sh). Then it would be obvious that cache works properly.
- Set up [search](./askme_fedukov/app/static/search.js) bar to do full text searching with Django's [defaults]((https://github.com/sorrtory/VKEdu-WebTech/blob/master/askme_fedukov/app/models.py#L180-L190))

## Conclusion

### Outline

Django is really powerful when you need to create the app with dispatch.
It has a lot of in-built options almost for any case and you must use them as they are.

In short, if you need a simple web app the formula is `bootsrap+django+djangoREST`. \
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
- Format code as you write/generate it (then formatter won't fuck jinja's embeds)
- Cron in container is strange. Scripting the host will be better using kube/ansible.
