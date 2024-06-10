# RUN YOUR OWN YT/INSTA/TT videos downloader or use intubebot in telegram

### to start app
```

sudo docker build -t intube .
sudo docker run -d --name intube intube

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
- [x] fix tiktok video
- [x] dockerize
- [x] /audio in message = send as audio
