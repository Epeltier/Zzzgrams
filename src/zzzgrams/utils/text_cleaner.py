def clean_text_for_json(text: str) -> str:
    """
    Clean text to be safe for JSON serialization without escaping
    
    Args:
        text: Raw text that may contain special characters
        
    Returns:
        str: Cleaned text safe for JSON
    """
    # Replace newlines with spaces to avoid JSON escaping
    text = text.replace('\n', ' ').replace('\r', ' ')
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove quotes if they wrap the entire text
    text = text.strip()
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    return text 