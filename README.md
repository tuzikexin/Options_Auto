# Options index download Auto
 
This project aiming for use cloud VM run a docker image download yahoo vix data and uploda to google drive

### login to the cloud VM
-  https://orcaterm.cloud.tencent.com/

### download raw source code
~~~
git clone https://github.com/tuzikexin/Options_Auto.git
~~~

### loacal credentials for google drive
download the credentials json file from yaofugui google drive.
~~~
cd Options_Auto/app
mkdir credentials   # credentials.json upload to here
~~~
## option 1: Run with Python(Windows)
To run the script with the given arguments every day on a Windows machine, you can use the Windows Task Scheduler. Here’s a step-by-step guide to set this up:

### Step 1: Create a Batch File

First, create a batch file that will execute your Python script with the required arguments.

1. Open windown_python_daily_download.bat file.
2. Enter the following command, replacing the placeholders with your actual paths and arguments:

```batch
@echo off
cd "C:\path\to\your\script"
"C:\path\to\python\python.exe" opt_download.py --tickers VIX SPX --start_time_h 8 --start_time_m 55 --end_time_h 16 --end_time_m 5 --test_mode False
```

### Step 2: Schedule the Batch File with Task Scheduler

1. **Open Task Scheduler**:
   - Press `Win + R`, type `taskschd.msc`, and press Enter.

2. **Create a New Task**:
   - In the Task Scheduler, click on `Create Task...` in the right-hand Actions pane.

3. **General Settings**:
   - In the General tab, give your task a name (e.g., "Daily Options Data Download").
   - Optionally, provide a description.
   - Choose "Run whether user is logged on or not" to ensure the task runs even if you are not logged in.

4. **Set Triggers**:
   - Go to the Triggers tab and click `New...`.
   - Set the trigger to "Daily" and choose the start date and time for the first run.
   - Ensure the task is set to repeat every 1 day.
   - Click `OK` to save the trigger.

5. **Set Actions**:
   - Go to the Actions tab and click `New...`.
   - Set the action to "Start a program".
   - In the "Program/script" field, enter the path to your batch file (e.g., `C:\path\to\your\windows_python_daily_download.bat`).
   - Click `OK` to save the action.

6. **Set Conditions** (optional):
   - Go to the Conditions tab and set any conditions that should be met for the task to run, such as "Start the task only if the computer is on AC power".

7. **Set Settings**:
   - Go to the Settings tab and ensure "Allow task to be run on demand" is checked.
   - Optionally, check "Run task as soon as possible after a scheduled start is missed" to handle cases where the computer might be off at the scheduled time.
   - Click `OK` to save and finish creating the task.

8. **Enter Credentials**:
   - When prompted, enter your Windows username and password to allow the task to run with the necessary permissions.

### Step 3: Verify the Task

1. **Test the Task**:
   - In Task Scheduler, right-click your newly created task and select `Run`. This will test whether the task is set up correctly.

2. **Check Task History**:
   - After running, check the History tab of the task to ensure it ran successfully. Look for any errors that might need troubleshooting.

By following these steps, your script will run daily at the specified time, automatically starting and stopping based on your provided arguments. This setup ensures that the script is executed even if you are not logged into the machine, providing a reliable automation solution.


## option 2: Run with docker

### run as root user
~~~ 
sudo su - 
~~~

### (option) remove and build the image
    - cd Options_Auto/app
    - docker rmi -f tuzikexin/option_auto_download
    - bash build_docker.sh

### Pull the latest image 
~~~
bash pull_options_image.sh
~~~

### crontab(linux/mac) for daily job
~~~
crontab -e
~~~
~~~
# if the Docker container down, restart it
*/2 * * * 1-5 /home/lighthouse/Options_Auto/daily_restart_docker.sh >> /tmp/cron_test.log 2>&1

# Start the Docker container at NY 8:55 AM on weekdays
55 20 * * 1-5 /home/lighthouse/Options_Auto/daily_run_docker.sh >> /tmp/cron_test.log 2>&1

# Stop the Docker container at NY 16:05 PM on weekday
5 4 * * 1-5 /home/lighthouse/Options_Auto/daily_stop_docker.sh >> /tmp/cron_test.log 2&1
~~~
