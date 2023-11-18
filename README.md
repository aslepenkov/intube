#RUN YOUR OWN YT/INSTA/TT videos downloader bot

## TODO ADD used libs
* yt-dlp
* pymongo
* aiogram
* instaloader
* python-dotenv

## TODO ADD RELEASENOTES


# when updated .service file
sudo systemctl daemon-reload

#status
sudo systemctl status intube_bot.service

#start 
sudo systemctl start intube_bot.service

#stop 
sudo systemctl stop intube_bot.service

#logs
cat /var/log/syslog | grep  intube
tac /var/log/syslog | grep  intube

#concat to one file
cat * > logs.txt

