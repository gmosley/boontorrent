FROM openjdk:8 


RUN apt-get update && apt-get install -y \
  git \
  maven 

RUN git clone https://github.com/dylanmann/mldht.git

WORKDIR mldht

RUN mvn package dependency:copy-dependencies appassembler:assemble && \
    mvn antrun:run

WORKDIR work

EXPOSE 10044/tcp
EXPOSE 10044/udp

ENTRYPOINT ["../bin/mldht"] 
