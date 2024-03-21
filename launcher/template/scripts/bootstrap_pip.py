from urllib import request
import importlib.util

if not importlib.util.find_spec("pip"):
    get_pip_url = 'https://bootstrap.pypa.io/get-pip.py'
    with open('get_pip.py', 'w') as local, request.urlopen(get_pip_url) as remote:
        for line in remote:
            local.write(line.decode('utf8'))

    import get_pip # type: ignore

    get_pip.main()