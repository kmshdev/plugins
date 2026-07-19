"""A bounded selector AST and Selectors Level 4 specificity fold."""

from __future__ import annotations

import re
from dataclasses import dataclass

from selector_tokens import SelectorSyntaxError, Token, unescape_identifier


@dataclass(frozen=True, order=True)
class Specificity:
    a: int = 0
    b: int = 0
    c: int = 0

    def __add__(self, other: "Specificity") -> "Specificity":
        return Specificity(self.a + other.a, self.b + other.b, self.c + other.c)

    def as_list(self) -> list[int]:
        return [self.a, self.b, self.c]


@dataclass(frozen=True)
class SimpleSelector:
    kind: str
    name: str = ""
    arguments: tuple["Selector", ...] = ()


@dataclass(frozen=True)
class Selector:
    selector: str
    simple_selectors: tuple[SimpleSelector, ...]
    start: int
    end: int


@dataclass(frozen=True)
class SelectorResult:
    selector: str
    specificity: Specificity
    start: int
    end: int
    notes: tuple[str, ...]


_IGNORED = {"WHITESPACE", "COMMENT"}
_LEGACY_PSEUDO_ELEMENTS = {"after", "before", "first-letter", "first-line"}
_MATCHES_SPECIFICITY = {"is", "not", "has"}
_NTH_PSEUDO_CLASSES = {"nth-child", "nth-last-child"}


def _significant(tokens: list[Token]) -> list[Token]:
    return [token for token in tokens if token.kind not in _IGNORED]


def _trim(tokens: list[Token]) -> list[Token]:
    start = 0
    end = len(tokens)
    while start < end and tokens[start].kind in _IGNORED:
        start += 1
    while end > start and tokens[end - 1].kind in _IGNORED:
        end -= 1
    return tokens[start:end]


def _split_top_level(tokens: list[Token]) -> list[list[Token]]:
    members: list[list[Token]] = []
    depth = 0
    start = 0
    for index, token in enumerate(tokens):
        if token.kind in {"LPAREN", "LBRACKET"}:
            depth += 1
        elif token.kind in {"RPAREN", "RBRACKET"}:
            depth -= 1
        elif token.kind == "COMMA" and depth == 0:
            members.append(tokens[start:index])
            start = index + 1
    members.append(tokens[start:])
    return members


def _matching_index(tokens: list[Token], opening: int) -> int:
    opening_kind = tokens[opening].kind
    closing_kind = "RPAREN" if opening_kind == "LPAREN" else "RBRACKET"
    depth = 0
    for index in range(opening, len(tokens)):
        if tokens[index].kind == opening_kind:
            depth += 1
        elif tokens[index].kind == closing_kind:
            depth -= 1
            if depth == 0:
                return index
    raise SelectorSyntaxError(f"Unclosed delimiter at offset {tokens[opening].start}")


def _nth_selector_arguments(tokens: list[Token], pseudo_name: str) -> tuple[Selector, ...]:
    depth = 0
    of_index: int | None = None
    for index, token in enumerate(tokens):
        if token.kind in {"LPAREN", "LBRACKET"}:
            depth += 1
        elif token.kind in {"RPAREN", "RBRACKET"}:
            depth -= 1
        elif (
            depth == 0
            and token.kind == "IDENT"
            and unescape_identifier(token.value).lower() == "of"
        ):
            of_index = index
            break
    anb_tokens = tokens if of_index is None else tokens[:of_index]
    anb_parts: list[str] = []
    previous: Token | None = None
    for token in anb_tokens:
        if token.kind == "COMMENT":
            continue
        if previous is not None and token.start > previous.end:
            anb_parts.append(" ")
        anb_parts.append(token.value)
        previous = token
    anb = "".join(anb_parts).strip()
    if not re.fullmatch(
        r"(?:odd|even|[+-]?\d+|[+-]?(?:\d+)?n(?:\s*[+-]\s*\d+)?)",
        anb,
        re.IGNORECASE,
    ):
        raise SelectorSyntaxError(f":{pseudo_name}() requires a valid An+B expression")
    if of_index is None:
        return ()
    selectors = tokens[of_index + 1 :]
    if not _significant(selectors):
        raise SelectorSyntaxError(f":{pseudo_name}() requires a selector list after 'of'")
    return tuple(parse_selector_list(selectors))


