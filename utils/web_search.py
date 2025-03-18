import time
import json
import os
import re
from config import get_model, SEARCH_RESULT_LIMIT
from utils.caching import generate_cache_key, get_cached_response, cache_response
from utils.client_manager import get_client

def simulated_search(query):
    """
    Simulate a web search using the current AI provider with caching.
    
    Args:
        query (str): The search query.
        
    Returns:
        list: A list of simulated search result items.
    """
    try:
        # Streamlined prompt for faster processing
        system_prompt = """You are a search engine API. Return search results in JSON format:
        [
            {
                "title": "Title of the page",
                "url": "https://example.com/page1",
                "snippet": "A brief snippet (1-2 sentences)",
                "content": "Content (300 words maximum)"
            }
        ]
        
        Create 2-3 diverse, realistic results with actual website URLs for the query.
        """
        
        prompt = f"Search query: {query}"
        
        # Generate cache key
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        cache_key = generate_cache_key(get_model(), messages, 0.7)
        
        # Check cache first
        cached_response = get_cached_response(cache_key)
        if cached_response:
            print(f"Using cached search results for: {query}")
            content = cached_response.choices[0].message.content
        else:
            # Get the client from client manager
            client = get_client()
            
            # Call API
            response = client.chat.create(
                model=get_model(),
                messages=messages,
                temperature=0.7
            )
            
            # Cache the response
            cache_response(cache_key, response)
            
            # Extract the content
            content = response.choices[0].message.content
        
        # Parse the JSON response
        try:
            search_results = json.loads(content)
            return search_results[:SEARCH_RESULT_LIMIT]
        except json.JSONDecodeError:
            # If parsing fails, try to extract JSON from the text
            json_match = re.search(r'(\[[\s\S]*\])', content)
            if json_match:
                try:
                    search_results = json.loads(json_match.group(1))
                    return search_results[:SEARCH_RESULT_LIMIT]
                except:
                    pass
            
            # Return a default response if JSON parsing fails
            return [
                {
                    "title": f"Search result for {query}",
                    "url": "https://example.com/result",
                    "snippet": "This is a placeholder result for your query.",
                    "content": f"This is simulated content for the search query: {query}. Since the actual JSON parsing failed, we're providing this placeholder content."
                }
            ]
    except Exception as e:
        print(f"Error in simulated_search: {e}")
        return []


def search_and_process(query):
    """
    Search for a query and process the results.
    
    Args:
        query (str): The search query.
        
    Returns:
        list: A list of processed search results.
    """
    search_results = simulated_search(query)
    
    # Return the results directly (no further processing needed)
    return search_results