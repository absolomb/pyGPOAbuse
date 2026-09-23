"""Helpers for the bracketed GPO client-side extension list."""

import re


SCHEDULED_TASKS_CSE = "AADCED64-746C-4633-A97C-D61349046527"
SCHEDULED_TASKS_TOOL = "CAB54552-DEEA-4691-817E-ED4A4D1AFC72"
NULL_CSE = "00000000-0000-0000-0000-000000000000"
GROUP = re.compile(r"\[([^][]+)\]")
GUID = re.compile(r"\{([0-9A-Fa-f-]{36})\}")


def remove_scheduled_task_extensions(value):
    """Remove scheduled-task entries while preserving unrelated GPO extensions."""
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        value = "".join(value)
    if not value:
        return value

    groups = list(GROUP.finditer(value))
    if "".join(match.group(0) for match in groups) != value:
        raise ValueError("Unrecognized GPO extension list format")

    result = []
    for match in groups:
        content = match.group(1)
        guids = GUID.findall(content)
        if len(guids) < 2 or "".join("{" + guid + "}" for guid in guids) != content:
            raise ValueError("Unrecognized GPO extension group format")

        cse = guids[0].upper()
        if cse == SCHEDULED_TASKS_CSE:
            continue
        if cse == NULL_CSE:
            tools = [guid for guid in guids[1:] if guid.upper() != SCHEDULED_TASKS_TOOL]
            if tools:
                result.append("[" + "{" + guids[0] + "}" + "".join("{" + guid + "}" for guid in tools) + "]")
            continue
        result.append(match.group(0))
    return "".join(result)
