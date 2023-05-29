#!/bin/bash

# Check if Docker is installed
if ! [ -x "$(command -v docker)" ]; then
  # Install Docker
  echo "Docker is not installed. Installing Docker..."
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  rm get-docker.sh
  # Add user to Docker group
  sudo usermod -aG docker $USER
  echo "Docker has been installed and added to the current user group."
else
  echo "Docker is already installed."
fi

# Pull Flaresolverr
docker_images=$(docker images | grep "flaresolverr/flaresolverr" | wc -l)
if ! [ ${docker_images} -ge 1 ]; then
	echo "flaresolverr's container was not found. Pulling it.. (~200Mb)"
	docker pull flaresolverr/flaresolverr
else 
  echo "Flaresolverr's docker container found."
fi

running_dockers=$(docker container ls | grep "flaresolverr/flaresolverr:latest" | wc -l)
if [ ${running_dockers} -eq 0 ]; then
  echo "Launching Flaresolverr ..."
  docker run -d   --name=flaresolverr   -p 8191:8191   -e LOG_LEVEL=info   --restart unless-stopped   flaresolverr/flaresolverr:latest
else 
  echo "Flaresolverr is already running."
fi