def _parse_member(tokens: list[Token], *, allow_relative: bool) -> Selector:
    trimmed = _trim(tokens)
    if not trimmed:
        raise SelectorSyntaxError("Selector lists cannot contain an empty member")
    significant = _significant(trimmed)
    if not significant:
        raise SelectorSyntaxError("Selector lists cannot contain an empty member")

    nodes: list[SimpleSelector] = []
    index = 0
    last_was_combinator = False
    while index < len(significant):
        token = significant[index]

        if token.kind == "COMBINATOR":
            if (index == 0 and not allow_relative) or last_was_combinator or index == len(significant) - 1:
                raise SelectorSyntaxError(f"Unexpected combinator at offset {token.start}")
            last_was_combinator = True
            index += 1
            continue
        last_was_combinator = False

        if token.kind == "HASH":
            nodes.append(SimpleSelector("id", token.value[1:]))
            index += 1
            continue

        if token.kind == "DOT":
            if index + 1 >= len(significant) or significant[index + 1].kind != "IDENT":
                raise SelectorSyntaxError(f"Class selector at offset {token.start} requires an identifier")
            nodes.append(SimpleSelector("class", significant[index + 1].value))
            index += 2
            continue

        if token.kind == "LBRACKET":
            close = _matching_index(significant, index)
            if not _significant(significant[index + 1 : close]):
                raise SelectorSyntaxError(f"Empty attribute selector at offset {token.start}")
            nodes.append(SimpleSelector("attribute"))
            index = close + 1
            continue

        if token.kind in {"COLON", "DOUBLE_COLON"}:
            if index + 1 >= len(significant) or significant[index + 1].kind != "IDENT":
                raise SelectorSyntaxError(f"Pseudo selector at offset {token.start} requires a name")
            name_token = significant[index + 1]
            name = unescape_identifier(name_token.value).lower()
            is_element = token.kind == "DOUBLE_COLON" or name in _LEGACY_PSEUDO_ELEMENTS
            function_open = index + 2
            if (
                function_open < len(significant)
                and significant[function_open].kind == "LPAREN"
                and name_token.end == significant[function_open].start
            ):
                close = _matching_index(significant, function_open)
                arguments = significant[function_open + 1 : close]
                if is_element:
                    nodes.append(SimpleSelector("pseudo-element", name))
                elif name == "where":
                    if not arguments:
                        raise SelectorSyntaxError(":where() requires a selector list")
                    nodes.append(SimpleSelector("where", name, tuple(parse_selector_list(arguments))))
                elif name in _MATCHES_SPECIFICITY:
                    if not arguments:
                        raise SelectorSyntaxError(f":{name}() requires a selector list")
                    nodes.append(
                        SimpleSelector(
                            "matches",
                            name,
                            tuple(parse_selector_list(arguments, allow_relative=name == "has")),
                        )
                    )
                elif name in _NTH_PSEUDO_CLASSES:
                    nodes.append(SimpleSelector("nth", name, _nth_selector_arguments(arguments, name)))
                else:
                    nodes.append(SimpleSelector("pseudo-class", name))
                index = close + 1
            else:
                nodes.append(SimpleSelector("pseudo-element" if is_element else "pseudo-class", name))
                index += 2
            continue

        if token.kind in {"IDENT", "STAR"}:
            if index + 1 < len(significant) and significant[index + 1].kind == "PIPE":
                if index + 2 >= len(significant) or significant[index + 2].kind not in {"IDENT", "STAR"}:
                    raise SelectorSyntaxError(f"Namespace separator at offset {significant[index + 1].start} requires a type")
                local = significant[index + 2]
                if local.kind == "IDENT":
                    nodes.append(SimpleSelector("type", local.value))
                index += 3
            else:
                if token.kind == "IDENT":
                    nodes.append(SimpleSelector("type", token.value))
                index += 1
            continue

        if token.kind == "PIPE":
            if index + 1 >= len(significant) or significant[index + 1].kind not in {"IDENT", "STAR"}:
                raise SelectorSyntaxError(f"Namespace separator at offset {token.start} requires a type")
            if significant[index + 1].kind == "IDENT":
                nodes.append(SimpleSelector("type", significant[index + 1].value))
            index += 2
            continue

        if token.kind == "DELIM" and token.value == "&":
            nodes.append(SimpleSelector("nesting"))
            index += 1
            continue

        raise SelectorSyntaxError(f"Unexpected token {token.value!r} at offset {token.start}")

    return Selector(
        selector="".join(token.value for token in trimmed),
        simple_selectors=tuple(nodes),
        start=trimmed[0].start,
        end=trimmed[-1].end,
    )


def parse_selector_list(tokens: list[Token], *, allow_relative: bool = False) -> list[Selector]:
    """Parse a top-level selector list into specificity-relevant AST nodes."""

    return [_parse_member(member, allow_relative=allow_relative) for member in _split_top_level(tokens)]


def _max_specificity(arguments: tuple[Selector, ...]) -> Specificity:
    return max((fold_specificity(argument).specificity for argument in arguments), default=Specificity())


def fold_specificity(selector: Selector) -> SelectorResult:
    """Fold one parsed selector according to Selectors Level 4 rules."""

    score = Specificity()
    notes = {
        "Selectors Level 4 uses (A,B,C); inline styles are outside selector specificity."
    }
    for node in selector.simple_selectors:
        if node.kind == "id":
            score += Specificity(a=1)
        elif node.kind in {"class", "attribute", "pseudo-class"}:
            score += Specificity(b=1)
        elif node.kind in {"type", "pseudo-element"}:
            score += Specificity(c=1)
        elif node.kind == "where":
            notes.add(":where() and its arguments contribute zero specificity.")
        elif node.kind == "matches":
            score += _max_specificity(node.arguments)
            notes.add(f":{node.name}() contributes its most specific selector-list argument.")
        elif node.kind == "nth":
            score += Specificity(b=1) + _max_specificity(node.arguments)
            if node.arguments:
                notes.add(f":{node.name}(... of S) adds one pseudo-class plus the most specific member of S.")
    return SelectorResult(
        selector=selector.selector,
        specificity=score,
        start=selector.start,
        end=selector.end,
        notes=tuple(sorted(notes)),
    )
