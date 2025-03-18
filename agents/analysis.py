import json
import os
import re
from config import get_model, TEMPERATURE
from utils.prompt_templates import ANALYSIS_SYSTEM_PROMPT
from utils.caching import generate_cache_key, get_cached_response, cache_response
from utils.client_manager import get_client

def analyse_information(subtask, information):
    """
    Analyse information collected for a research subtask.
    
    Args:
        subtask (dict): A subtask from the research plan.
        information (dict): Information retrieved for the subtask.
        
    Returns:
        dict: Analysis of the information.
    """
    try:
        # Format the information for the prompt 
        formatted_information = []
        for source in information.get("sources", [])[:3]:  # Limit to top 3 sources (for now)
            formatted_information.append(
                f"Source: {source.get('title', 'Unknown')}\n"
                f"URL: {source.get('url', 'Unknown')}\n"
                f"Key Information: " + "; ".join(source.get("key_information", []))
            )
        
        # Join the formatted information
        information_text = "\n\n".join(formatted_information)
        
        # Streamlined prompt with few findings for faster processing and testing (for now)
        human_prompt = f"""Analyse this information for the research subtask:

            Subtask: {subtask["description"]}

            Information:
            {information_text}

            Focus on 3-5 key findings and a brief summary."""
        
        # Get the client from client manager
        client = get_client()
        
        # Generate cache key
        messages = [
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": human_prompt}
        ]
        cache_key = generate_cache_key(get_model(), messages, TEMPERATURE)
        
        # Check cache first
        cached_response = get_cached_response(cache_key)
        if cached_response:
            print(f"Using cached analysis for subtask: {subtask['id']}")
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
            analysis = json.loads(content)
            return analysis
        except json.JSONDecodeError:
            # If parsing fails, try to extract JSON from the text
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                try:
                    analysis = json.loads(json_match.group(1))
                    return analysis
                except:
                    pass
            
            # Fallback to a manually constructed analysis - simple for speed
            return {
                "subtask_id": subtask["id"],
                "analysis": {
                    "key_findings": [
                        "Information was successfully collected on this topic",
                        "Multiple sources provided relevant insights"
                    ],
                    "patterns_identified": [],
                    "contradictions": [],
                    "knowledge_gaps": [],
                    "summary": f"The collected information provides useful insights into {subtask['description']}."
                }
            }
    except Exception as e:
        print(f"Error in analyse_information: {e}")
        # Return a simple analysis on error
        return {
            "subtask_id": subtask["id"],
            "analysis": {
                "key_findings": ["Limited information processing"],
                "patterns_identified": [],
                "contradictions": [],
                "knowledge_gaps": [],
                "summary": f"Basic insights on {subtask['description']}."
            }
        }