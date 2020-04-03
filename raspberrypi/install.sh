#!/bin/bash

sudo apt-get install -y python3 python3-pip python3-smbus python3-pil
sudo apt-get install -y i2c-tools
sudo pip3 install --upgrade setuptools
sudo pip3 install -r ../requirements.txt

# sense websockets dont support TLS 2
#CipherString = DEFAULT@SECLEVEL=2 --> 1


sudo cp senseshow.service /etc/systemd/system/senseshow.service

sudo systemctl enable senseshow.service


## send pvoutput data
echo "*/5 * * * *  python3 $(pwd)/pvoutput.py" | sudo crontab -



## Notes
# /etc/ssl/openssl.cnf  and lower ciper until sense fixeswebsockers https://community.home-assistant.io/t/debian-10-and-openssl-1-1-1b-wrong-signature-type-errors/121050
# enable SPI and I2C in raspi0config/