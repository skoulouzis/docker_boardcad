FROM fgrehm/netbeans:v8.0.1

RUN sudo apt-get update -y && sudo apt-get upgrade -y && sudo apt-get install -y libgl1-mesa-dev cups
RUN sudo apt-get autoclean -y && sudo apt-get autoremove -y
COPY BoardCAD BoardCAD
WORKDIR BoardCAD

CMD java -jar BoardCAD.jar
