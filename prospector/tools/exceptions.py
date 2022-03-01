class BadToolConfig(Exception):
    def __init__(self, tool_name: str, message: str):
        super().__init__(f"Bad option value found for tool {tool_name}: {message}")
