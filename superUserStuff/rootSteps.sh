#!/bin/bash

apt upgrade -y

apt install nginx -y
apt install sqlite3 -y
apt install bat -y
apt install unzip -y

apt install python3-certbot-nginx -y

ufw allow OpenSSH
ufw default deny incoming
ufw default allow outgoing

ufw allow http
ufw allow https
ufw enable
ufw status verbose

echo You mant to add users like so :
echo adduser cdot
echo And then add cdot to /etc/sudoers
echo
echo You should also set up https like so :
echo certbot --nginx -d bussinfr.net
echo Enter email, agree to terms, and then test renewals with :
echo certbot renew --dry-run
echo
echo Renewals used to be by a cron job but are
echo now done with a systemd timer that you can
echo view like so :
echo systemctl status certbot.timer
echo
echo Also put top level HTML and favicon in place.
echo
