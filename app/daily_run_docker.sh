#!/bin/bash

# Name of the Docker image
IMAGE_NAME="option_auto_download"

# Tag for the Docker image
IMAGE_TAG="latest"

# Check if build was successful
if [ $? -eq 0 ]; then

    echo "Running Docker container..."
    docker run --rm -v /Users/kexin/Desktop/xiaoyu/app/:/app/ --name daily-container ${IMAGE_NAME}:${IMAGE_TAG}  --ticker VIX --end_time_h 22 --end_time_m 45 --test_mode no

    # Check if the Docker container ran successfully
    if [ $? -eq 0 ]; then
        echo "Container ran successfully."
    else
        echo "Container encountered an error during execution."
    fi
fi
