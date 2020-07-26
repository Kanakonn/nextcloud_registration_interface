#!/bin/bash
pip install -r requirements.txt

cd /tmp
git clone https://github.com/matejak/nextcloud-API.git
cd nextcloud-API
python setup.py install
