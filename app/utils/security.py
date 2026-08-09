"""Security utilities for input validation and file handling."""

import re
from typing import Optional
from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def validate_text_input(text: str, max_length: int = 4000) -> tuple[bool, Optional[str]]:
    """
    Validate text input for safety.
    
    Args:
        text: The text to validate
        max_length: Maximum allowed length
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Input cannot be empty"
    
    if len(text) > max_length:
        return False, f"Input exceeds maximum length of {max_length} characters"
    
    # Check for potential prompt injection patterns
    dangerous_patterns = [
        r"<script.*?>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"eval\s*\(",
        r"exec\s*\(",
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(f"Potentially dangerous input detected: {pattern}")
            return False, "Input contains potentially dangerous content"
    
    return True, None


def validate_file_size(file_size_bytes: int) -> tuple[bool, Optional[str]]:
    """
    Validate file size against configured limits.
    
    Args:
        file_size_bytes: Size of the file in bytes
        
    Returns:
        tuple: (is_valid, error_message)
    """
    max_size = settings.max_file_size_mb * 1024 * 1024  # Convert to bytes
    
    if file_size_bytes > max_size:
        return False, f"File exceeds maximum size of {settings.max_file_size_mb}MB"
    
    return True, None


def validate_file_type(filename: str, mime_type: str) -> tuple[bool, Optional[str]]:
    """
    Validate file type against allowed types.
    
    Args:
        filename: The filename to check
        mime_type: The MIME type to check
        
    Returns:
        tuple: (is_valid, error_message)
    """
    allowed_types = settings.allowed_file_types.split(",")
    
    # Check by extension
    file_extension = filename.split(".")[-1].lower() if "." in filename else ""
    if file_extension not in allowed_types:
        return False, f"File type .{file_extension} is not allowed"
    
    # Additional MIME type validation for PDFs
    if file_extension == "pdf" and mime_type != "application/pdf":
        return False, "Invalid PDF file"
    
    # Image MIME types
    if file_extension in ["jpg", "jpeg"] and mime_type not in ["image/jpeg", "image/jpg"]:
        return False, "Invalid JPEG file"
    
    if file_extension == "png" and mime_type != "image/png":
        return False, "Invalid PNG file"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Remove path separators
    filename = filename.replace("/", "").replace("\\", "")
    
    # Remove special characters that could be problematic
    filename = re.sub(r'[<>:"|?*]', '', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:255 - len(ext) - 1] + "." + ext if ext else name[:255]
    
    return filename


def detect_prompt_injection(text: str) -> tuple[bool, Optional[str]]:
    """
    Detect potential prompt injection attempts.
    
    Args:
        text: The text to analyze
        
    Returns:
        tuple: (is_suspicious, reason)
    """
    suspicious_patterns = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"forget\s+(everything|all\s+instructions)",
        r"override\s+(your\s+)?programming",
        r"new\s+(system\s+)?instruction",
        r"act\s+as\s+(a\s+)?different",
        r"pretend\s+(you\s+are)?",
        r"roleplay\s+as",
        r"simulate\s+(a\s+)?",
        r"bypass\s+(your\s+)?safety",
        r"disable\s+(your\s+)?filters",
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(f"Potential prompt injection detected: {pattern}")
            return True, f"Potential prompt injection detected: {pattern}"
    
    return False, None


def validate_stock_symbol(symbol: str) -> tuple[bool, Optional[str]]:
    """
    Validate stock symbol format.
    
    Args:
        symbol: The stock symbol to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not symbol or not symbol.strip():
        return False, "Stock symbol cannot be empty"
    
    # Basic validation: 1-5 uppercase letters, optionally followed by numbers
    symbol = symbol.strip().upper()
    if not re.match(r'^[A-Z]{1,5}\d*$', symbol):
        return False, "Invalid stock symbol format"
    
    return True, None
