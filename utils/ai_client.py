import os
import requests
import json
from config import get_provider, get_api_key

class AIClient:
    """
    A unified client for multiple AI providers (Mistral and OpenAI).
    """
    
    def __init__(self):
        """Initialise the AI client."""
        self.provider = get_provider()
        self.api_key = get_api_key()
        
        if not self.api_key:
            raise ValueError(f"{self.provider.upper()} API key is not set. Please add it to your .env file.")
        
        # Configure base URLs
        self.base_urls = {
            "mistral": "https://api.mistral.ai/v1",
            "openai": "https://api.openai.com/v1"
        }
        
        self.chat = ChatCompletions(self)
    
    def update_configuration(self):
        """Update configuration (useful when provider changes)."""
        self.provider = get_provider()
        self.api_key = get_api_key()
        
        if not self.api_key:
            raise ValueError(f"{self.provider.upper()} API key is not set. Please add it to your .env file.")


class ChatCompletions:
    """
    Handles chat completions for multiple AI providers.
    """
    
    def __init__(self, client):
        """
        Initialise the chat completions handler.
        
        Args:
            client (AIClient): The parent AI client.
        """
        self.client = client
    
    def create(self, model, messages, temperature=0.7, max_tokens=None):
        """
        Create a chat completion with the current provider's API.
        
        Args:
            model (str): The model ID to use.
            messages (list): A list of message objects.
            temperature (float, optional): The temperature for sampling. Default is 0.7.
            max_tokens (int, optional): The maximum number of tokens to generate.
            
        Returns:
            ChatResponse: A standardised response object.
        """
        # Ensure we have current configuration
        self.client.update_configuration()
        provider = self.client.provider
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Set up provider-specific headers and payload
        if provider == "mistral":
            headers["Authorization"] = f"Bearer {self.client.api_key}"
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens
        else:  # OpenAI
            headers["Authorization"] = f"Bearer {self.client.api_key}"
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens
        
        # Make the API request
        response = requests.post(
            f"{self.client.base_urls[provider]}/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code != 200:
            raise Exception(f"Error from {provider.upper()} API: {response.status_code} - {response.text}")
        
        # Parse the response
        response_data = response.json()
        
        # Create a standardised response object
        return ChatResponse(response_data, provider)


class ChatResponse:
    """
    A standardised response object for chat completions.
    """
    
    def __init__(self, response_data, provider):
        """
        Initialise the response object.
        
        Args:
            response_data (dict): The response data from the provider API.
            provider (str): The AI provider ("mistral" or "openai").
        """
        self.provider = provider
        self.id = response_data.get("id")
        self.created = response_data.get("created")
        self.model = response_data.get("model")
        
        # Create standardised choices
        self.choices = []
        
        if provider == "mistral":
            # Process Mistral response format
            for choice in response_data.get("choices", []):
                content = choice.get("message", {}).get("content", "")
                message = {"role": choice.get("message", {}).get("role", "assistant"), "content": content}
                self.choices.append(MessageChoice(0, message, choice.get("finish_reason")))
        else:  # OpenAI
            # Process OpenAI response format
            for i, choice in enumerate(response_data.get("choices", [])):
                message = choice.get("message", {})
                self.choices.append(MessageChoice(i, message, choice.get("finish_reason")))


class MessageChoice:
    """
    A standardised message choice object.
    """
    
    def __init__(self, index, message, finish_reason):
        """
        Initialise the message choice.
        
        Args:
            index (int): The index of the choice.
            message (dict): The message content.
            finish_reason (str): The reason why the generation finished.
        """
        self.index = index
        self.message = Message(message.get("role", "assistant"), message.get("content", ""))
        self.finish_reason = finish_reason


class Message:
    """
    A standardised message object.
    """
    
    def __init__(self, role, content):
        """
        Initialise the message.
        
        Args:
            role (str): The role of the message (system, user, assistant).
            content (str): The content of the message.
        """
        self.role = role
        self.content = content