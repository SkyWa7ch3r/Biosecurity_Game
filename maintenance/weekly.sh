pkill -9 daphne
killall otree
cd /usr/Biosecurity_Game_V2/
/usr/pgsql-9.6/bin/pg_dump -a -U otree -h localhost django_db > /usr/postgres-backup/biosecurity-$(date +"%d-%m-%Y").sql
echo y | otree resetdb
psql -U otree django_db < /usr/postgres-backup/biosecurity-$(date +"%d-%m-%Y").sql
sudo su -c "reboot"
