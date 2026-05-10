class GujBotException(Exception):
    """Base exception class for GujBot."""
    pass

class MissingAPIKeyError(GujBotException):
    """Raised when an API key is missing for the selected provider."""
    pass

class ModelAPIError(GujBotException):
    """Raised when an error occurs during an API call to a model provider."""
    pass

class RAGSearchError(GujBotException):
    """Raised when an error occurs during vector database search."""
    pass
