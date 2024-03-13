#!/bin/bash

# Function to convert time to minutes since midnight
time_to_minutes() {
    hour=$(echo $1 | cut -d: -f1)
    minute=$(echo $1 | cut -d: -f2)
    echo $((hour * 60 + minute))
}

# Get current time and date
current_time=$(date +%H:%M)
current_minutes=$(time_to_minutes $current_time)

# Define time range
start_time="20:55"  # this is beijing time 
end_time="04:03"

# Convert range to minutes since midnight
start_minutes=$(time_to_minutes $start_time)
end_minutes=$(time_to_minutes $end_time)

# Adjust for range that crosses midnight
if [[ $current_minutes -lt $end_minutes ]]; then
    current_minutes=$((current_minutes + 1440)) # Add 24 hours in minutes
fi

# Check if current time is within the range
if [[ $current_minutes -ge $start_minutes ]] || [[ $current_minutes -lt $((end_minutes + 1440)) ]]; then

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
    fi
fi
