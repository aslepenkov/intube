#!/bin/bash

# Define the container and image names
CONTAINER_NAME=intube
IMAGE_NAME=intube
DOCKERFILE_PATH=./Dockerfile  # Adjust the path to your Dockerfile

# Stop the running container
# docker stop $CONTAINER_NAME

# Remove the container
docker rm -f $CONTAINER_NAME

# Remove the image
docker rmi $IMAGE_NAME

# Build the image
docker build -t $IMAGE_NAME .

# Run the container
docker run -d --name $CONTAINER_NAME $IMAGE_NAME
