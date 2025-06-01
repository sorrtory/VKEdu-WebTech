#!/bin/bash
# This script is used by cron job to update the cache of backend.

set -a
source /home/app/web/.env && /usr/local/bin/python /home/app/web/manage.py update_cache
source /home/app/web/.env && /usr/local/bin/python /home/app/web/manage.py send_notification "Cache is updated. Reload the page to see the changes."