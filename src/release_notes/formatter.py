def render_release_notes(changes: str) -> str:
    items = [line.strip() for line in changes.splitlines() if line.strip()]
    bullets = "\n".join(f"- {item}" for item in items)
    return f"# Release notes\n\n{bullets}\n"
