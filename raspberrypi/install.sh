#!/bin/bash

sudo apt-get install -y python-smbus
sudo apt-get install -y i2c-tool

sudo cp senseshow.service /etc/systemd/system/senseshow.service

sudo systemctl enable senseshow.service


## Notes
# /etc/ssl/openssl.cnf  and lower ciper until sense fixeswebsockers https://community.home-assistant.io/t/debian-10-and-openssl-1-1-1b-wrong-signature-type-errors/121050
# enable SPI and I2C in raspi0config