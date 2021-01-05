FROM fgrehm/netbeans:v8.0.1

RUN sudo apt-get update -y && sudo apt-get upgrade -y && sudo  apt-get install -y libgl1-mesa-dev 
COPY BoardCAD BoardCAD
WORKDIR BoardCAD

CMD java -jar BoardCAD.jar
