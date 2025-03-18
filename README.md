# AI Research Assistant Documentation

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation & Setup](#installation--setup)
4. [Project Structure](#project-structure)
5. [Core Components](#core-components)
   - [Main Application](#main-application)
   - [Configuration](#configuration)
   - [Agents](#agents)
   - [Utilities](#utilities)
6. [How to Run](#how-to-run)
7. [Code Explanation](#code-explanation)
   - [Main Files](#main-files)
   - [Agent Files](#agent-files)
   - [Utility Files](#utility-files)
8. [Next Steps & What I Still Have To Do](#next-steps--what-i-still-have-to-do)
9. [Troubleshooting](#troubleshooting)

## Overview

The AI Research Assistant is a multi-agent system powered by AI that automates the research process. 
It breaks down complex research questions into manageable subtasks, gathers information for each subtask, analyses the findings, 
and generates a cohesive research report. The system supports 3 languages so far, and features performance optimisations like 
caching and parallel processing, and provides a user-friendly Streamlit interface for when you want to test it. 
I have included in the documentation, instructions on how to test.

## System Requirements

- Python 3.8 or higher
- OPEN AI and/or Mistral AI API key
- Internet connection

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/busayoA/Research-Agent.git
   cd research-agent-project
   ```

2. **Create a virtual environment:**
    I recommend using a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a .env file with your API keys:**
   ```
   OPEN_API_KEY=your_openai_api_key_here
   MISTRAL_API_KEY=your_mistral_api_key_here
   ```

5. **Initialise the directory structure:**
   ```bash
   python setup.py
   ```

## Project Structure

```
research-agent-project/
├── agents/                      # Agent implementation files
│   ├── __init__.py              # Package initialisation
│   ├── task_manager.py          # Task manager agent for research question breakdown
│   ├── information_retrieval.py # Information retrievl agent for gathering subtask info
│   ├── analysis.py              # Information analysis agent for analysing the results
│   └── report_generator.py      # Report generator agent for creating the final report
├── utils/                       # Utility functions
│   ├── __init__.py              # Package initialisation
│   ├── caching.py               # Utility for caching responses
│   ├── language_detection.py    # Language detection for English, Spanish, and French
│   ├── ai_client.py             # Unified client for both AI providers
│   ├── client_manager.py        # Centralized client creation logic
│   ├── prompt_templates.py      # The system prompts
│   └── web_search.py            # A simulated search functionality (for now)
├── cache/                       # Cached API responses folder
├── reports/                     # Generated research reports folder
├── config.py                    # Configuration settings
├── main.py                      # The entry point fot the command line
├── streamlit_app.py             # The Streamlit web interface
├── setup.py                     # Setup script
├── requirements.txt             # Dependencies/required libraries
├── .env                         # Environment variables
└── README.md                    # Project documentation
```

## Core Components

### Main Application

- **streamlit_app.py**: The web interface for the research assistant built with Streamlit
- **main.py**: Command-line entry point for running the research process

### Configuration

- **config.py**: Central configuration file that manages API keys, model settings and parameters

### Agents

- **task_manager.py**: Analyses research questions and breaks them down into subtasks
- **information_retrieval.py**: Gathers information for each subtask using simulated search
- **analysis.py**: Processes collected information to identify key findings
- **report_generator.py**: Synthesizes analyses into a coherent research report

### Utilities

- **caching.py**: Implements a caching system to store and retrieve API responses
- **language_detection.py**: Detects the language of user queries (English, Spanish, French)
- **ai_client.py**: A unified client for the AI providers I use
- **client_manager.py**: Centralized client creation logic
- **prompt_templates.py**: This one contains the system prompts for each agent
- **web_search.py**: This is where web search functionality is simulated

## How to Run

### Using the Streamlit Interface (Recommended)

1. Start the Streamlit application:
   ```bash
   streamlit run streamlit_app.py
   ```

2. Ideally, the web browser should open automatically but if it doesn't, open your web browser and go to http://localhost:8501

3. Enter your API key(s) in the sidebar if not already set in .env

4. Type your research question in the text area and click "Start Research". If the question is not in English, the whole page will reset with the detected language

5. Monitor the progress bar and timer and view the generated report when complete

### If You Prefer to use the Command Line Instead of Streamlit

1. Run the main script:
   ```bash
   python main.py
   ```

2. Enter your research question when prompted

3. The script will run through all stages and save the report to the reports directory

## Explanation of the Code

### Main Files

#### `streamlit_app.py`

This file is the entrypoint UI and it implements the web interface using Streamlit:

- **Key Components:**
  - Session state management for tracking research progress
  - Language detection and UI adaptations based on detected language
  - Threading to prevent UI freezing during research (very useful in testing)
  - Real-time progress updates and status messages
  - Tabbed interface for viewing research reports and plans (so it is clear what the subtasks are)

- **Main Functions:**
  - `run_research_in_thread()`: Executes the research process in a separate thread
  - `start_research()`: Initialises and starts the research process
  - `process_updates()`: Handles updates from the research thread
  - `get_ui_text()`: Retrieves translated UI text based on detected language

```python
# Key pattern: Using a queue for thread communication
# line 40
st.session_state.update_queue = queue.Queue()

# line 176
thread = threading.Thread(
    target=run_research_in_thread,
    args=(research_question, api_key, st.session_state.update_queue),
    daemon=True
)
thread.start()
```

#### `main.py`

Provides a command-line interface for running the research assistant:

- **Key Functions:**
  - `run_research_assistant()`: Orchestrates the entire research process
  - `save_report()`: Saves the generated report to a file
  - `main()`: Entry point that handles user input and configuration

```python
# Core research process - line 9
def run_research_assistant(research_question):
    """
    Run the entire research assistant pipeline.
    
    Args:
        research_question (str): The research question to investigate.
        
    Returns:
        str: A research report answering the question.
    """
    print(f"Starting research on: {research_question}")
    
    # Step 1: Create my research plan
    print("Step 1: Creating research plan...")
    research_plan = create_research_plan(research_question)
    subtasks = research_plan.get("subtasks", [])
    print(f"Research plan created with {len(subtasks)} subtasks")
    
    # Step 2: Retrieve information for each subtask
    print("Step 2: Retrieving information...")
    information_collection = []
    for subtask in subtasks:
        print(f"  Retrieving information for subtask: {subtask['id']}")
        information = retrieve_information(subtask)
        information_collection.append(information)
        time.sleep(1)  # I use a teeny delay to avoid rate limits
    
    # Step 3: Analyse the information
    print("Step 3: Analysing information...")
    analyses = []
    for i, subtask in enumerate(subtasks):
        print(f"  Analysing information for subtask: {subtask['id']}")
        analysis = analyse_information(subtask, information_collection[i])
        analyses.append(analysis)
        time.sleep(1)  
    
    # Step 4: Generate the final report
    print("Step 4: Generating final report...")
    report = generate_report(research_question, analyses, subtasks)
    
    print("Research completed!")
    return report
```

#### `config.py`

Manages configuration settings for the application:

- Loads environment variables from the .env file
- Sets default values for model selection, temperature, and other parameters
- Provides functions for validation and configuration access

```python
# Environment variables with defaults
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "1500"))
```

#### `setup.py`

Initialises the project structure and dependencies:

- Creates necessary directories (agents, utils, reports)
- Sets up Python package initialisation files
- Installs required dependencies
- Creates environment file templates

```python
# line 12
def create_directory_structure():
    """Create the necessary directory structure for the project."""
    print("Creating directory structure...")
    
    # Create main directories if they don't exist
    directories = [
        'agents',
        'utils', 
        'reports'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
    
    print("Directory structure created successfully.\n")
```

### Agent Files

#### `task_manager.py`

Breaks down research questions into subtasks:

- **Key Functions:**
  - `create_research_plan()`: Analyses the research question and generates subtasks
  - `generate_additional_subtasks()`: Creates additional subtasks if needed
  - `generate_standard_subtasks()`: Provides fallback subtasks for any research question

- **Process:**
  1. Detects the language of the research question
  2. Sends a prompt to the AI model to break down the question
  3. Ensures at least 5 subtasks are created
  4. Returns a structured research plan with subtasks and search queries

```python
# Language detection integration - line 30
# Detect the language of the research question
language_code = detect_language(research_question)

# Get language-specific instructions
language_instruction = format_instructions_for_language(language_code)


# Ensure minimum number of subtasks - line 83
subtasks = research_plan.get("subtasks", [])
if len(subtasks) < 5:
    # Add more subtasks to reach at least 5
    existing_count = len(subtasks)
    additional_subtasks = generate_additional_subtasks(
        research_question, 5 - existing_count, existing_count, language_code
    )
    subtasks.extend(additional_subtasks)
```

#### `information_retrieval.py`

Gathers information for each subtask:

- **Key Functions:**
  - `retrieve_information()`: Processes a subtask to collect information
  - `process_single_query()`: Handles a single search query

- **Process:**
  1. Runs search queries in parallel using ThreadPoolExecutor
  2. Removes duplicate results based on URL
  3. Formats search results for the AI model prompt
  4. Generates a structured information collection for each subtask

```python
# Parallel processing with ThreadPoolExecutor - line 37
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
```

#### `analysis.py`

Analyses information collected for each subtask:

- **Key Functions:**
  - `analyse_information()`: Processes collected information to identify patterns and findings

- **Process:**
  1. Formats the information for the model prompt
  2. Sends the prompt to generate analysis
  3. Parses the response into a structured analysis
  4. Includes fallback mechanisms for parsing failures

```python
# Streamlined prompt with few finidings for faster processing and testing (for now) - line 41
human_prompt = f"""Analyse this information for the research subtask:

    Subtask: {subtask["description"]}

    Information:
    {information_text}

    Focus on 3-5 key findings and a brief summary."""

# Caching implementation - line 59
cache_key = generate_cache_key(get_model(), messages, TEMPERATURE)
        
# Check cache first
cached_response = get_cached_response(cache_key)
```

#### `report_generator.py`

Synthesizes analyses into a coherent research report:

- **Key Functions:**
  - `generate_report()`: Creates a comprehensive research report based on analyses

- **Process:**
  1. Maps subtask IDs to descriptions
  2. Formats analyses for the prompt
  3. Adds language-specific instructions
  4. Generates a markdown-formatted research report

```python
# Get language-specific instructions - line 52
language_instruction = format_instructions_for_language(language_code)
    
# TEMPORARY streamlined prompt for faster processing, with language instruction
human_prompt = f"""Generate a concise research report for:
    Research Question: {research_question}

    Analyses:
    {analyses_text}

    Keep the report focused and under 2000 words.

    {language_instruction}"""
```

### Utility Files

#### `caching.py`

Implements a caching system to reduce API calls and increase speed:

- **Key Functions:**
  - `generate_cache_key()`: Creates a unique hash for caching
  - `get_cached_response()`: Retrieves cached responses
  - `cache_response()`: Stores responses in the cache

```python
# line 11
def generate_cache_key(model, messages, temperature, max_tokens=None):
    """
    Generate a unique cache key based on request parameters
    
    Args:
        model (str): The model name
        messages (list): The messages list
        temperature (float): The temperature setting
        max_tokens (int, optional): Maximum tokens limit
        
    Returns:
        str: A hexadecimal cache key
    """
    # Convert messages to a string representation
    message_str = json.dumps(messages, sort_keys=True)
    
    # Create a unique identifier from all parameters
    params_str = f"{model}_{message_str}_{temperature}_{max_tokens}"
    
    # Generate MD5 hash
    return hashlib.md5(params_str.encode('utf-8')).hexdigest()
```

#### `language_detection.py`

Handles language detection and translation:

- **Key Functions:**
  - `detect_language()`: Determines the language of input text
  - `format_instructions_for_language()`: Provides language-specific instructions

```python
# line 4
def detect_language(text):
    """
    Detect the language of a given text (limited to English, French, and Spanish).
    
    Args:
        text (str): The text to analyse
        
    Returns:
        str: The detected language code ('en', 'fr', 'es')
    """
    # Dictionary of language-specific characters and common words
    language_markers = {
        'en': ['the', 'and', 'is', 'of', 'to', 'in', 'a', 'for', 'that', 'with', 'you', 'it', 'not', 'on', 'this'],
        'es': ['el', 'la', 'los', 'las', 'y', 'en', 'de', 'que', 'es', 'un', 'una', 'por', 'con', 'para', 'como'],
        'fr': ['le', 'la', 'les', 'et', 'en', 'un', 'une', 'des', 'du', 'est', 'que', 'pour', 'dans', 'ce', 'pas']
    }
    
    # Normalize and tokenize text
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    
    # Count occurrences of language-specific words
    language_scores = {}
    for lang, markers in language_markers.items():
        word_count = sum(1 for word in words if word in markers)
        if words:
            language_scores[lang] = word_count / len(words)
        else:
            language_scores[lang] = 0
    
    # Return the language with the highest score
    if not language_scores:
        return 'en'  # Default to English if no matches
    
    best_language = max(language_scores.items(), key=lambda x: x[1])
    
    # If the best score is too low, default to English
    if best_language[1] < 0.05:
        return 'en'
        
    return best_language[0]
```

#### `prompt_templates.py`

Contains system prompts for each agent:

- Defines structured prompts for different research phases
- Includes human-like prompts for more natural interactions
- Optimised for JSON output format

```python
TASK_MANAGER_SYSTEM_PROMPT = """
You are a Task Manager Agent in a research assistant system. Your job is to:
1. Interpret user research requests
2. Break down complex questions into AT LEAST 5 specific, focused subtasks
3. Create a structured research plan

Return your response as a JSON object with the following structure:
{
    "research_question": "The main research question",
    "subtasks": [
        {
            "id": "subtask-1",
            "description": "Description of subtask 1",
            "search_queries": ["query 1", "query 2"]
        },
        ...
    ]
}

You MUST create AT LEAST 5 distinct subtasks. For complex topics, you may create more if necessary.
Each subtask should have 1-2 search queries. Be thorough and comprehensive in your breakdown.
"""
```

#### `web_search.py`

Simulates web search functionality:

- **Key Functions:**
  - `simulated_search()`: Creates mock search results using an AI model
  - `search_and_process()`: Processes search queries

## Next Steps & What I Still Have To Do

1. Deploy onto Azure

2. Migrate the codebase to Cursor

3. Implementing real web searching

4. Using more AI models

5. Adding new languages

## Troubleshooting

### API Key Issues

**Problem**: "API key is not set" or authentication errors
**Solution**: 
1. Check that your API key is correctly set in the `.env` file
2. Verify the API key is valid and has sufficient credits
3. Enter the API key manually in the Streamlit interface

### JSON Parsing Errors

**Problem**: Agent failures due to malformed JSON responses
**Solution**:
1. Check the logs for the exact error message
2. The system includes fallback mechanisms, but you can adjust them in each agent file
3. Try with a different model (larger models tend to produce more reliable results)

### Language Detection Issues

**Problem**: Incorrect language detection for short or ambiguous queries
**Solution**:
1. Add more context to your query
2. Manually specify a language with a tag (e.g., "[ES] ¿Cómo funciona...")

### Performance Issues

**Problem**: Slow response times
**Solution**:
1. Use a different model 
2. Enable caching if it's disabled
3. Reduce `MAX_TOKENS` in `config.py`
4. Check your internet connection speed

### Startup Errors

**Problem**: Application fails to start
**Solution**:
1. Verify all dependencies are installed: `pip install -r requirements.txt`
2. Check for Python version compatibility (3.8+ required)
3. Run `python setup.py` to ensure proper directory structure
4. Check Streamlit installation: `streamlit hello` to verify

Thank you for your consideration!
