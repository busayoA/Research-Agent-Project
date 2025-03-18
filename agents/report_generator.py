import os
from config import get_model, TEMPERATURE, MAX_TOKENS
from utils.prompt_templates import REPORT_GENERATOR_SYSTEM_PROMPT
from utils.caching import generate_cache_key, get_cached_response, cache_response
from utils.language_detection import format_instructions_for_language
from utils.client_manager import get_client

def generate_report(research_question, analyses, subtasks, language_code='en'):
    """
    Generate a comprehensive research report based on analysed information.
    
    Args:
        research_question (str): The main research question.
        analyses (list): A list of analyses for each subtask.
        subtasks (list): A list of subtasks from the research plan.
        language_code (str): The language to use for the report
        
    Returns:
        str: A formatted research report.
    """
    try:
        # Create a mapping of subtask IDs to descriptions
        subtask_map = {subtask["id"]: subtask["description"] for subtask in subtasks}
        
        # Format the analyses for the prompt - more concise for speed
        formatted_analyses = []
        for analysis in analyses:
            subtask_id = analysis.get("subtask_id")
            subtask_description = subtask_map.get(subtask_id, "Unknown subtask")
            
            analysis_data = analysis.get("analysis", {})
            key_findings = analysis_data.get("key_findings", [])[:3]  # Limit to top 3 findings
            summary = analysis_data.get("summary", "No summary available.")
            
            formatted_analyses.append(
                f"Subtask: {subtask_description}\n"
                f"Key Findings: " + "; ".join([f"{finding}" for finding in key_findings]) + "\n"
                f"Summary: {summary}"
            )
        
        # Join the formatted analyses
        analyses_text = "\n\n".join(formatted_analyses)
        
        # Get language-specific instructions
        language_instruction = format_instructions_for_language(language_code)
        
        # Streamlined prompt for faster processing, with language instruction
        human_prompt = f"""Generate a concise research report for:
            Research Question: {research_question}

            Analyses:
            {analyses_text}

            Keep the report focused and under 2000 words.

            {language_instruction}"""
        
        # Get the client from client manager
        client = get_client()
        
        # Generate cache key
        messages = [
            {"role": "system", "content": REPORT_GENERATOR_SYSTEM_PROMPT},
            {"role": "user", "content": human_prompt}
        ]
        cache_key = generate_cache_key(get_model(), messages, TEMPERATURE, MAX_TOKENS)
        
        # Check cache first
        cached_response = get_cached_response(cache_key)
        if cached_response:
            print(f"Using cached report for: {research_question}")
            report = cached_response.choices[0].message.content
        else:
            # Call the API
            response = client.chat.create(
                model=get_model(),
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            # Cache the response
            cache_response(cache_key, response)
            
            # Extract the content
            report = response.choices[0].message.content
        
        return report
    except Exception as e:
        print(f"Error in generate_report: {e}")
        
    # Verify language code is supported, default to English if not
    # system is currently limited to the languages I speak
    if language_code not in ['en', 'es', 'fr']:
        language_code = 'en'
    
    # Return a simple report on error in the appropriate language
    if language_code == 'en':
        return f"""
            # Research Report: {research_question}

            ## Introduction
            This report provides a brief overview of the research question: "{research_question}"

            ## Key Findings
            - Research was conducted on this topic
            - Information was collected and analysed
            - Some insights were generated

            ## Conclusion
            The research provides initial insights, but further investigation may be needed for a more comprehensive understanding.
            """
    elif language_code == 'es':
        return f"""
                # Informe de Investigación: {research_question}

                ## Introducción
                Este informe proporciona una breve descripción general de la pregunta de investigación: "{research_question}"

                ## Hallazgos Clave
                - Se realizó una investigación sobre este tema
                - Se recopiló y analizó información
                - Se generaron algunos conocimientos

                ## Conclusión
                La investigación proporciona conocimientos iniciales, pero puede ser necesaria una investigación adicional para una comprensión más completa.
                """
    else:  # French
        return f"""
            # Rapport de Recherche : {research_question}

            ## Introduction
            Ce rapport fournit un bref aperçu de la question de recherche : "{research_question}"

            ## Principales Conclusions
            - Des recherches ont été menées sur ce sujet
            - Des informations ont été collectées et analysées
            - Certaines perspectives ont été générées

            ## Conclusion
            La recherche fournit des perspectives initiales, mais des recherches supplémentaires peuvent être nécessaires pour une compréhension plus complète.
            """