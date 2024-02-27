#!/bin/bash

# Name of the Docker image
IMAGE_NAME="option_auto_download"

# Tag for the Docker image
IMAGE_TAG="latest"

# Remove Dangling Images
docker system prune -f
docker pull tuzikexin/${IMAGE_NAME}:${IMAGE_TAG}
