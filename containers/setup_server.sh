#!/usr/bin/env bash

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# source: https://earthly.dev/blog/private-docker-registry/
sudo apt update -y
sudo apt install curl apt-transport-https ca-certificates  -y
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
sudo chmod a+r /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) \
signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
| sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update -y
sudo apt install docker-ce docker-compose -y
docker --version || { >&2 echo "Failed to install docker" && exit 1; }

mkdir "$SCRIPT_DIR"/registry
mkdir "$SCRIPT_DIR"/registry/registry-data

cd "$SCRIPT_DIR"/registry
cp "$SCRIPT_DIR"/docker-compose.yml "$SCRIPT_DIR"/registry

sudo apt install nginx apache2-utils -y
sudo cp "$SCRIPT_DIR"/registry.conf /etc/nginx/conf.d/registry.conf

sudo cp "$SCRIPT_DIR"/nginx.conf /etc/nginx/nginx.conf

sudo systemctl restart nginx
sudo systemctl status nginx