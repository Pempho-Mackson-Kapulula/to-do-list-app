@echo off
set PYTHONPATH=%CD%\src

echo Running All Project Unit Tests...
py -m unittest discover -s tests -p "test_*.py" -v
