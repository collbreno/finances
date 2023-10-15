
# Setting up Django and packages
First of all, install `django` and other dependencies used in this project:
```
pip install django apscheduler yahooquery
```
Run the migrations to create and set up the database.
```
python manage.py migrate
```

## Setting up SMTP 
Inside `mysite` folder, you must create a `secrets.py` file to provide the `email` and `password` used for sending emails.
```python
# secrets.py
SMTP_EMAIL = 'your_email@example.com'
SMTP_PASSWORD = 'your_password'
```
Your project structure should look like this:
```
├── ...
├── db.sqlite3
├── manage.py
├── finances
│   ├── ...
└── mysite
    ├── ...
    ├── secrets.py <-- here
    ├── settings.py
    └── ...
```
Others SMTP settings, like `EMAIL_HOST` or `EMAIL_PORT`, can be customized in `settings.py` file inside `mysite` folder. 

See https://docs.djangoproject.com/en/4.2/topics/email for more details.

## Starting apscheduler
In order to keep active the service responsible for sending emails and registering the notifications in the database, you must run the following command in a separate console at the project root:
```
python manage.py runapscheduler
```
This will start the `apscheduler`, responsible for scheduling the tasks to watch the tunnels periodically.

See https://pypi.org/project/django-apscheduler for more details.

## Running the server
Start the development server:
```
python manage.py runserver
```
Now you can access the project at `http://localhost:8000/finances` in your web browser.