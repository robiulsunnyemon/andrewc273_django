#!/bin/bash
set -e

domains=(admin.dojapr.com)
email="your-email@example.com" # Replace with your email address.
staging=0 # Set to 1 for testing to avoid rate limits.

data_path="./certbot/conf"
webroot_path="./certbot/www"

if [ "$email" = "your-email@example.com" ]; then
  echo "ERROR: You must set your email address in certbot/init-letsencrypt.sh"
  exit 1
fi

if [ -d "$data_path/live/${domains[0]}" ]; then
  echo "Certificate data already exists for ${domains[0]}"
fi

mkdir -p "$data_path"
mkdir -p "$webroot_path"

echo "### Creating dummy certificate for ${domains[0]}..."
docker-compose run --rm --entrypoint "" certbot sh -c "
  mkdir -p /etc/letsencrypt/live/${domains[0]} && \
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout \"/etc/letsencrypt/live/${domains[0]}/privkey.pem\" \
    -out \"/etc/letsencrypt/live/${domains[0]}/fullchain.pem\" \
    -subj \"/CN=localhost\"
"

echo "### Starting nginx..."
docker-compose up -d nginx

staging_arg=""
if [ "$staging" != "0" ]; then
  staging_arg="--staging"
fi

echo "### Requesting Let's Encrypt certificate for ${domains[0]}..."
docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot \
  $staging_arg \
  --email "$email" --agree-tos --no-eff-email \
  -d "${domains[0]}"

echo "### Reloading nginx with the real certificate..."
docker-compose exec nginx nginx -s reload

echo "### Certificate obtained and nginx reloaded."
