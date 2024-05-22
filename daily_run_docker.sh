#!/bin/bash

# Name of the Docker image
IMAGE_NAME="option_auto_download"

# Tag for the Docker image
IMAGE_TAG="latest"

if [ $? -eq 0 ]; then
    # Get the credentials directory
    current_dir=$(pwd)
    credentials_f="credentials"
    credentials_folder="$current_dir/$credentials_f"
    echo 'credentials file path:' $credentials_folder

    if [ $(ls -A $credentials_folder | wc -l) -eq 0 ]; then
        echo "credentials directory is empty."
    else
        docker run --rm -v $credentials_folder:/app/credentials/ --name daily-vis-container tuzikexin/${IMAGE_NAME}:${IMAGE_TAG}  --ticker VIX SPX --start_time_h 8 --start_time_m 55 --end_time_h 16 --end_time_m 5 --test_mode no

        # Check if the Docker container ran successfully
        if [ $? -eq 0 ]; then
            echo "Container ran successfully."
        else
            echo "Container encountered an error during execution."
            docker rm daily-vis-container
        fi
    fi
fi
