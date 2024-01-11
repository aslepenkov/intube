# RUN YOUR OWN YT/INSTA/TT videos downloader or use intubebot in telegram

### Create a new virtual environment by running 

```
sudo apt install python3.11-venv
python3 -m venv <venv_name>
source <venv_name>/bin/activate
deactivate
pip install -r requrements.txt
pip freeze > requrements.txt
```

### when updated .service file
```
sudo systemctl restart intube_bot.service
sudo systemctl daemon-reload
sudo systemctl status intube_bot.service
sudo systemctl start intube_bot.service
sudo systemctl stop intube_bot.service
```

### to restart process
```
ps -ef | grep intube
kill <PID>
```
or
```
ps -ef | grep intube | grep -v grep | awk '{print $2}' | xargs kill -9
nohup ./script.sh &
```
then start:
```
nohup ./script.sh &
```

### logs
```
cat /var/log/syslog | grep intube
tac /var/log/syslog | grep intube
```

### concat to one file
```
cat * > logs.txt
```

### mongo filter example
```
{"user": {"$regex": "^id.*"}}
```

### TODO

- [x] single download_media or bv+wa
- [x] download_media return object, not array
- [x] link picking in message str 
- [x] user friendly filename mp3 and cover
- [x] fix err text mmsg without links
- [ ] fix tiktok video

