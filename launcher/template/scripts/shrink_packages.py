from distutils.sysconfig import get_python_lib
from os import listdir, remove, path, rmdir as os_rmdir


def get_package_path(name): return path.join(get_python_lib(), name)


# https://stackoverflow.com/a/66605704/12245612
def rmdir(name):
    if not path.exists(name):
        print(name, "not exists")
        return
    for sub in listdir(name):
        sub = path.join(name, sub)
        if path.isdir(sub):
            rmdir(sub)
        elif path.isfile(sub):
            remove(sub)
    try:
        os_rmdir(name)
    except:
        pass


pg_path = get_package_path("pygame")
for subdir in ("docs", "examples", "tests"):
    rmdir(path.join(pg_path, subdir))

pggui_data = path.join(get_package_path("pygame_gui"), "data")
for fontfile in filter(lambda s: s.startswith("NotoSans"), listdir(pggui_data)):
    remove(path.join(pggui_data, fontfile))
