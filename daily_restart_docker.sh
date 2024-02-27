#!/bin/bash

# Get the current hour
current_hour=$(date +%H)

# Define the start and end time
start_time=15
end_time=23

# Check if the current time is within the desired range
if [ "$current_hour" -ge "$start_time" ] && [ "$current_hour" -le "$end_time" ]; then
    echo "Current time is within the range."

    # Check if the "option_download" container is running
    if ! docker ps | grep -q "daily-vis-container"; then
        echo "The 'daily-vis-container' container is not running. Starting a new container from tuzikexin/option_auto_download:latest."

        # Run the Docker container 
        # Get the credentials directory
        current_dir=$(pwd)
        credentials_f="credentials"
        credentials_folder="$current_dir/$credentials_f"
        if [ $(ls -A $credentials_folder | wc -l) -eq 0 ]; then
            echo "credentials directory is empty."
        else
            docker run --rm -v $credentials_folder:/app/credentials/ --name daily-vis-container tuzikexin/${IMAGE_NAME}:${IMAGE_TAG}  --ticker VIX --end_time_h 22 --end_time_m 45 --test_mode no
        fi
    fi
fi
