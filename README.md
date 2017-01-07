This script wraps any command in a notification with action buttons. To be more specific, depending on the result of 
`_should_run` function, it either just executes the command, or shows a prompt notification asking you whether it should be run now.

This is useful, for instance, if you got a cron job doing heavy network operations and you wanna make sure it wouldn't run on mobile network and waste all of your traffic.

# Requirements

* notification daemon, supporting actions
* pynotify2: `pip3 install "https://bitbucket.org/takluyver/pynotify2"`

# Configuration

Right now you should just add the names of allowed WiFi networks to `ALLOWED_NETWORKS`. I might add configuration file later.

# Using

Example:

    python3 notification_wrapper.py ls -al /bin