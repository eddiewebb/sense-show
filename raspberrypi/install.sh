#!/bin/bash

sudo cp senseshow.service /etc/systemd/system/senseshow.service

sudo systemctl enable myscript.service