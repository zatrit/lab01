@echo off

setlocal
path %cd%\python

cd {app_dir}

set main_file=main.py
for /F "tokens=*" %%I in (launch.ini) do set %%I

python.exe -v %main_file%

cd ..
