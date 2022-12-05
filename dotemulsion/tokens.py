from enum import Enum


class TokenType(Enum):
    DEFAULT = 0
    RUN = 1


class Token:
    TYPE = TokenType.DEFAULT


class RunToken(Token):
    TYPE = TokenType.RUN

    def __init__(self, name):
        self.name = name
        self.include = []
        self.exclude = []
        self.settings = {}
        self.pre_deps = []
        self.post_deps = []
        self.runs = []

    def add_attrib_token(self, attrib, string):
        {
            "include": self.include,
            "exclude": self.exclude,
            "pre_deps": self.pre_deps,
            "post_deps": self.post_deps
        }[attrib].append(string)

    def __str__(self):
        return f"""\nRun Token[{self.name}]:
        \tIncludes : {self.include}
        \tExcludes : {self.exclude}
        \tSettings : {self.settings}
        \tPre Deps : {self.pre_deps}
        \tPost Deps: {self.post_deps}
        \tRuns     : {self.runs}\n"""

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {
            "name": self.name,
            "include": self.include,
            "exclude": self.exclude,
            "settings": self.settings,
            "pre_deps": self.pre_deps,
            "post_deps": self.post_deps,
            "runs": self.runs
        }
