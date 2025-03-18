import json
import os
import re
from config import get_model, TEMPERATURE
from utils.prompt_templates import TASK_MANAGER_SYSTEM_PROMPT
from utils.caching import generate_cache_key, get_cached_response, cache_response
from utils.language_detection import detect_language, format_instructions_for_language
from utils.client_manager import get_client

def create_research_plan(research_question):
    """
    Create a research plan by breaking down a research question into subtasks.
    
    Args:
        research_question (str): The main research question.
        
    Returns:
        dict: A research plan with subtasks.
    """
    try:
        # Detect the language of the research question
        language_code = detect_language(research_question)
        
        # Get language-specific instructions
        language_instruction = format_instructions_for_language(language_code)
        
        # Modified prompt to request at least 5 subtasks in the detected language
        human_prompt = f"""I need you to break down the following research question into at least 5 focused subtasks:

            {research_question}

            Each subtask should have 1-2 search queries. You MUST create AT LEAST 5 distinct subtasks covering different aspects of the research question. Feel free to create more if the complexity of the topic requires it.

            {language_instruction}"""
        
        # Get the client from the unified client manager
        client = get_client()
        
        # Generate cache key
        messages = [
            {"role": "system", "content": TASK_MANAGER_SYSTEM_PROMPT},
            {"role": "user", "content": human_prompt}
        ]
        cache_key = generate_cache_key(get_model(), messages, TEMPERATURE)
        
        # Check cache first
        cached_response = get_cached_response(cache_key)
        if cached_response:
            print(f"Using cached research plan for: {research_question}")
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
            research_plan = json.loads(content)
            
            # Store the detected language in the research plan
            research_plan["language"] = language_code
            
            # Ensure that least 5 subtasks were given
            subtasks = research_plan.get("subtasks", [])
            if len(subtasks) < 5:
                # Add more subtasks to reach at least 5
                existing_count = len(subtasks)
                additional_subtasks = generate_additional_subtasks(research_question, 5 - existing_count, existing_count, language_code)
                subtasks.extend(additional_subtasks)
                research_plan["subtasks"] = subtasks
                
            return research_plan
            
        except json.JSONDecodeError:
            # If parsing fails, try to extract JSON from the text
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                try:
                    research_plan = json.loads(json_match.group(1))
                    
                    # Store the detected language in the research plan
                    research_plan["language"] = language_code
                    
                    # Ensure we have at least 5 subtasks
                    subtasks = research_plan.get("subtasks", [])
                    if len(subtasks) < 5:
                        # Add more subtasks to reach at least 5
                        existing_count = len(subtasks)
                        additional_subtasks = generate_additional_subtasks(research_question, 5 - existing_count, existing_count, language_code)
                        subtasks.extend(additional_subtasks)
                        research_plan["subtasks"] = subtasks
                        
                    return research_plan
                except:
                    pass
            
            # Fallback to a manually constructed plan with at least 5 subtasks
            return {
                "research_question": research_question,
                "language": language_code,
                "subtasks": generate_standard_subtasks(research_question, language_code)
            }
    except Exception as e:
        print(f"Error in create_research_plan: {e}")
        # Return a fallback plan with at least 5 subtasks
        language_code = detect_language(research_question)
        return {
            "research_question": research_question,
            "language": language_code,
            "subtasks": generate_standard_subtasks(research_question, language_code)
        }

def generate_additional_subtasks(research_question, count, start_index=0, language_code='en'):
    """
    Generate additional subtasks to ensure we have the minimum required number.
    
    Args:
        research_question (str): The main research question
        count (int): Number of additional subtasks needed
        start_index (int): Starting index for subtask IDs
        language_code (str): Language code for response
        
    Returns:
        list: List of additional subtask dictionaries
    """
    # Template subtasks that could apply to most research questions
    # In an ideal situation, these would be translated for each supported language
    templates = [
        {
            "description": "Historical background and evolution",
            "search_queries": [f"history of {research_question}", f"evolution of {research_question}"]
        },
        {
            "description": "Current trends and future outlook",
            "search_queries": [f"future of {research_question}", f"trends in {research_question}"]
        },
        {
            "description": "Key debates and controversies",
            "search_queries": [f"debates about {research_question}", f"controversies about {research_question}"]
        },
        {
            "description": "Practical applications and real-world examples",
            "search_queries": [f"applications of {research_question}", f"examples of {research_question}"]
        },
        {
            "description": "Expert opinions and academic research",
            "search_queries": [f"expert opinions on {research_question}", f"research on {research_question}"]
        },
        {
            "description": "Economic and business implications",
            "search_queries": [f"economic impact of {research_question}", f"business implications of {research_question}"]
        },
        {
            "description": "Technological aspects and innovations",
            "search_queries": [f"technology in {research_question}", f"innovations in {research_question}"]
        },
        {
            "description": "Social and cultural impact",
            "search_queries": [f"social impact of {research_question}", f"cultural aspects of {research_question}"]
        },
        {
            "description": "Ethical considerations and concerns",
            "search_queries": [f"ethics of {research_question}", f"ethical issues in {research_question}"]
        },
        {
            "description": "Legal and regulatory framework",
            "search_queries": [f"regulations for {research_question}", f"laws about {research_question}"]
        }
    ]
    
    additional_subtasks = []
    for i in range(count):
        template = templates[i % len(templates)]
        subtask = {
            "id": f"subtask-{start_index + i + 1}",
            "description": template["description"],
            "search_queries": template["search_queries"]
        }
        additional_subtasks.append(subtask)
    
    return additional_subtasks

def generate_standard_subtasks(research_question, language_code='en'):
    """
    Generate a standard set of subtasks that would work for most research questions.
    
    Args:
        research_question (str): The main research question
        language_code (str): Language code for response
        
    Returns:
        list: List of standard subtask dictionaries
    """
    # Create at least 6 subtasks to exceed the minimum requirement
    # For a production system, these would be translated for each supported language
    return [
        {
            "id": "subtask-1",
            "description": f"Key concepts and definitions related to {research_question}",
            "search_queries": [f"{research_question} definition", f"{research_question} explained"]
        },
        {
            "id": "subtask-2",
            "description": f"Historical background and evolution of {research_question}",
            "search_queries": [f"history of {research_question}", f"evolution of {research_question}"]
        },
        {
            "id": "subtask-3",
            "description": f"Current developments and state of the art in {research_question}",
            "search_queries": [f"latest developments in {research_question}", f"current state of {research_question}"]
        },
        {
            "id": "subtask-4",
            "description": f"Challenges, controversies, or debates related to {research_question}",
            "search_queries": [f"challenges in {research_question}", f"controversies about {research_question}"]
        },
        {
            "id": "subtask-5",
            "description": f"Future trends and implications of {research_question}",
            "search_queries": [f"future of {research_question}", f"implications of {research_question}"]
        },
        {
            "id": "subtask-6",
            "description": f"Practical applications and real-world examples of {research_question}",
            "search_queries": [f"applications of {research_question}", f"examples of {research_question}"]
        }
    ]