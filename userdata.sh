#!/bin/bash

#Make sure that we clone/run as ubuntu
su ubuntu
cd ~

# Get latest copy of mldht
git clone https://github.com/dylanmann/mldht.git
cd mldht

# build code
mvn package dependency:copy-dependencies appassembler:assemble && mvn antrun:run

# run daemon as root
cd work
(../bin/mldht 0<&- > out.log &) & 
