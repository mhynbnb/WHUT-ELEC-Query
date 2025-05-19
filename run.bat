@echo off
if exist config.json (
    start /min pythonw main.py
) else (
    python main.py
)
