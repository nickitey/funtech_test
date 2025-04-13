#!/bin/sh

openssl genrsa -out /app/private_key.pem 2048
openssl rsa -in /app/private_key.pem -pubout -out /app/public_key.pem
export PRIVATE_KEY=$(cat /app/private_key.pem)
export PUBLIC_KEY=$(cat /app/public_key.pem)

pytest
