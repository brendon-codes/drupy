#!/bin/bash

#
# BACKUP DB
# Brendon Crawford
#

readonly CONF_DB_HOST="localhost"
readonly CONF_DB_USER="main"
readonly CONF_DB_PASS=""
readonly CONF_DB_NAME="drupalhead"
readonly CONF_OUTFILE="$(date +%Y-%m-%d-%H%M%S).sql.gz"

echo "Dumping DB..."

mysqldump \
  --add-drop-table \
  --add-locks \
  --complete-insert \
  --extended-insert \
  --host="${CONF_DB_HOST}" \
  --user="${CONF_DB_USER}" \
  --password="${CONF_DB_PASS}" \
  "${CONF_DB_NAME}" |\
    gzip -9 > "${CONF_OUTFILE}"

echo "Finished."

