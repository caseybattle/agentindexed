#!/usr/bin/env python3
"""PreToolUse hook: cap the output of enumeration commands before they run.

Reads the Claude Code hook payload on stdin. When a Bash command contains a
segment known to emit huge output (ps/env/find/ls -R/du/dmesg/git log), that
segment is rewritten with a bounded pipe and the modified command is handed
back via hookSpecificOutput.updatedInput.

Two properties matter more than coverage here:

  * Fail open. Any parse problem, any surprise -> emit nothing and let the
    original command run untouched. A hook that breaks the shell is worse
    than a hook that misses a case.
  * Prefer width caps over row caps. `cut -c1-200` keeps every row of `ps`
    output and drops only the runaway argv tail, so no row is silently lost.
    Row caps (`head -n`) are used only where the row count itself is
    unbounded, and they announce themselves in the output.
"""
import json
import re
import sys

WIDTH = 200      # chars per line kept for width-capped commands
ROWS = 200       # lines kept for row-capped commands
NOTE = "[trimmed by .claude/hooks/trim-bash-output.py]"

# A segment is left alone if it already bounds its own output, or if it is
# doing something that a trailing pipe would corrupt.
HAS_LIMITER = re.compile(r"\b(head|tail|cut|wc|sed|awk|column|jq)\b")
UNSAFE = re.compile(r"[|<>`]|\$\(")

# (segment matcher, pipe to append, announce-truncation-in-output)
RULES = [
    (re.compile(r"^\s*ps\s+-?-?(aux|ef|eo|Ao|A|e)\b"), "cut -c1-%d" % WIDTH, False),
    (re.compile(r"^\s*(env|printenv)\b"), "cut -c1-%d" % WIDTH, False),
    (re.compile(r"^\s*find\b(?!.*(-maxdepth|-delete|-exec|-printf))"), "head -n %d" % ROWS, True),
    (re.compile(r"^\s*ls\s+-\w*R"), "head -n %d" % ROWS, True),
    (re.compile(r"^\s*du\b(?!.*-s)"), "head -n %d" % ROWS, True),
    (re.compile(r"^\s*(dmesg|journalctl)\b"), "tail -n %d" % ROWS, True),
    (re.compile(r"^\s*git\s+log\b(?!.*(-n\s|--oneline|-\d))"), "head -n %d" % ROWS, True),
]


def balanced(segment):
    """True when quotes pair up, so the separator split did not cut mid-string."""
    return segment.count("'") % 2 == 0 and segment.count('"') % 2 == 0


def rewrite_segment(segment):
    """Return the bounded form of one simple segment, or None to leave it be."""
    if UNSAFE.search(segment) or HAS_LIMITER.search(segment) or not balanced(segment):
        return None
    for pattern, pipe, announce in RULES:
        if pattern.search(segment):
            trimmed = segment.rstrip()
            trailing = segment[len(trimmed):]
            out = "%s | %s" % (trimmed, pipe)
            if announce:
                out += " && echo '%s'" % NOTE
            return out + trailing
    return None


def rewrite(command):
    """Rewrite noisy segments in place, preserving separators and everything else."""
    parts = re.split(r"(\s*(?:&&|\|\||;)\s*)", command)
    changed = False
    for i in range(0, len(parts), 2):          # even indices are segments
        new = rewrite_segment(parts[i])
        if new is not None:
            parts[i] = new
            changed = True
    return "".join(parts) if changed else None


def main():
    payload = json.load(sys.stdin)
    if payload.get("tool_name") != "Bash":
        return
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command")
    if not isinstance(command, str) or not command.strip():
        return
    updated = rewrite(command)
    if updated is None:
        return
    result = dict(tool_input)
    result["command"] = updated
    json.dump({
        "systemMessage": "token-guard: capped output of an enumeration command",
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": result,
        },
    }, sys.stdout)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail open: no output means the original command runs unchanged
