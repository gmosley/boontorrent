FROM ubuntu:17.10

RUN apt-get update && apt-get install -y \
  git \
  python3 \
  python3-pip \
  python3-libtorrent

RUN pip3 install termcolor

ADD prototype3.py .

EXPOSE 40363/tcp
EXPOSE 40363/udp

ENTRYPOINT ["python3", "prototype3.py"]