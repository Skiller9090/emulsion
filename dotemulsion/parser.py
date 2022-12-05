from enum import Enum
from .tokens import RunToken
import string


class ParserStates(Enum):
    FAILED = -1
    INIT = 0
    RUN_NAME = 1
    RUN = 2
    ATTRIB_EXCLUDE = 3
    ATTRIB_INCLUDE = 4
    ATTRIB_SETTINGS = 5
    ATTRIB_SETTING_VALUE = 5.5
    ATTRIB_PRE_DEPS = 6
    ATTRIB_POST_DEPS = 7
    ATTRIB_RUN = 8
    DONE = 99


class DotEmulsionParser:
    def __init__(self, source):
        self._source = source if hasattr(source, "__next__") else iter(source)
        self._state = ParserStates.INIT
        self._c_token = None
        self._s_meta = {}
        self._buffer = []
        self._tokens = []
        self._STATE_MAP = {
            ParserStates.FAILED: self.fail_state,
            ParserStates.INIT: self.init_state,
            ParserStates.RUN_NAME: self.run_name_state,
            ParserStates.RUN: self.run_state,
            ParserStates.ATTRIB_EXCLUDE: lambda sym: self._string_list_state(sym, attrib="exclude"),
            ParserStates.ATTRIB_INCLUDE: lambda sym: self._string_list_state(sym, attrib="include"),
            ParserStates.ATTRIB_PRE_DEPS: lambda sym: self._string_list_state(sym, attrib="pre_deps"),
            ParserStates.ATTRIB_POST_DEPS: lambda sym: self._string_list_state(sym, attrib="post_deps"),
            ParserStates.ATTRIB_SETTINGS: self.settings_state,
            ParserStates.ATTRIB_SETTING_VALUE: self.settings_value_state,
            ParserStates.ATTRIB_RUN: self.runs_state,
            ParserStates.DONE: lambda _: None
        }

    @property
    def done(self):
        return self._state in [ParserStates.FAILED, ParserStates.DONE]

    @property
    def failed(self):
        return self._state is ParserStates.FAILED

    def step(self):
        sym = None
        try:
            sym = next(self._source)
        except StopIteration:
            if self._state is ParserStates.INIT:
                self._state = ParserStates.DONE
            else:
                self._state = ParserStates.FAILED
        if self.failed:
            return
        self._STATE_MAP.get(self._state, self.fail_state)(sym)

    def init_state(self, sym):
        if sym in string.ascii_letters:
            self._state = ParserStates.RUN_NAME
            self._buffer.append(sym)

    def fail_state(self, _):
        self._state = ParserStates.FAILED
        print("Failed State")

    def run_name_state(self, sym):
        if sym in string.ascii_letters:
            self._buffer.append(sym)
        elif sym == "{":
            self._c_token = RunToken("".join(self._buffer))
            self._buffer.clear()
            self._state = ParserStates.RUN
        elif sym in string.whitespace:
            pass
        else:
            self._state = ParserStates.FAILED
            raise Exception(f"Error: Did not expect '{sym}' character here!")

    def run_state(self, sym):
        if sym in string.ascii_letters + "-_+@~#<>.?/*&^%$£!":
            self._buffer.append(sym)
        elif sym == "{":
            attrib_name = "".join(self._buffer)
            self._buffer.clear()
            state_mapping = {
                "exclude": ParserStates.ATTRIB_EXCLUDE,
                "include": ParserStates.ATTRIB_INCLUDE,
                "settings": ParserStates.ATTRIB_SETTINGS,
                "pre-deps": ParserStates.ATTRIB_PRE_DEPS,
                "post-deps": ParserStates.ATTRIB_POST_DEPS,
                "run": ParserStates.ATTRIB_RUN
            }
            next_state = state_mapping.get(attrib_name, None)
            if next_state is None:
                self._state = ParserStates.FAILED
                raise Exception(f"Error: Attribute '{attrib_name}' does not exist for run object!")
            else:
                self._state = next_state
        elif sym in string.whitespace:
            pass
        elif sym == "}":
            self.emit_token()
            self._state = ParserStates.INIT
        else:
            self._state = ParserStates.FAILED
            raise Exception(f"Error: Did not expect '{sym}' character here!")

    def _string_list_state(self, sym, attrib=None):
        if sym in "\"'":
            if not self._s_meta.get("in_string", False):
                self._s_meta["in_string"] = True
                self._s_meta["open_char"] = sym
            else:
                if self._s_meta["open_char"] == sym:
                    self._s_meta.clear()
                    self._c_token.add_attrib_token(attrib, "".join(self._buffer))
                    self._buffer.clear()
                else:
                    self._buffer.append(sym)
        else:
            if self._s_meta.get("in_string", False):
                self._buffer.append(sym)
            elif sym in string.whitespace + ";,":
                pass
            elif sym == "}":
                self._buffer.clear()
                self._s_meta.clear()
                self._state = ParserStates.RUN
            else:
                self._state = ParserStates.FAILED
                raise Exception(f"Error: Did not expect '{sym}' character here!")

    def settings_state(self, sym):
        if sym in string.ascii_letters + "+-_~[]#@/?.*&^%$£!":
            self._buffer.append(sym)
        elif sym == ":":
            self._s_meta["setting_name"] = "".join(self._buffer)
            self._buffer.clear()
            self._state = ParserStates.ATTRIB_SETTING_VALUE
        elif sym in string.whitespace:
            pass
        else:
            self._state = ParserStates.FAILED
            raise Exception(f"Error: Did not expect '{sym}' character here!")

    def settings_value_state(self, sym):
        if self._s_meta.get("in_string", False):
            if sym == self._s_meta["open_char"]:
                self._c_token.settings[self._s_meta["setting_name"]] = "".join(self._buffer)
                self._s_meta.clear()
                self._buffer.clear()
            else:
                self._buffer.append(sym)
        else:
            if sym == ",":
                self._c_token.settings[self._s_meta["setting_name"]] = "".join(self._buffer)
                self._buffer.clear()
                self._state = ParserStates.ATTRIB_SETTINGS
            elif sym == "}":
                self._c_token.settings[self._s_meta["setting_name"]] = "".join(self._buffer)
                self._buffer.clear()
                self._state = ParserStates.RUN
            elif sym in string.ascii_letters + "-[]@~#?/<>.*&^%$£!()":
                self._buffer.append(sym)
            elif sym in "\"'":
                if self._buffer:
                    self._state = ParserStates.FAILED
                    raise Exception("Error: Settings values which are strings should not have any other value "
                                    "prefixing!")
                self._s_meta["in_string"] = True
                self._s_meta["open_char"] = sym
            elif sym in string.whitespace:
                pass
            else:
                self._state = ParserStates.FAILED
                raise Exception(f"Error: Did not expect '{sym}' character here!")

    def runs_state(self, sym):
        if sym in string.ascii_letters + "-_+@~#<>.?/*&^%$£!":
            self._buffer.append(sym)
        elif sym == ",":
            self._c_token.runs.append("".join(self._buffer))
            self._buffer.clear()
        elif sym == "}":
            self._c_token.runs.append("".join(self._buffer))
            self._buffer.clear()
            self._state = ParserStates.RUN
        elif sym in string.whitespace:
            pass
        else:
            self._state = ParserStates.FAILED
            raise Exception(f"Error: Did not expect '{sym}' character here!")

    def emit_token(self):
        self._tokens.append(self._c_token)
        self._c_token = None

    def get_tokens(self):
        return self._tokens
