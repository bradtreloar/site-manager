
SHELL=/bin/bash

# Run status monitor every five minutes
*/5 * * * *      cd /home/ubuntu/site-manager && /usr/bin/python3 run.py update_https_status

# Send status report to sysadmin every Monday at 9:00
00 09 * * mon    cd /home/ubuntu/site-manager && /usr/bin/python3 run.py send_status_report

# Backup websites every Sunday
00 09 * * sun    cd /home/ubuntu/site-manager && /usr/bin/python3 run.py backup_wordpress
00 10 * * sun    cd /home/ubuntu/site-manager && /usr/bin/python3 run.py backup_drupal
