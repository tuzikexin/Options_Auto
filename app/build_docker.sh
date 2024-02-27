#!/bin/bash

# Name of the Docker image
IMAGE_NAME="option_auto_download"

# Tag for the Docker image
IMAGE_TAG="latest"

# Build the Docker image
echo "Building Docker image..."
docker build -t tuzikexin/${IMAGE_NAME}:${IMAGE_TAG} .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Docker image built successfully."

    # Run the Docker container with specified arguments
    echo "Running Docker container..."
    # Get the parent directory of the current working directory
    current_dir=$(pwd)
    parent_dir=$(dirname "$current_dir")
    credentials_f="credentials"
    credentials_folder="$parent_dir/$credentials_f"
    echo 'credentials file path:' $credentials_folder

    if [ $(ls -A $credentials_folder | wc -l) -eq 0 ]; then
        echo "credentials directory is empty."
    else
        docker run --rm -v $credentials_folder:/app/credentials/ --name temp-vix-container tuzikexin/${IMAGE_NAME}:${IMAGE_TAG} --ticker VIX --end_time_h 23 --end_time_m 59 --test_mode yes

        # Check if the Docker container ran successfully
        if [ $? -eq 0 ]; then
            echo "Container ran successfully. and push to dockerhub"
            # docker tag ${IMAGE_NAME}:${IMAGE_TAG} tuzikexin/${IMAGE_NAME}:${IMAGE_TAG}
            # docker login
            docker push tuzikexin/${IMAGE_NAME}:${IMAGE_TAG}

            # Remove Dangling Images
            docker system prune -f
        else
            echo "Container encountered an error during execution."
            docker rm daily-vis-container
        fi
    fi
else
    echo "Docker image build failed."
fi
