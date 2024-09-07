# SWAP Project Backend (Migration from [SWAP Legacy](https://github.com/zalalov/swap-web-legacy))

## Instructions for local run:
### 1. Create .env file:
```
$ cp .env.example .env
```
### 2. Add all the field values to **.env** file (version from 13.05.2024 below):
```
DJANGO_DB_HOST=
DJANGO_DB_USER=
DJANGO_DB_PASSWORD=
DJANGO_DB_NAME=
DJANGO_DB_PORT=
```
### 3. Create new sqlite based database with WRITE access (with users/auth/sessions/etc inside), because of read-only for the default one:
```
$ python manage.py migrate --database=users
```
### 4. Create new superuser within `users` database, ignore warnings about non-applied migrations for `default` database:
```
$ python manage.py createsuperuser --database=users
```

### 5. Run docker-compose command (docker-compose has to be installed):
```
$ docker compose up
```
