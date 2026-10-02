def enforce_draft_format(draft: str) -> str:
    """
    Deterministically enforce formatting rules on an AI-generated draft.
    """

    draft = draft.strip()

    # Remove accidental metadata prefixes.
    prefixes = [
        "Draft:",
        "Response:",
        "Customer Response:",
    ]

    for prefix in prefixes:
        if draft.startswith(prefix):
            draft = draft[len(prefix):].strip()

    # Enforce the 100-word limit.
    words = draft.split()

    if len(words) > 100:
        draft = " ".join(words[:100])

    return draft