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

directives_to_add="
    client_max_body_size 4000m;
    server_names_hash_bucket_size 64;
"

if grep -q "client_max_body_size" /etc/nginx/nginx.conf && grep -q "server_names_hash_bucket_size" /etc/nginx/nginx.conf; then
    echo "Directives already exist in nginx.conf"
    exit 0
fi

line_number=$(sudo awk '/http \{/{print NR; exit}' /etc/nginx/nginx.conf)
if [ -n "$line_number" ]; then
    sudo head -n "$line_number" /etc/nginx/nginx.conf > /etc/nginx/nginx.conf.new
    echo "$directives_to_add" | sudo tee -a /etc/nginx/nginx.conf.new > /dev/null
    sudo tail -n +$(($line_number + 1)) /etc/nginx/nginx.conf >> /etc/nginx/nginx.conf.new
    sudo mv /etc/nginx/nginx.conf.new /etc/nginx/nginx.conf
else
    echo "Error: Unable to find 'http {' in nginx.conf"
    exit 1
fi

sudo systemctl restart nginx
sudo systemctl status nginx