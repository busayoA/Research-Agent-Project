import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# API keys from environment variables
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Provider configuration (default to Mistral)
AI_PROVIDER = os.environ.get("AI_PROVIDER", "mistral")  # Options: "mistral" or "openai"

# Model configurations
MISTRAL_MODEL = os.environ.get("MISTRAL_MODEL", "mistral-small")  # Default to the fastest model
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")  # Default to GPT-3.5 Turbo

# Common parameters - optimised for speed
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "1500"))  # Reduced for speed (for now)

# Search parameters
SEARCH_RESULT_LIMIT = int(os.environ.get("SEARCH_RESULT_LIMIT", "2"))

def get_provider():
    """Get the current AI provider"""
    return AI_PROVIDER

def get_model():
    """Get the appropriate model name based on the current provider"""
    if AI_PROVIDER.lower() == "openai":
        return OPENAI_MODEL
    else:
        return MISTRAL_MODEL

def get_api_key():
    """Get the appropriate API key based on the current provider"""
    if AI_PROVIDER.lower() == "openai":
        return OPENAI_API_KEY
    else:
        return MISTRAL_API_KEY

def set_provider(provider):
    """Set the AI provider ('mistral' or 'openai')"""
    global AI_PROVIDER
    if provider.lower() in ["mistral", "openai"]:
        AI_PROVIDER = provider.lower()
        os.environ["AI_PROVIDER"] = provider.lower()
    else:
        raise ValueError("Provider must be either 'mistral' or 'openai'")

def set_model(model):
    """Set the model for the current provider"""
    global MISTRAL_MODEL, OPENAI_MODEL
    if AI_PROVIDER.lower() == "openai":
        OPENAI_MODEL = model
        os.environ["OPENAI_MODEL"] = model
    else:
        MISTRAL_MODEL = model
        os.environ["MISTRAL_MODEL"] = model
        
def get_model_options():
    """Get available model options for the current provider"""
    if AI_PROVIDER.lower() == "openai":
        return {
            "gpt-3.5-turbo": "GPT-3.5 Turbo (Fastest ⚡)",
            "gpt-4-turbo": "GPT-4 Turbo (Balanced)",
            "gpt-4o": "GPT-4o (Most Capable)"
        }
    else:
        return {
            "mistral-small": "Mistral Small (Fastest ⚡)",
            "mistral-medium": "Mistral Medium (Balanced)",
            "mistral-large": "Mistral Large (Most Capable)"
        }

# Validate API key
def validate_api_key():
    """Validate that the appropriate API key is set"""
    if AI_PROVIDER.lower() == "openai" and not OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY is not set. Please add it to your .env file.")
        return False
    elif AI_PROVIDER.lower() == "mistral" and not MISTRAL_API_KEY:
        print("WARNING: MISTRAL_API_KEY is not set. Please add it to your .env file.")
        return False
    return True