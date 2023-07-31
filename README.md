###########################################
######### Running the project #############
###########################################


###### Running local ###### 

On terminal 1 cmd:
1. `git clone xxx`
2. `cd docker_template/django`
3. `source venv/bin/activate`
4. `pip install -r requirements.txt`
5. Change debug to TRUE in settings.py in Django
6. `python manage.py runserver`

On terminal 2 cmd:
1. `sudo systemctl enable rabbitmq-server`
2. `sudo systemctl start rabbitmq-server`
3. `sudo systemctl status rabbitmq-server`

On terminal 3 cmd:
1. `celery -A core worker -B -l INFO` (If you want to run both separately, the code is `celery -A core worker -l info --pool=solo` and `celery -A core beat -l info`)

On terminal 4 cmd:
1. `python manage.py shell`
2. `from task1.tasks import add`
3. `add.delay(2,2)`

On terminal 5 cmd:
1. `cd docker_template/flask`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `flask run`

On URL: http://127.0.0.1:8000/reviews - test send of email


###### Running production ###### 

On terminal 1 cmd:
1. `git clone xxx`
2. `cd docker_template`
3. Change debug to FALSE in settings.py in the Django folder
4. `docker-compose build`
5. `docker-compose up`

On terminal 2 cmd:
1. `docker exec -it django_container sh`
2. `python manage.py shell`
3. `from task1.tasks import add`
4. `add.delay(2,2)`

On URL: http://127.0.0.1:8000/reviews - test send of email


###########################################
######### Building from scratch ###########
###########################################


##########################################
##### Setting up Django ##################
##########################################
1. `mkdir docker_template`
2. `cd docker_template`
3. Create `docker-compose.yml` in this directory
4. `mkdir django_app`
5. `cd django_app`
6. `python3 -m venv venv`
7. `source venv/bin/activate`
8. `pip install django` (plus all the packages you need)
9. `django-admin startproject core .`
10. `pip freeze > requirements.txt`
11. `python manage.py runserver`
12. Create `Dockerfile` in this directory

###########################################
##### Running single Dockerfile (Django) ##
###########################################
1. `cd docker_template/django`
2. `docker build --tag python-django1 .`
3. `docker run --publish 8000:8000 python-django1`
4. `docker exec -it fbdf9567f98a2cd08d2227fcfa787f2101dec138538941ead798b16614da20f5 /bin/bash`

##########################################
##### Setting up Flask ###################
##########################################
1. `mkdir docker_template`
2. `cd docker_template`
3. Create `docker-compose.yml` in this directory
4. `mkdir flask_app`
5. `cd flask_app`
6. `python3 -m venv venv`
7. `source venv/bin/activate`
8. `pip install flask` (plus all the packages you need)
9. `pip freeze > requirements.txt`
10. Create `app.py` file with the necessary code
11. `python app.py` or `flask run`
12. Create `Dockerfile` in this directory

##########################################
##### Running single Dockerfile (Flask) ##
##########################################
1. `cd docker_template/flask`
2. `docker build --tag python-flask1 .`
3. `docker run --publish 5000:5000 python-flask1`
4. `docker exec -it fbdf9567f98a2cd08d2227fcfa787f2101dec138538941ead798b16614da20f5 /bin/bash`

##########################################
##### Running entire Docker Compose ######
##########################################
1. `cd docker_template`
2. `docker-compose build`
3. `docker-compose up`
4. `docker exec -it name_of_container sh`

##########################################
##### Packages ###########################
##########################################
#### Important packages
- `pip install psycopg2-binary`
- `pip install celery`
- `pip install django-celery-beat`
- `pip install python-dotenv`

#### Unnecessary packages
- `pip install flower`
- `pip install django-celery-results`

### Original requirements.txt