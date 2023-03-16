python manage.py migrate


if [[ $APP_ENV == 'prod' ]]; then
  gunicorn tass_api.wsgi:application -c gunicorn.conf.py
elif [[ $APP_ENV == 'local' ]]; then
  python manage.py runserver 0.0.0.0:8080
else
  gunicorn tass_api.wsgi:application -c gunicorn.conf.py
fi