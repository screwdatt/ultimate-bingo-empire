#!/bin/bash
set -e

echo "=== Ultimate Bingo Empire Deploy ==="
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip nginx supervisor redis-server certbot python3-certbot-nginx

useradd --no-create-home --shell /bin/false bingo || true
mkdir -p /var/www/bingo /var/log/bingo
cd /var/www/bingo

git clone https://github.com/YourUsername/ultimate-bingo-empire.git . || git pull
chown -R bingo:bingo /var/www/bingo

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

read -p "Domain (e.g. bingo.example.com): " DOMAIN
read -p "Stripe Secret Key: " STRIPE_SECRET
read -p "Stripe Publishable Key: " STRIPE_PUB
read -p "Stripe Webhook Secret: " STRIPE_WEBHOOK

sed -i "s|YOUR_DOMAIN|$DOMAIN|g" bingo_project/settings.py
sed -i "s|sk_live_.*|$STRIPE_SECRET|" bingo_project/settings.py
sed -i "s|pk_live_.*|$STRIPE_PUB|" bingo_project/settings.py
sed -i "s|whsec_.*|$STRIPE_WEBHOOK|" bingo_project/settings.py

python manage.py migrate
python manage.py collectstatic --no-input

echo "Done! Visit https://$DOMAIN"
