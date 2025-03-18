[5/10/2024]
I only just learnt what an Agent is but I'm going to do this and do it well
1. Project plan:
- What is the core concept of this project? 
    - A multi-agent system thatis capable of breaking a research prompt into subtasks 

2. How do I start?
    - Simple setup. I need either a UI or CLI app (I'm thinking streamlit)
    - always have an env and a config file + requirements.txt
    - maybe have a single file in the future that does the config set up for me incase I need to switch IDEs later
    - API keys are a must have, Busayo

3. Everything should be modularised
    - Agents for the actual agents
    - utils for generic tasks

Each agent should be its own separate component - this is the whole point of an Agent

Web interface - start with something simple using streamlit

I need somehwere to store the reports
Probably think of adding some sort of caching mechanism for faster processing
I want it to be multilingual (once I figure out how to do that)


[6/10/2024]
So, looking at things, I need some kind of wrapper class to call the model's API client.
- It should check for the API key and describe what needs to happen if there is an error
- needs a caching.py file for caching queries
- needs a module for language detection possibly
- prompts on prompts on prompts: how many prompts could I possibly need for all of this?


[12/10/2024]
AGENTS
some sort of agent that acts as a query manager to break down research questions and then retrieves the relevant info
- but then I need to analyse this for the report

Decisions:
    - query_manager.py
    - information_retrieval.py

More decisions:
- A file to house my precious prompts (I love a good alliteration) - should probably go in utils because it's not an agent in itself
- The prompts should probably, actually (definitely) be *templates* that guide the model on how to execute the task



[13/10/2024]
THE HARD PART
- How do you even do a web search via an API call? I don't know YET but I think for now, we simulate one. 
So instead of web searching, I can make a call to the actual model itself for now. When I have time off work, 
I can buckle down and figure out the web search!

TODAY'S CONCLUSION
- Calling APIs rules! 
I got it to work on the CLI. My streamlit app is... well, it sucks lol
I guess the next step is to get that up and running

    Priorities
    - Do I:
        1. Focus on the streamlit UI now?
        2. Or do I start working on the web search?

    I vote for the UI because it seems like it will be a quicker issue to solve. 
    My thinking is that the sooner I have a UI with simulated web search working, the sooner I can start testing with Fikayo.


[19/10/2024]
PROGRESS! My UI is functional... ish. Some buttons don't work but it's progress regardless.
I'm thinking – caching is next. I know enough about it to make decent code that works 

- SIDE BAR: I started working on the web search lol. I couldn't help my curiousity. I think I've made a good start but I am still
a bit lost on how to integrate it to the rest of the code in a functional manner

    - SIDE-BAR IN THIS SIDE-BAR: The web search did not work and it broke my code lol. I've rolled back my changes and will stick to a simulated web search until I have proper time to really tackle this case

- CLOSING REMARKS: I have a functional web search simulation but it is soooooooo slow. My next task is to troubleshoot for 
speed optimisation because I don't have time to wait ages for results

[9/11/2024]
Okay, so my simulated web search works better now (I swapped out the models and I am now using the smallest one, RIP Mistral Large & GPT-4o - for now)
So, web_search.py now exists as a temporary solution for search functionality. Next, we cache!

So what does caching entail? I want to:
1. create some kind of key to always be able to locate a cached item
2. be able to create a cached response and store it alongside its key
3. be able to retrieve a cached response from the backend
4. integrate the caching feature with both the backend and the frontend


END-OF-DAY NOTES
- I think I've got the caching down. The only problem now, is after running for a few minutes, my UI crashes, so that's fun.
I'm too tired to solve it now so we come back tomorrow.


[10/11/2024]
I'm back and better than yesterday so let's get it!
Today, I'm going to focus on further modularisation of the agents. I only have 2 now but I can easily see where 
query_manager and information_retrieval can both be broken down further to split things into modules.


WHAT DID I ACHIEVE TODAY?
1. I updated information_retrieval for STRICTLY gathering information
2. I built analysis for processing collected information
3. I developed report_generator for generating final reports
4. I renamed query_manager to task_manager because it seems more fitting
5. I got the UI to stop crashing by using something called Threading - very interesting discovery I made today


[29/11/2024]
I have zero motivation to work but let's do this. Today's task:
1. refine the prommpt tempaltes into something more standardised
2. do research on the web searching implementation
3. look into making the system multilingual

END-OF-DAY NOTES:
1. Prompt templates are better than they were and it is reflected in the results. I'm happy with today's progress
2. I think I might have to use Le Chat to help me build out the multilungual support part
3. I might also need some help from le chat to figure out web searching


[10/01/2025]
Happy new year!
Today, I will be working with Le Chat to make my baby multilingual!

NOTES ON LE CHAT:
- Very good code that does exactly what I asked for
- The provided code was functional but I had to do a lot of re-formatting
- Also, it spells analyse as 'analyze' which I don't like. I can probably ask it to use British spellings

WHAT DID I ACHIEVE TODAY?
1. I made the system able to accept inputs in different languages and respond in these detected languages
2. I got started on the documentation for Fikayo

[08/02/2025]
Today, we focus on testing and finding bugs. These will be recorded in a new file I have created called 'issues'

NEW THINGS I ADDED TODAY
1. I implemented threading to prevent UI freezing
2. I added progress tracking and visualization
3. I implemented parallel processing for search queries
4. I had to downsize parameters to speed up processing because things were still going a bit slow
5. I added fallback mechanisms for error handling so that the system doesn't simply crash when an error is raised


[22/02/2025]
Today's themes are... DOCUMENTATION AND CODE COMMENTS!!!!

NEW THINGS I ADDED TODAY
1. I created a comprehensive README.md as documentation
2. I added hella inline code comments
3. I tested with aa bunch of different research questions and languages


[15/03/2025]
1. Updated documentation
2. Created GitHub Repo and pushed


[16/03/2025]
1. Removed notes folder from gitignore definition and pushed to GitHub