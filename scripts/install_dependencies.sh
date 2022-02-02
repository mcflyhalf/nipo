#!/bin/bash
# pip install upgradeable from reqs.txt
/home/ubuntu/projects/nipo/bin/python -m pip install --upgrade -r requirements.txt

# pip install nipo (not editable)
cd /home/ubuntu/projects/nipo 
/home/ubuntu/projects/nipo/bin/python -m pip install .