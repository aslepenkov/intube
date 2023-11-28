#RUN YOUR OWN YT/INSTA/TT videos downloader bot

# commands used
## Create a new virtual environment by running python3 -m venv <venv_name>.
source <venv_name>/bin/activate
deactivate
pip install -r requrements.txt
pip freeze > requrements.txt

# when updated .service file
sudo systemctl restart intube_bot.service
sudo systemctl daemon-reload
sudo systemctl status intube_bot.service
sudo systemctl start intube_bot.service
sudo systemctl stop intube_bot.service


# logs
cat /var/log/syslog | grep  intube
tac /var/log/syslog | grep  intube

## concat to one file
cat * > logs.txt

