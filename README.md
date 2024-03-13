### Options Auto
 
This project aiming for use cloud VM run a docker image download yahoo vix data and uploda to google drive

### 
1. login in the cloud VM https://orcaterm.cloud.tencent.com/
~~~ 
# run as root user
sudo su -

# download raw source 
git clone https://github.com/tuzikexin/Options_Auto.git

# (option) remove and build the image
    - cd Options_Auto/app
    - docker rmi -f tuzikexin/option_auto_download
    - bash build_docker.sh

# Pull the image 
bash pull_options_image.sh

# use the loacal credentials for google drive
cd Options_Auto
mkdir credentials  # credentials.json upload to here

# crontab for daily job
crontab -e
    # if the Docker container down, restart it
    */5 * * * 1-5 raw_source_path/daily_restart_docker.sh >> /tmp/cron_test.log 2>&1
    
    # Start the Docker container at NY 8:55 AM on weekdays
    55 20 * * 1-5 raw_source_path/daily_run_docker.sh >> /tmp/cron_test.log 2>&1

    # Stop the Docker container at NY 16:05 PM on weekdays
    5 4 * * 1-5 raw_source_path/daily_stop_docker.sh >> /tmp/cron_test.log 2>&1
~~~
