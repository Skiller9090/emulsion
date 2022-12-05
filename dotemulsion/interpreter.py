from .parser import DotEmulsionParser


def check_ex_in(tokens):
    for token in tokens:
        if token.include and token.exclude:
            raise Exception("Interpreter Error: You can't both include and exclude globs!")


class DotEmulsionInterpreter:
    def __init__(self, source):
        self._parser = DotEmulsionParser(source)
        self._parsed = False

    def _parse(self):
        while not self._parser.done:
            self._parser.step()
        self._parsed = True

    def evaluate(self):
        if not self._parsed:
            self._parse()
        if self._parser.failed:
            raise Exception("Error: Failed to parse!")
        tokens = self._parser.get_tokens()
        check_ex_in(tokens)
        return {
            x.name: x.to_dict() for x in tokens
        }
