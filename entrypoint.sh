#!/bin/bash

pip install -e /kh_reminder
python /kh_reminder/kh_reminder/scripts/initializedb.py
pserve /kh_reminder/production.ini --reload
