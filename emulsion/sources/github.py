from .source import Source
from github import UnknownObjectException
from typing import TYPE_CHECKING
from emulsion.utils import download_file
import requests

if TYPE_CHECKING:
    from github.Repository import Repository


class GithubSource(Source):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repo: Repository = self._manager.github.get_repo(self._path)

    @property
    def type(self):
        return "GithubSource"

    @property
    def has_emulsion(self):
        try:
            self.repo.get_contents("init.emulsion")
            return True
        except UnknownObjectException:
            return False

    def ls(self, r_path, show_dirs=True):
        paths = map(lambda x: {"path": x.path, "type": x.type}, self.repo.get_contents(r_path))
        return iter(filter(lambda x: x["type"] == "file", paths)), iter(filter(lambda x: x["type"] == "dir", paths))

    def download(self, r_path, l_path, verbose=True):
        if verbose:
            print(f"Downloading file: {r_path}")
        download_file(self.repo.get_contents(r_path).download_url, l_path, verbose=True)

    def load_content(self, r_path):
        content = self.repo.get_contents(r_path).decoded_content.decode()
        return content

    def get_content_stream(self, r_path, chunk_size=2048):
        return requests.get(
            self.repo.get_contents(r_path).download_url,
            stream=True,
            headers={"Accept-Encoding": "identity"}
        ).iter_content(chunk_size=chunk_size, decode_unicode=True)

    def resource_name(self):
        return self.repo.name
