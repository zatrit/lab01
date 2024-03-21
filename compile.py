import os
import py_compile
from glob import glob
import shutil
import argparse
import py7zr

parser = argparse.ArgumentParser()
parser.add_argument("--scripts", action="store_true")
parser.add_argument("--dont-archive", action="store_false", dest="archive")

args = parser.parse_args()

BUILD_DIR = os.path.join("_build", "raw")
os.makedirs(BUILD_DIR, exist_ok=True)

sources = {s for s in glob("**/*.py", recursive=True)
           if not s.startswith(BUILD_DIR)}
blacklist = {"optimize_sprites.py", "generate_vignette.py", "compile.py"}
sources -= blacklist
sources -= {s for s in sources if s.startswith("launcher")}

SPACES = "                                       "

config = {}

if args.scripts:
    for src in sources:
        print("Compiling:", SPACES, src, end="\r")
        output = os.path.join(BUILD_DIR, src)
        module_dir = os.path.abspath(output + "/" + os.path.pardir)
        os.makedirs(module_dir, exist_ok=True)
        shutil.copy(src, output)
    config["main_file"] = "main.py"
else:
    for src in sources:
        print("Compiling:", src, SPACES, end="\r")
        output = os.path.join(BUILD_DIR, src + "c")
        py_compile.compile(src, output, optimize=2)
    config["main_file"] = "main.pyc"

print("Compiling: DONE", SPACES)

with open(os.path.join(BUILD_DIR, "launch.ini"), "w") as file:
    file.writelines(map("=".join, config.items()))

shutil.copytree("assets", os.path.join(
    BUILD_DIR, "assets"), dirs_exist_ok=True)
shutil.copy("requirements.txt", os.path.join(BUILD_DIR, "requirements.txt"))
shutil.copy("readme.md", os.path.join(BUILD_DIR, "readme.md"))

if args.archive:
    with py7zr.SevenZipFile("_build/lab01.7z", mode="w") as archive:
        for f in glob("**", root_dir=BUILD_DIR, recursive=True):
            print("Compressing:", f, SPACES, end="\r")
            archive.write(os.path.join(BUILD_DIR, f), f)
    print("Compressing: DONE", SPACES)
