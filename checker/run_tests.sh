#!/bin/bash

docker login registry.gitlab.com/onti-fintech/onti-2021-fintech/fintech2021002/n2n-oracle/ftchecker-final2021-n2n-oracle
sudo docker pull registry.gitlab.com/onti-fintech/onti-2021-fintech/fintech2021002/n2n-oracle/ftchecker-final2021-n2n-oracle
id=$(sudo docker create registry.gitlab.com/onti-fintech/onti-2021-fintech/fintech2021002/n2n-oracle/ftchecker-final2021-n2n-oracle)
sudo docker container cp $id:/home/n2n-oracle/python/tests origin_tests
mv origin_tests/tests/* origin_tests
sudo docker rm -v $id
rm -rf origin_tests/tests
git checkout HEAD -- origin_tests/conftest.py
sudo python3 prepare_tests.py --keep_dependencies
sudo docker network prune -f
sudo docker-compose up --abort-on-container-exit