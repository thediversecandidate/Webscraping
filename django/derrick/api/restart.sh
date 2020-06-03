#!/bin/sh

sudo supervisorctl reread
sudo supervisorctl update

sudo supervisorctl stop derrickcelery
sudo supervisorctl start derrickcelery
sudo supervisorctl status derrickcelery
