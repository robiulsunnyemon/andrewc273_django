# Certbot Setup for admin.dojapr.com

This project uses Docker Compose with Nginx and Certbot to issue Let's Encrypt certificates.

## What changed

- `docker-compose.yml` now includes `version: "3.8"` and `restart: unless-stopped` for main services.
- `nginx/nginx.conf` now has better HTTPS headers and TLS settings.
- Added `certbot/init-letsencrypt.sh` to bootstrap a dummy cert, start Nginx, and request a real Let's Encrypt certificate.

## Usage

1. Open `certbot/init-letsencrypt.sh` and replace `your-email@example.com` with a real email.
2. Make the script executable:

```bash
chmod +x certbot/init-letsencrypt.sh
```

3. Run the bootstrap script:

```bash
./certbot/init-letsencrypt.sh
```

4. After it succeeds, start the full stack:

```bash
docker-compose up -d
```

## GitHub Actions

The deploy workflow expects a secret named `CERTBOT_EMAIL` containing the email address you want to use for Let's Encrypt.

```bash
docker-compose up -d
```

## Important notes

- Make sure DNS for `admin.dojapr.com` points to your server.
- Port `80` and `443` must be open on the server.
- If you use GitHub Actions deploy, run `certbot` before `docker-compose up -d` so the cert exists when Nginx starts.

## Renewal

Renew manually with:

```bash
docker-compose run --rm certbot renew --webroot -w /var/www/certbot
```

Then reload Nginx:

```bash
docker-compose exec nginx nginx -s reload
```
