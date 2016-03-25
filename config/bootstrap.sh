#!/usr/bin/env bash

# installs the package passed in if it's not installed
install () {
    package=$1
    dpkg-query -l $package &> /dev/null
    if [ $? -ne 0 ]; then
      apt-get -y install $package
    fi
}

apt-get update
apt-get upgrade

install git
install sqlite3

install python3
install python3-dev
install python3-pip
#install sqlite3
#install postgresql-server-dev-all
install postgresql-9.3
install libpq-dev

sudo -u postgres psql -c "CREATE USER adi_calendar WITH PASSWORD 'bzYcqT4k';"
sudo -u postgres psql -c "CREATE DATABASE calendar;"
sudo -u postgres psql -c "GRANT CONNECT ON DATABASE calendar TO adi_calendar;"
sudo -u postgres psql -c "GRANT ALL ON DATABASE calendar TO adi_calendar;"

sudo pip3 install -r /vagrant/config/requirements.txt
