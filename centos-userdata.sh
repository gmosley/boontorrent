#!/bin/bash

# Make sure that we clone/run as ubuntu
su ubuntu
cd ~

# install dependencies
sudo yum install -y make htop java-1.8.0-openjdk-devel maven

# get the geocity database
wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz
tar -zxvf GeoLite2-City.tar.gz
cd `find GeoLite2-City_* | head -1`
mv *.mmdb ~
cd ~

# Get latest copy of mldht
git clone https://github.com/dylanmann/mldht.git
cd mldht

# build code
mvn package dependency:copy-dependencies appassembler:assemble && mvn antrun:run

# run daemon as root
cd work
sleep 10
(../bin/mldht 0<&- &>> out.log &) & 
