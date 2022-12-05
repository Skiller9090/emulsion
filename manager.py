from configurations import Configurations
from github import Github


class Manager:
    INSTANCE = None

    @classmethod
    def get(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = cls()
        return cls.INSTANCE

    def __init__(self):
        if self.INSTANCE is not None:
            raise Exception("Manager already defined!")
        self.config = Configurations()
        self.github = None

    def login(self):
        self.github = Github(login_or_token=self.config.get_token(), verify=True)
