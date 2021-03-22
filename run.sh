#!/bin/sh

cd /deployment
if [ $# -eq 0 ]
  then
    python3 src/deploy.py
elif [ "$1" == "oracle" ]
  then
    python3 src/oracle.py
fi


