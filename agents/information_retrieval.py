import json
import os
import re
import concurrent.futures
from config import get_model, TEMPERATURE
from utils.prompt_templates import INFORMATION_RETRIEVAL_SYSTEM_PROMPT, INFORMATION_RETRIEVAL_HUMAN_PROMPT
from utils.web_search import search_and_process
from utils.caching import generate_cache_key, get_cached_response, cache_response
from utils.client_manager import get_client

def retrieve_information(subtask):
    """
    Retrieve and process information for a research subtask.
    
    Args:
        subtask (dict): A subtask from the research plan.
        
    Returns:
        dict: Processed information from various sources.
    """
    try:
        # Get search results for each query in parallel
        all_search_results = []
        
        # Define the function to process a single query
        def process_single_query(query):
            return search_and_process(query)
        
        # Use ThreadPoolExecutor to run queries in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all queries to the executor
            future_to_query = {
                executor.submit(process_single_query, query): query 
                for query in subtask["search_queries"]
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_query):
                try:
                    search_results = future.result()
                    all_search_results.extend(search_results)
                except Exception as e:
                    print(f"Error processing query: {e}")
        
        # Remove duplicate results based on URL
        unique_results = {}
        for result in all_search_results:
            if result["url"] not in unique_results:
                unique_results[result["url"]] = result
        
        # Format search results for the prompt - limit content length for speed
        formatted_results = []
        for url, result in unique_results.items():
            # Trim content to speed up processing - PLAY AROUND WITH THIS FIGURE TO SEE EFFECT ON RESULTS
            content = result['content']
            if len(content) > 1000:  # Limit to ~1000 chars for faster processing
                content = content[:1000] + "..."
                
            formatted_results.append(
                f"Source: {result['title']}\n"
                f"URL: {result['url']}\n"
                f"Content: {content}\n\n"
            )
        
        # Join the formatted results - limit to top results if many were found
        if len(formatted_results) > 5:
            formatted_results = formatted_results[:5]  # Limit to top 5 results (for now)
        search_results_text = "\n".join(formatted_results)
        
        # Format the prompt
        prompt = INFORMATION_RETRIEVAL_HUMAN_PROMPT.format(
            subtask_description=subtask["description"],
            search_results=search_results_text
        )
        
        # Get the client from client manager
        client = get_client()
        
        # Generate cache key
        messages = [
            {"role": "system", "content": INFORMATION_RETRIEVAL_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        cache_key = generate_cache_key(get_model(), messages, TEMPERATURE)
        
        # Check cache first
        cached_response = get_cached_response(cache_key)
        if cached_response:
            print(f"Using cached response for subtask: {subtask['id']}")
            content = cached_response.choices[0].message.content
        else:
            # Call the API
            response = client.chat.create(
                model=get_model(),
                messages=messages,
                temperature=TEMPERATURE
            )
            
            # Cache the response
            cache_response(cache_key, response)
            
            # Extract the content
            content = response.choices[0].message.content
        
        # Parse the JSON response
        try:
            information = json.loads(content)
            return information
        except json.JSONDecodeError:
            # If parsing fails, try to extract JSON from the text
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                try:
                    information = json.loads(json_match.group(1))
                    return information
                except:
                    pass
            
            # Fallback to a manually constructed result
            return {
                "subtask_id": subtask["id"],
                "sources": [
                    {
                        "title": result["title"],
                        "url": result["url"],
                        "credibility_score": 0.7,
                        "relevance_score": 0.8,
                        "key_information": [result["snippet"]],
                        "summary": result["snippet"]
                    } for url, result in list(unique_results.items())[:3]  # Limit to 3 sources
                ]
            }
    except Exception as e:
        print(f"Error in retrieve_information: {e}")
        # Return a simple result on error
        return {
            "subtask_id": subtask["id"],
            "sources": []
        }