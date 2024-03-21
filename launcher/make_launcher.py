from io import BytesIO
import py_compile
from os import path, makedirs, remove
from glob import iglob
import shutil
import tomllib
from urllib import request
import zipfile

with open('config.toml', 'rb') as file:
    config = tomllib.load(file)
out_dir = config['out_dir']
python_dir = path.join(out_dir, 'python')
tinygit_dir = path.join(out_dir, 'tinygit')
python_std = config['python_std']
std_dir = path.join(python_dir, python_std)

for _dir in [path.join(out_dir, config['app_dir']), tinygit_dir, python_dir, std_dir]:
    makedirs(_dir, exist_ok=True)

python_url = config['python_url']
print('Downloading:', python_url)
with request.urlopen(python_url) as remote, zipfile.PyZipFile(BytesIO(remote.read())) as python:
    python.extractall(python_dir)

tinygit_bin = path.join(tinygit_dir, 'git.exe')
tinygit_url = config['tinygit_url']
print('Downloading:', tinygit_url)
with request.urlopen(tinygit_url) as remote, open(tinygit_bin, 'wb') as tinygit:
    tinygit.write(remote.read())

std_file = std_dir + '.zip'
print('Extecting Python standard library')
with open(std_file, 'rb') as file, zipfile.PyZipFile(file) as std:
	std.extractall(std_dir)
remove(std_file)

path_file = path.join(python_dir, python_std + '._pth')
print('Writing path file:', path_file)
with open(path_file, 'w') as outfile, open('path.pth', 'r') as infile:
     outfile.write(str.format(infile.read(), **config))

print('Copying files')
for file in iglob('**/*', recursive=True, root_dir='template'):
    src = path.join('template', file)
    if path.isdir(src):
        continue
    dest = path.join(out_dir, file)
    makedirs(path.dirname(dest), exist_ok=True)

    with open(src, 'r') as f, open(dest, 'w') as out:
        out.write(f.read().format(**config))