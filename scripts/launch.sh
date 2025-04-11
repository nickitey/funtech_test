#!/bin/sh

launch_service() {
  uwsgi -m --ini uwsgi.ini &
  celery -A apirewards worker -l info
}

openssl genrsa -out /app/private_key.pem 2048
openssl rsa -in /app/private_key.pem -pubout -out /app/public_key.pem
export PRIVATE_KEY=$(cat /app/private_key.pem)
export PUBLIC_KEY=$(cat /app/public_key.pem)

python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser --no-input 1>/dev/null 2>&1

if [ $? -eq 0 ]
then
  echo "Суперюзер успешно создан"
  launch_service
else
  echo "Суперюзер с такими именем уже существует. Пропускаю" >&2
  launch_service
fi
