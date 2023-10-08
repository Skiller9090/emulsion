import requests
from github import UnknownObjectException, BadCredentialsException
from .manager import Manager
from pathlib import Path

manager = Manager.get()

def auth_error_handler(func):
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except BadCredentialsException:
            print("You credential is either incorrect or expires. Please enter an active PAT and retry!")
            retrieve_PAT()

    return inner_function


def gh_file_exists(repo, path):
    try:
        repo.get_contents(path)
        return True
    except UnknownObjectException as _:
        return False


def progress_bar(progress, total):
    percent = 100 * (progress / total)
    percent_int = round(percent/2)
    bar = '▇' * percent_int + "-" * (50 - percent_int)
    print(f"\r|{bar}| {percent:.2f}% ({progress}/{total} Kb)", end="\r")


def download_file(url, save_path, verbose=False, chunk_size=8196):
    path = Path(save_path)
    path.parent.mkdir(exist_ok=True)
    with requests.get(url, stream=True, headers={"Accept-Encoding": "identity"}) as r:
        r.raise_for_status()
        total = round(int(r.headers.get('content-length', 0)) / 1024, 2)
        downloaded = 0
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                if verbose:
                    cs = chunk_size/1024
                    if cs + downloaded > total:
                        downloaded = total
                    else:
                        downloaded += cs
                    progress_bar(round(downloaded, 2), total)
    print()
    return True


def retrieve_PAT():
    _token = input("Enter PAT: ")
    manager.config.save_token(_token)
