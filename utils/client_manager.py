from config import get_provider, get_api_key

def get_client():
    """
    Get the appropriate AI client based on the current provider configuration.
    This centralises the client creation logic to avoid repetition across files.
    
    Returns:
        object: The appropriate AI client instance
    """
    provider = get_provider()
    api_key = get_api_key()
    
    if not api_key:
        raise ValueError(f"{provider.upper()} API key is not set. Please add it to your .env file or enter it in the UI.")
    
    from utils.ai_client import AIClient
    return AIClient()