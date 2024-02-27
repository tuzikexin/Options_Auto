#!/bin/bash

# Name of the Docker image
IMAGE_NAME="option_auto_download"

# Tag for the Docker image
IMAGE_TAG="latest"

if [ $? -eq 0 ]; then
    current_dir=$(pwd)
    credentials_f="credentials"
    credentials_folder="$current_dir/$credentials_f"
    # Get the credentials directory
    credentials_f="credentials"
    credentials_folder="$current_dir/$credentials_f"
    echo 'credentials path:' $credentials_folder
    docker run --rm -v $credentials_folder:/app/credentials/ --name daily-vis-container tuzikexin/${IMAGE_NAME}:${IMAGE_TAG}  --ticker VIX --end_time_h 22 --end_time_m 45 --test_mode no

    # Check if the Docker container ran successfully
    if [ $? -eq 0 ]; then
        echo "Container ran successfully."
    else
        echo "Container encountered an error during execution."
        docker rm daily-vis-container
    fi
fi
