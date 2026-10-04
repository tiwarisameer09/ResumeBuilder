try:
    import bleach
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False

def sanitize_text(text: str) -> str:
    """Sanitize user string inputs to prevent XSS / HTML injection in resumes."""
    if not text:
        return ""
    if BLEACH_AVAILABLE:
        # Strip all HTML tags, leaving plain text
        cleaned = bleach.clean(text, tags=[], attributes={}, strip=True)
        return cleaned.strip()
    # Basic fallback if bleach is unavailable in local dev
    return text.replace("<", "&lt;").replace(">", "&gt;").strip()
