#!/bin/bash
# The userdata of each crawler node is
  # #! /bin/bash
  # wget -O - https://raw.githubusercontent.com/gmosley/boontorrent/master/userdata.sh | bash
# This ensures that our deployment process is uniform

# Make sure that we clone/run as ubuntu
su ubuntu
cd ~

# install dependencies
echo 'Acquire::ForceIPv4 "true";' | sudo tee /etc/apt/apt.conf.d/99force-ipv4
sudo apt update
sudo apt install -y make htop openjdk-8-jdk maven

# get the geocity database
# wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz
# tar -zxvf GeoLite2-City.tar.gz
# cd `find GeoLite2-City_* | head -1`
# mv *.mmdb ~
# cd ~

# Get latest copy of mldht
git clone https://github.com/dylanmann/mldht.git
cd mldht

# build code
mvn package dependency:copy-dependencies appassembler:assemble && mvn antrun:run

# run daemon as root
cd work
(make 0<&- &>> out.log &) & 
