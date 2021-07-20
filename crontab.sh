
SHELL=/bin/bash
APP_ROOT=/app
RUN="/usr/bin/python3 $APP_ROOT/run.py"

# Run uptime monitor every five minutes
*/5 * * * *      $RUN https_uptime_monitor
*/5 * * * *      $RUN smtp_uptime_monitor

# Backup websites every Sunday
00 09 * * sun    $RUN backup_wordpress
00 10 * * sun    $RUN backup_drupal
00 11 * * sun    $RUN backup_mysql

# Run DNS monitor daily
00 12 * * *      $RUN dns_monitor

# Send status report to sysadmin every Monday at 9:00
00 09 * * mon    $RUN status_report
