#!/bin/bash

# Name of the Docker image
IMAGE_NAME="option_auto_download"

# Tag for the Docker image
IMAGE_TAG="latest"

# Build the Docker image
echo "Building Docker image..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Docker image built successfully."

    # Remove Dangling Images
    docker image prune -f

    # Run the Docker container with specified arguments
    echo "Running Docker container..."
    docker run --rm -v /Users/kexin/Desktop/xiaoyu/app/:/app/ --name temp-container ${IMAGE_NAME}:${IMAGE_TAG} --ticker VIX --end_time_h 23 --end_time_m 59 --test_mode yes

    # Check if the Docker container ran successfully
    if [ $? -eq 0 ]; then
        echo "Container ran successfully. and push to dockerhub"
        docker tag ${IMAGE_NAME}:${IMAGE_TAG} tuzikexin/${IMAGE_NAME}:${IMAGE_TAG}
        # docker login
        docker push tuzikexin/${IMAGE_NAME}:${IMAGE_TAG}
    else
        echo "Container encountered an error during execution."
    fi
else
    echo "Docker image build failed."
fi
