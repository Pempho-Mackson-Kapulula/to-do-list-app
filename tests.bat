@echo off
set PYTHONPATH=%CD%

echo Running All Project Unit Tests...
python -m unittest discover -s tests -p "test_*.py" -v
