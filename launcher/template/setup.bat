@echo off

setlocal
path %cd%\tinygit;%cd%\python

cd scripts

python.exe -v bootstrap_pip.py

python.exe -v -m pip install -r ..\{app_dir}\requirements.txt

python.exe -v shrink_packages.py

python.exe -v -m pip uninstall -y pip setuptools wheel

cd ..
pause