# Django eCommerce project


### 1.1 Installation on Docker

```bash
git clone https://github.com/taskovikj/commerce.git
```
```bash
docker-compose up -d --build
```

### 1.2 Create database according to settings.py
### 1.3 Run migrations

```bash
docker exec -it django_container sh
```
```bash
python manage.py makemigrations aucions
```
```bash
python manage.py migrate
```


### 1.4 Restart django container

```
python manage.py runserver
```

