# docker_boardcad

Run :
```
docker run --rm  --name boardcad -e XAUTHORITY=/.Xauthority --net host -v /tmp/.X11-unix:/tmp/.X11-unix 
-v ~/.Xauthority:/.Xauthority  -v $(pwd):/home/developer/boards  -e DISPLAY=:0.0 alogo53/docker_boardcad 
```
