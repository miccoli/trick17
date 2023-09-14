#!/bin/sh
systemd-run --user --wait --service-type=notify -d -E PYTHONPATH=src tests/tnotify.py
