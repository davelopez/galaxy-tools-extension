from typing import Callable, List

from .constants import _LAN, WHITESPACE_CHARS


class MultiLineStream:
    def __init__(self, source: str, position: int = 0) -> None:
        self._source = source
        self._position = position
        self._len = len(source)

    def eos(self) -> bool:
        return self._len <= self._position

    def get_source(self) -> str:
        return self._source

    def pos(self) -> int:
        return self._position

    def advance(self, n: int) -> None:
        self._position = self._position + n

    def go_to_end(self) -> None:
        self._position = self._len

    def peek_char(self, n: int = 0) -> int:
        try:
            return ord(self._source[self._position + n])
        except IndexError:
            return -1

    def advance_if_char(self, ch: int) -> bool:
        if ch == self.peek_char():
            self._position = self._position + 1
            return True
        return False

    def advance_if_chars(self, ch: List[int]) -> bool:
        if self._position + len(ch) > self._len:
            return False
        i = 0
        for i in range(len(ch)):
            if self._source[self._position + i] != chr(ch[i]):
                return False
        self.advance(i)
        return True

    def advance_until_char(self, ch: int) -> bool:
        while self._position < self._len:
            if ord(self._source[self._position]) == ch:
                return True
            self.advance(1)
        return False

    def advance_until_chars(self, ch: List[int]) -> bool:
        while self._position + len(ch) <= self._len:
            i = 0
            while i < len(ch) and self._source[self._position + i] == chr(ch[i]):
                i = i + 1
            if i == len(ch):
                return True
            self.advance(i or 1)
        self.go_to_end()
        return False

    def advance_while_char_in(self, list: List[int]) -> int:
        pos_now = self._position
        while self._position < self._len and ord(self._source[self._position]) in list:
            self._position = self._position + 1
        return self._position - pos_now

    def advance_until_char_or_new_tag(self, ch: int) -> bool:
        while self._position < self._len:
            if self.peek_char() == ch or self.peek_char() == _LAN:
                return True
            self.advance(1)
        return False

    def advance_until_chars_or_new_tag(self, ch: List[int]) -> bool:
        while self._position + len(ch) <= self._len:
            i = 0
            if self.peek_char() == _LAN:
                return True
            while i < len(ch) and self._source[self._position + i] == chr(ch[i]):
                i = i + 1
            if i == len(ch):
                return True
            self.advance(i or 1)
        self.go_to_end()
        return False

    def advance_while_char(self, predicate: Callable[[str], bool]) -> int:
        pos_now = self._position
        while self._position < self._len and predicate(self._source[self._position]):
            self._position = self._position + 1
        return self._position - pos_now

    def skip_whitespace(self) -> bool:
        n = self.advance_while_char_in(WHITESPACE_CHARS)
        return n > 0
