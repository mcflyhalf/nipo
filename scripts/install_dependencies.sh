#!/bin/bash
# pip install upgradeable from reqs.txt
cd /home/ubuntu/projects/nipo 
source nipo_prod_env.sh
/home/ubuntu/projects/nipo/bin/python -m pip install --upgrade -r requirements.txt

# pip install nipo (not editable)
/home/ubuntu/projects/nipo/bin/python -m pip install .
chown -R ubuntu:www-data .
chmod -R 774 .
