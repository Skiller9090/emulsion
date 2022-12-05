from abc import ABC, abstractmethod


class Source(ABC):
    def __init__(self, manager, path):
        self._path = path
        self._manager = manager

    @property
    @abstractmethod
    def type(self):
        return "AbstractSource"

    @property
    @abstractmethod
    def has_emulsion(self):
        pass

    @abstractmethod
    def ls(self, r_path, show_dirs=True):
        pass

    @abstractmethod
    def download(self, r_path, l_path, verbose=True):
        pass

    @abstractmethod
    def load_content(self, r_path):
        pass

    @abstractmethod
    def get_content_stream(self, r_path, chunk_size=2048):
        pass

    @abstractmethod
    def resource_name(self):
        pass
