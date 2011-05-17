#!/bin/bash

readonly ITEMS=(
  s/lib_database\.\(_?\)db_/lib_database.\\1/g
  s/db\.\(_?\)db_/db.\\1/g
  s/lib_bootstrap\.\(_?\)bootstrap_/lib_bootstrap.\\1/g
  s/lib_cache\.\(_?\)cache_/lib_cache.\\1/g
  s/lib_file\.\(_?\)file_/lib_file.\\1/g
  s/lib_language\.\(_?\)language_/lib_language.\\1/g
  s/lib_menu\.\(_?\)menu_/lib_menu.\\1/g
  s/lib_plugin\.\(_?\)plugin_/lib_plugin.\\1/g
  s/lib_session\.\(_?\)session_/lib_session.\\1/g
  s/lib_theme_maintenance\.\(_?\)theme_/lib_theme_maintenance.\\1/g
  s/lib_theme\.\(_?\)theme_/lib_theme.\\1/g
  s/lib_unicode\.\(_?\)unicode_/lib_unicode.\\1/g
)

for i in ${ITEMS[@]}; do
  #echo ${i}
  find . -type f -name "*.py" -exec sed -Ee "${i}" -i '' {} \;  
done;