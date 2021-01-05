# docker_boardcad

Run :

```bash
docker run --rm  --name firefox -e XAUTHORITY=/.Xauthority --net host -v /tmp/.X11-unix:/tmp/.X11-unix -v ~/.Xauthority:/.Xauthority  -e DISPLAY=:0.0 alogo53/
docker_boardcad 
```
