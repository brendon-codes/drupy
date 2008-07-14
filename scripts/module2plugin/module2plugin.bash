#!/bin/bash

find drupy/base -type f -name "*.py" -exec sed -i '' 's/module/plugin/g' {} \;