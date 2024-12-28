#!/usr/bin/env bash

cd "$REPO_PATH/portfolio" || exit
.venv/bin/python portfolio/main.py "$@"

if [ $? != 0 ]; then
    .venv/bin/python portfolio/main.py retry
fi
.venv/bin/python portfolio/backup_db.py
