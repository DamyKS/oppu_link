set -o errexit  # exit on error

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate
#python manage.py createcachetable
#python manage.py createsuperuser --no-input