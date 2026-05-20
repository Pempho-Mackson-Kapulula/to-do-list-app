@echo off
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe src\main.py
) else (
    py src\main.py
)