#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# สร้างฐานข้อมูลและ migrate
flask db upgrade
