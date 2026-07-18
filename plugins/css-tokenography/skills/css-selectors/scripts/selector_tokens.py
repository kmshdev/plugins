"""Balanced tokenization for the specificity calculator's selector subset."""

from __future__ import annotations

from dataclasses import dataclass


class SelectorSyntaxError(ValueError):
    """Raised when a selector cannot be tokenized or parsed safely."""


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    start: int
    end: int


_PUNCTUATION = {
    ".": "DOT",
    ":": "COLON",
    "[": "LBRACKET",
    "]": "RBRACKET",
    "(": "LPAREN",
    ")": "RPAREN",
    ",": "COMMA",
    "*": "STAR",
    "|": "PIPE",
}


def _is_name_start(character: str) -> bool:
    return character == "_" or character.isalpha() or ord(character) >= 0x80


def _is_name(character: str) -> bool:
    return _is_name_start(character) or character.isdigit() or character == "-"


def _consume_escape(source: str, index: int) -> int:
    if index + 1 >= len(source) or source[index + 1] in "\n\r\f":
        raise SelectorSyntaxError(f"Invalid escape at offset {index}")
    index += 1
    if source[index] in "0123456789abcdefABCDEF":
        consumed = 0
        while index < len(source) and consumed < 6 and source[index] in "0123456789abcdefABCDEF":
            index += 1
            consumed += 1
        if index < len(source) and source[index].isspace():
            index += 1
        return index
    return index + 1


def _starts_identifier(source: str, index: int) -> bool:
    if index >= len(source):
        return False
    character = source[index]
    if _is_name_start(character) or character == "\\":
        return True
    if character != "-" or index + 1 >= len(source):
        return False
    following = source[index + 1]
    return _is_name_start(following) or following in {"-", "\\"}


def _consume_name(source: str, index: int) -> int:
    while index < len(source):
        character = source[index]
        if _is_name(character):
            index += 1
        elif character == "\\":
            index = _consume_escape(source, index)
        else:
            break
    return index


def tokenize_selector(source: str) -> list[Token]:
    """Tokenize selector syntax while validating strings, comments, and delimiters."""

    tokens: list[Token] = []
    stack: list[tuple[str, int]] = []
    index = 0
    while index < len(source):
        start = index
        character = source[index]

        if character.isspace():
            index += 1
            while index < len(source) and source[index].isspace():
                index += 1
            tokens.append(Token("WHITESPACE", source[start:index], start, index))
            continue

        if source.startswith("/*", index):
            close = source.find("*/", index + 2)
            if close < 0:
                raise SelectorSyntaxError(f"Unterminated comment at offset {start}")
            index = close + 2
            tokens.append(Token("COMMENT", source[start:index], start, index))
            continue

        if character in {'"', "'"}:
            quote = character
            index += 1
            while index < len(source) and source[index] != quote:
                if source[index] in "\n\r\f":
                    raise SelectorSyntaxError(f"Unterminated string at offset {start}")
                if source[index] == "\\":
                    index = _consume_escape(source, index)
                else:
                    index += 1
            if index >= len(source):
                raise SelectorSyntaxError(f"Unterminated string at offset {start}")
            index += 1
            tokens.append(Token("STRING", source[start:index], start, index))
            continue

        if character == "#" and index + 1 < len(source) and (
            _is_name(source[index + 1]) or source[index + 1] == "\\"
        ):
            index = _consume_name(source, index + 1)
            tokens.append(Token("HASH", source[start:index], start, index))
            continue

        if _starts_identifier(source, index):
            index = _consume_name(source, index)
            tokens.append(Token("IDENT", source[start:index], start, index))
            continue

        if source.startswith("::", index):
            index += 2
            tokens.append(Token("DOUBLE_COLON", "::", start, index))
            continue
        if source.startswith("||", index):
            index += 2
            tokens.append(Token("COMBINATOR", "||", start, index))
            continue
        if character in ">+~":
            index += 1
            tokens.append(Token("COMBINATOR", character, start, index))
            continue
        if character in _PUNCTUATION:
            index += 1
            kind = _PUNCTUATION[character]
            if kind in {"LBRACKET", "LPAREN"}:
                stack.append((kind, start))
            elif kind in {"RBRACKET", "RPAREN"}:
                expected = "LBRACKET" if kind == "RBRACKET" else "LPAREN"
                if not stack or stack[-1][0] != expected:
                    raise SelectorSyntaxError(f"Unexpected {character!r} at offset {start}")
                stack.pop()
            tokens.append(Token(kind, character, start, index))
            continue

        index += 1
        tokens.append(Token("DELIM", character, start, index))

    if stack:
        kind, start = stack[-1]
        delimiter = "[" if kind == "LBRACKET" else "("
        raise SelectorSyntaxError(f"Unclosed {delimiter!r} at offset {start}")
    return tokens


def unescape_identifier(value: str) -> str:
    """Decode CSS escapes sufficiently for case-insensitive pseudo-class names."""

    output: list[str] = []
    index = 0
    while index < len(value):
        if value[index] != "\\":
            output.append(value[index])
            index += 1
            continue
        index += 1
        start = index
        while index < len(value) and index - start < 6 and value[index] in "0123456789abcdefABCDEF":
            index += 1
        if index > start:
            codepoint = int(value[start:index], 16)
            output.append(chr(codepoint) if codepoint and codepoint <= 0x10FFFF else "\N{REPLACEMENT CHARACTER}")
            if index < len(value) and value[index].isspace():
                index += 1
        elif index < len(value):
            output.append(value[index])
            index += 1
    return "".join(output)
