#!/usr/bin/env bash

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