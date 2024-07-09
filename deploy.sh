#!/bin/bash

# Check if container name is passed as an argument
if [ -z "$1" ]
then
  echo "No container name supplied. Usage: ./script.sh <container_name>"
  exit 1
fi

# Define the container name from the argument
CONTAINER_NAME=$1
REPO_URL=https://github.com/aslepenkov/intube.git

# Change to the directory of your local clone of the Git repository
# cd /path/to/your/repository

# Stash any local changes and pull from the repository
git stash
git pull $REPO_URL

# Stop the running container
# docker stop $CONTAINER_NAME

# Remove the container
docker rm -f $CONTAINER_NAME

# Remove the image
docker rmi $CONTAINER_NAME

# Build the image
docker build -t $CONTAINER_NAME .

# Run the container
docker run -d --name $CONTAINER_NAME $CONTAINER_NAME