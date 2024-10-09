def error_detail(msg: str, errtype: str = "custom") -> list[dict[str, str]]:
    """Provide an error message in the ValidationError schema format."""
    return [{"msg": msg, "type": errtype}]
