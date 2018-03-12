#!/bin/bash
cd ~
git clone https://github.com/dylanmann/mldht.git
cd mldht
mvn package dependency:copy-dependencies appassembler:assemble && mvn antrun:run
cd work
(../bin/mldht 0<&- &> out.log &) & 
