#!/usr/bin/env python3
"""Record sanitized Claude Code tool failures for later review.

Records enough to prevent recurring silent failures while minimizing
secret/context leakage.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
LEDGER = ROOT / ".claude" / "local" / "failure_ledger.jsonl"

# Secret masking is a hand-written, single-pass scanner, not regular expressions
# (CodeQL alert #5: the old nested-quantifier patterns could backtrack
# super-linearly). Input is capped at SCAN_CAP characters BEFORE any parsing, so
# the cost of scrubbing never depends on the raw failure payload size. When in
# doubt the scanner masks: unterminated quotes, brackets and truncated
# constructs are redacted through the end of the bounded input.
SCAN_CAP = 8192
REDACTED = "<redacted>"
_QUOTES = "\"'"
# An identifier is sensitive when it ENDS with one of these stems, whatever the
# prefix (long, Unicode, camelCase): "x" * 65 + "token" still counts.
_SENSITIVE_STEMS = (
    "token",
    "secret",
    "password",
    "passwd",
    "apikey",
    "api_key",
    "api-key",
    "auth",
    "authorization",
    "credential",
    "credentials",
)
# Sensitive only when followed by "key", "_key" or "-key": "ssh_key", "accessKey".
_KEYED_STEMS = (
    "encryption",
    "signing",
    "private",
    "ssh",
    "gpg",
    "hmac",
    "jwt",
    "session",
    "csrf",
    "access",
)
# "Authorization: Bearer <credential>": a scheme word as the value means the
# credential follows it, so both words are masked.
_AUTH_SCHEMES = ("bearer", "basic", "digest", "token", "negotiate", "ntlm")
# Characters of a bare bearer token (RFC 6750 b64token, as the old pattern).
_TOKEN_CHARS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._~+/=-")
_HOST_STOP = ",;\"'"
_TRUNCATED = "... <truncated>"


def _is_ident(c: str) -> bool:
    return c.isalnum() or c == "_" or c == "-"


def _mentions_key(text: str) -> bool:
    """True when ``text`` contains anything key-like (fail-closed widening)."""
    t = text.lower()
    return "key" in t or "bearer" in t or any(stem in t for stem in _SENSITIVE_STEMS)


def _is_sensitive_key(word: str) -> bool:
    w = word.lower()
    if w.endswith(("_key", "-key")):
        base = w[:-4]
        if base.endswith(_SENSITIVE_STEMS) or base.endswith(_KEYED_STEMS):
            return True
    if w.endswith("key") and w[:-3].endswith(_KEYED_STEMS):
        return True
    return w.endswith(_SENSITIVE_STEMS)


def _skip_space(s: str, k: int, n: int) -> int:
    while k < n and s[k].isspace():
        k += 1
    return k


def _value_end(s: str, k: int, n: int) -> int:
    """Return the index just past the secret value that starts at ``k``.

    Shell-like: a value is a run of unquoted characters and quoted segments that
    ends at unquoted whitespace or one of ``, ; } ]``. Quoted segments may span
    line breaks and honour backslash escapes (so ``"abc\\"x"`` is one value);
    ``{`` / ``[`` open a nested structure consumed to its matching close.
    Anything unterminated masks through the end of the bounded input.
    """
    depth = 0
    while k < n:
        c = s[k]
        if c in _QUOTES:
            k += 1
            while k < n and s[k] != c:
                k += 2 if s[k] == "\\" else 1
            if k >= n:
                return n
            k += 1
        elif c == "\\":
            k += 2
        elif c in "{[":
            depth += 1
            k += 1
        elif c in "}]":
            if depth == 0:
                break
            depth -= 1
            k += 1
        elif depth == 0 and (c.isspace() or c in ",;"):
            break
        else:
            k += 1
    return min(k, n)


class _Masker:
    """One forward pass over already-bounded text.

    The committed cursor ``i`` only ever increases. Each helper looks ahead from
    the cursor and either commits (the cursor jumps past everything it consumed,
    so assignment-like text inside an already-masked value is never scanned
    again) or declines (the caller emits the text verbatim and moves on). The
    lookahead regions do not overlap, so total work is linear in the input.
    """

    def __init__(self, s: str, truncated: bool, urls: bool = True) -> None:
        self.s = s
        self.n = len(s)
        self.truncated = truncated
        # False only for the nested pass over a connection string's own
        # scheme/user part, which therefore cannot recurse again.
        self.urls = urls
        # Cache for "next '@' at or after k": there is no '@' in
        # [_at_from, _at), and _at is an '@' (or -1: none at all). Every
        # refresh starts beyond the previous hit, so all searches together
        # read the text at most once.
        self._at_from = -1
        self._at = -1

    def _find_at(self, k: int) -> int:
        if self._at_from != -1 and self._at_from <= k and (self._at == -1 or self._at >= k):
            return self._at
        self._at_from = k
        self._at = self.s.find("@", k)
        return self._at

    def run(self) -> str:
        s, n = self.s, self.n
        out: list[str] = []
        i = 0
        while i < n:
            if not _is_ident(s[i]):
                out.append(s[i])
                i += 1
                continue
            j = i
            while j < n and _is_ident(s[j]):
                j += 1
            word = s[i:j]
            sensitive = _is_sensitive_key(word)
            if self.urls and s.startswith("://", j):
                conn = self._connection_string(i, j)
                if conn is not None:
                    text, end = conn
                    if sensitive:
                        # "token://u:p@host" is also "token: <value>": mask the
                        # whole value, as the old sequential passes did.
                        text = f"{word}={REDACTED}"
                        end = self._masked_through(end, _value_end(s, end, n))
                    out.append(text)
                    i = end
                    continue
            if sensitive:
                done, stop = self._assignment(word, j, out)
                if done is None:
                    # No separator. The looked-at gap holds only quotes,
                    # backslashes and whitespace, inert outside a value.
                    out.append(s[i:stop])
                i = stop
                continue
            if word.lower().endswith("bearer"):
                done = self._bearer(word, j, out)
                if done is not None:
                    i = done
                    continue
            out.append(word)
            i = j
        return "".join(out)

    def _separator(self, k: int) -> tuple[bool, int]:
        """Look for ``:`` / ``=`` (also ``:=``, ``==``, ``=>``) from ``k``,
        crossing only quotes, backslashes and whitespace (a quoted key, a line
        break). Returns (found, index past it) or (False, where it stopped)."""
        s, n = self.s, self.n
        while k < n and (s[k] in _QUOTES or s[k] == "\\" or s[k].isspace()):
            k += 1
        if k >= n or s[k] not in ":=":
            return False, k
        k += 1
        if k < n and s[k] in "=>":
            k += 1
        return True, k

    def _masked_through(self, start: int, end: int) -> int:
        """Extend a masked value ``s[start:end]`` while it chains on (fail closed).

        * a value ending in an auth scheme word ("Bearer"), or consisting only
          of an empty quoted string, is followed by the real credential;
        * a value holding ``scheme://user:`` whose password runs past the
          value's end (to a later '@') is masked through that host;
        * a value that swallowed something key-like and ends with, or is
          followed by, a separator ("x/api_key = <secret>") carries the next
          value too.

        Every step starts at or after the previous end, so this stays linear.
        """
        s, n = self.s, self.n
        while True:
            seg = s[start:end].lower()
            scheme_or_empty = seg.endswith(_AUTH_SCHEMES) or (seg and not seg.strip(_QUOTES))
            if scheme_or_empty and end < n and s[end].isspace():
                nxt = _skip_space(s, end, n)
                nxt_end = _value_end(s, nxt, n)
                if nxt_end > nxt:
                    start, end = nxt, nxt_end
                    continue
                return end
            if self.urls and "://" in seg:
                far = self._url_reach(start, end)
                if far > end:
                    start, end = end, far
                    continue
            if not _mentions_key(seg):
                return end
            if seg.endswith((":", "=", ">")):
                nxt = _skip_space(s, end, n)
            else:
                found, nxt = self._separator(end)
                if not found:
                    return end
                nxt = _skip_space(s, nxt, n)
            nxt_end = _value_end(s, nxt, n)
            if nxt_end == nxt:
                return end
            start, end = nxt, nxt_end

    def _url_reach(self, start: int, end: int) -> int:
        """Furthest index a connection string beginning inside ``s[start:end]``
        masks when its password ends beyond ``end``; ``end`` if none does."""
        s = self.s
        p = s.find("://", start, end)
        while p != -1:
            if p > 0 and _is_ident(s[p - 1]):
                span = self._conn_span(p, beyond=end)
                if span is not None:
                    return span[2]
            p = s.find("://", p + 3, end)
        return end

    def _assignment(self, word: str, j: int, out: list[str]) -> tuple[int | None, int]:
        """``key = value`` / ``"key": "value"`` / ``key:\\n  value``."""
        s, n = self.s, self.n
        found, k = self._separator(j)
        if not found:
            return None, k
        k = _skip_space(s, k, n)
        end = self._masked_through(k, _value_end(s, k, n))
        key = "authorization" if word.lower() == "authorization" else word
        out.append(f"{key}={REDACTED}")
        return end, end

    def _bearer(self, word: str, j: int, out: list[str]) -> int | None:
        """``Bearer <token>`` outside any key assignment."""
        s, n = self.s, self.n
        k = _skip_space(s, j, n)
        if k == j or k >= n or s[k] not in _TOKEN_CHARS:
            return None
        end = k
        while end < n and s[end] in _TOKEN_CHARS:
            end += 1
        if _mentions_key(s[k:end]):
            # The token swallowed an assignment ("Bearer token=a@b"): finish
            # that value with the full value grammar.
            end = _value_end(s, end, n)
        out.append(f"{word[:-6]}Bearer {REDACTED}")
        return self._masked_through(k, end)

    def _conn_span(self, j: int, beyond: int = -1) -> tuple[int, int, int] | None:
        """Parse ``://user:password@host`` at ``j`` (the index of "://").

        Mirrors the retired pattern ``\\w+://[^/:]+:([^@]+)@[^\\s,;"']+``: the
        password runs from the first ':' after the user to the next '@' (here:
        the last '@' of the unbroken run, since a password may contain '@').
        Returns (colon, last '@' or -1, end of host run); '@' is -1 when the
        input was truncated before any '@', which masks to the end. With
        ``beyond`` set, only a password reaching past it counts.
        """
        s, n = self.s, self.n
        h = j + 3
        while h < n and s[h] not in "/:":
            h += 1
        if h == j + 3 or h >= n or s[h] != ":":
            return None
        at = self._find_at(h + 1)
        if at == -1:
            return (h, -1, n) if self.truncated else None
        if at == h + 1 or at + 1 >= n or s[at + 1].isspace() or s[at + 1] in _HOST_STOP:
            return None
        if at < beyond:
            return None
        k = at + 1
        while k < n and not s[k].isspace() and s[k] not in _HOST_STOP:
            if s[k] == "@":
                at = k
            k += 1
        return h, at, k

    def _connection_string(self, i: int, j: int) -> tuple[str, int] | None:
        """``scheme://user:password@host`` starting at word ``s[i:j]``: mask the
        password. Returns the replacement text and the index to resume from."""
        s, n = self.s, self.n
        span = self._conn_span(j)
        if span is None:
            return None
        h, at, k = span
        user = s[j + 3 : h]
        if at == -1:
            # Truncated before any '@': it may lie beyond the cap, mask the rest.
            head = s[i : j + 3] + _Masker(user, False, urls=False).run()
            return head + ":" + REDACTED, n
        # The old substitution also masked copies of the password elsewhere in
        # the match; keep that (a copy in the host masks the whole host). The
        # user part is masked by a nested pass that cannot recurse again.
        password = s[h + 1 : at]
        head = s[i : h + 1].replace(password, REDACTED)
        prefix = _Masker(head, False, urls=False).run()
        if s.find(password, at + 1, k) != -1:
            return prefix + REDACTED + "@" + REDACTED, k
        if _mentions_key(user):
            # "x://api_key:<v>@<rest>": the user part is itself a key, so its
            # value continues past the '@'. Mask through the end of it.
            return prefix + REDACTED, self._masked_through(at + 1, _value_end(s, at + 1, n))
        return prefix + REDACTED + "@", at + 1


def _bounded(s: str) -> tuple[str, bool]:
    """Cap ``s`` at SCAN_CAP before parsing.

    When capped, the final partial token is dropped too, so a key, bearer token
    or connection string cut mid-way can never surface unmasked.
    """
    if len(s) <= SCAN_CAP:
        return s, False
    cut = SCAN_CAP
    while cut > 0 and not s[cut - 1].isspace():
        cut -= 1
    return s[:cut], True


def scrub(text: object, limit: int = 240) -> str:
    s = str(text or "")
    bounded, truncated = _bounded(s)
    try:
        s = _Masker(bounded, truncated).run()
    except Exception:  # the recorder must never crash: fail closed
        return REDACTED
    s = s.replace(str(ROOT), ".")
    if truncated or len(s) > limit:
        s = s[:limit] + _TRUNCATED
    return s


def summarize_target(value: object) -> str:
    s = str(value or "")
    if not s.strip():
        # Empty OR whitespace-only: nothing to summarise. (A whitespace-only value
        # is truthy, so a bare `if not s` let it through and `split()[0]` below then
        # raised IndexError — crashing the very hook meant to RECORD failures.)
        return ""
    scrubbed = scrub(s, 500)
    first = scrubbed.split(maxsplit=1)[0]
    digest = hashlib.sha256(scrubbed.encode("utf-8", "ignore")).hexdigest()[:12]
    return f"{scrub(first, 60)} sha256:{digest}"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool_name = payload.get("tool_name", "unknown")
    tool_input = payload.get("tool_input", {}) or {}
    entry = {
        "ts": dt.datetime.now(dt.UTC).isoformat(),
        "class": "unclassified",
        "surface": scrub(tool_name, 80),
        "command_or_target": summarize_target(
            tool_input.get("command") or tool_input.get("file_path") or ""
        ),
        "failure": scrub(
            payload.get("error") or payload.get("stderr") or payload.get("message") or "",
            240,
        ),
        "workaround": "",
        "future_fix": "classify and promote if recurring",
        "status": "open",
    }

    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUseFailure",
                    "additionalContext": (
                        "Tool failure recorded in ignored "
                        ".claude/local/failure_ledger.jsonl. Classify unresolved "
                        "failures in the handoff."
                    ),
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
