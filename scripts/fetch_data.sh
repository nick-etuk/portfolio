#!/usr/bin/env bash

cd "$REPO_PATH/portfolio" || exit
.venv/bin/python main.py "$@"

if [ $? != 0 ]; then
    .venv/bin/python main.py retry
fi
.venv/bin/python backup_db.py
