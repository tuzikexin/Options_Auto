#!/bin/bash

start_hour=21   # this the beijing time
start_minute=28
end_hour=4
end_minute=5

# Get the current hour and minute
current_hour=$(date +'%H')  # Current hour in 24-hour format
current_minute=$(date +'%M')  # Current minute

# Convert times to minutes for easier comparison
start_time_minutes=$((start_hour * 60 + start_minute))
end_time_minutes=$((end_hour * 60 + end_minute))
current_time_minutes=$((10#$current_hour * 60 + 10#$current_minute))  # Force base 10

# Check if the current time is within the desired range
if [ "$current_time_minutes" -ge "$start_time_minutes" ] && [ "$current_time_minutes" -le "$end_time_minutes" ]; then
    # echo "Current time is within the range."

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
            echo "restart the docker"
            docker run --rm -v $credentials_folder:/app/credentials/ --name daily-vis-container tuzikexin/option_auto_download:latest  --ticker VIX --end_time_h 16 --end_time_m 5 --test_mode no
        fi
    else 
        echo "docker is running"
    fi
fi
