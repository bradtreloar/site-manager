
SHELL=/bin/bash
APP_ROOT=/app
RUN="/usr/bin/python3 $APP_ROOT/run.py"

# Run status monitor every five minutes
*/5 * * * *      $RUN update_https_status
*/5 * * * *      $RUN update_ssh_status

# Send status report to sysadmin every Monday at 9:00
00 09 * * mon    $RUN send_status_report

# Backup websites every Sunday
00 09 * * sun    $RUN backup_wordpress
00 10 * * sun    $RUN backup_drupal
00 11 * * sun    $RUN backup_mysql

# Run DNS monitor daily
00 12 * * *      $RUN dns_monitor
