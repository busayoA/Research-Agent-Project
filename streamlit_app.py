import streamlit as st
import time
import json
import os
import threading
import queue
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check for API keys first
from config import MISTRAL_API_KEY, OPENAI_API_KEY, get_provider, set_provider, set_model, validate_api_key
from utils.language_detection import detect_language

# Initialise session state variables
if "research_status" not in st.session_state:
    st.session_state.research_status = None
if "research_progress" not in st.session_state:
    st.session_state.research_progress = 0
if "research_message" not in st.session_state:
    st.session_state.research_message = ""
if "research_report" not in st.session_state:
    st.session_state.research_report = ""
if "subtasks" not in st.session_state:
    st.session_state.subtasks = []
if "mistral_api_key" not in st.session_state:
    st.session_state.mistral_api_key = ""
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ""
if "thread_error" not in st.session_state:
    st.session_state.thread_error = None
if "update_queue" not in st.session_state:
    st.session_state.update_queue = queue.Queue()
if "research_complete" not in st.session_state:
    st.session_state.research_complete = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "elapsed_time" not in st.session_state:
    st.session_state.elapsed_time = 0
if "language_code" not in st.session_state:
    st.session_state.language_code = "en"
if "ai_provider" not in st.session_state:
    st.session_state.ai_provider = get_provider()

# Function to check if we have the necessary API key
def check_api_key():
    """Check if the required API key is set based on the selected provider"""
    provider = st.session_state.ai_provider
    
    if provider == "mistral":
        if not MISTRAL_API_KEY and not st.session_state.mistral_api_key:
            return False
    else:  # openai
        if not OPENAI_API_KEY and not st.session_state.openai_api_key:
            return False
    return True

# Function to handle provider change
def on_provider_change():
    """Handle change in AI provider selection"""
    set_provider(st.session_state.ai_provider)

# This function will run in a separate thread and communicate via the queue
def run_research_in_thread(research_question, mistral_api_key, openai_api_key, provider, update_queue):
    """
    Run the research process in a separate thread and communicate with the main thread via a queue.
    """
    try:
        # Set API keys from session state if provided
        if mistral_api_key:
            os.environ["MISTRAL_API_KEY"] = mistral_api_key
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # Set the provider
        set_provider(provider)
        
        # Detect language of the research question
        language_code = detect_language(research_question)
        update_queue.put({"language_code": language_code})
        
        # Send status update
        update_queue.put({"status": "running", "message": "Creating research plan...", "progress": 10})
        
        # Import here to avoid circular imports
        from agents.task_manager import create_research_plan
        
        # Step 1: Create a research plan
        research_plan = create_research_plan(research_question)
        subtasks = research_plan.get("subtasks", [])
        
        # Store the language code from the research plan
        language_code = research_plan.get("language", "en")
        update_queue.put({"language_code": language_code})
        
        # Send plan update
        update_queue.put({
            "status": "running", 
            "message": f"Research plan created with {len(subtasks)} subtasks", 
            "progress": 20,
            "subtasks": subtasks
        })
        
        # Step 2: Retrieve information for each subtask
        from agents.information_retrieval import retrieve_information
        
        information_collection = []
        for i, subtask in enumerate(subtasks):
            update_queue.put({
                "status": "running",
                "message": f"Retrieving information for subtask {i+1}/{len(subtasks)}: {subtask['description']}",
                "progress": 20 + int((i + 1) * 40 / len(subtasks))
            })
            
            information = retrieve_information(subtask)
            information_collection.append(information)
        
        # Step 3: Analyse the information
        from agents.analysis import analyse_information
        
        analyses = []
        for i, subtask in enumerate(subtasks):
            update_queue.put({
                "status": "running",
                "message": f"Analyzing information for subtask {i+1}/{len(subtasks)}: {subtask['description']}",
                "progress": 60 + int((i + 1) * 30 / len(subtasks))
            })
            
            analysis = analyse_information(subtask, information_collection[i])
            analyses.append(analysis)
        
        # Step 4: Generate the final report
        from agents.report_generator import generate_report
        
        update_queue.put({"status": "running", "message": "Generating final report...", "progress": 90})
        
        report = generate_report(research_question, analyses, subtasks, language_code)
        
        # Save the report to a file
        output_dir = "./reports"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a filename based on the research question
        filename = research_question.lower().replace(" ", "_")[:50]
        filename = "".join(c for c in filename if c.isalnum() or c == "_")
        filename = f"{filename}_{int(time.time())}.md"
        
        # Save the report
        with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
            f.write(report)
        
        # Send completion update
        update_queue.put({
            "status": "completed",
            "message": "Research completed successfully!",
            "progress": 100,
            "report": report
        })
        
    except Exception as e:
        # Send error update
        update_queue.put({
            "status": "error",
            "message": f"Error: {str(e)}",
            "progress": 0
        })

def start_research(research_question):
    """Start a new research process"""
    # Get the API keys to pass to the thread
    mistral_api_key = st.session_state.mistral_api_key if st.session_state.mistral_api_key else MISTRAL_API_KEY
    openai_api_key = st.session_state.openai_api_key if st.session_state.openai_api_key else OPENAI_API_KEY
    provider = st.session_state.ai_provider
    
    # Reset state
    st.session_state.research_status = "starting"
    st.session_state.research_progress = 0
    st.session_state.research_message = "Initialising research..."
    st.session_state.research_report = ""
    st.session_state.subtasks = []
    st.session_state.thread_error = None
    st.session_state.update_queue = queue.Queue()
    st.session_state.research_complete = False
    st.session_state.start_time = time.time()
    st.session_state.elapsed_time = 0
    st.session_state.language_code = detect_language(research_question)
    
    # Create and start the thread
    thread = threading.Thread(
        target=run_research_in_thread,
        args=(research_question, mistral_api_key, openai_api_key, provider, st.session_state.update_queue),
        daemon=True
    )
    thread.start()

# Process updates from the queue
def process_updates():
    """Process updates from the queue and update session state"""
    try:
        while not st.session_state.update_queue.empty():
            update = st.session_state.update_queue.get_nowait()
            
            # Update session state based on the update from the thread
            if "status" in update:
                st.session_state.research_status = update["status"]
            
            if "message" in update:
                st.session_state.research_message = update["message"]
            
            if "progress" in update:
                st.session_state.research_progress = update["progress"]
            
            if "subtasks" in update:
                st.session_state.subtasks = update["subtasks"]
            
            if "report" in update:
                st.session_state.research_report = update["report"]
                st.session_state.research_complete = True
                
            if "language_code" in update:
                st.session_state.language_code = update["language_code"]
                
    except Exception as e:
        st.session_state.thread_error = str(e)
    
    # Update elapsed time if research is ongoing
    if st.session_state.start_time and st.session_state.research_status in ["starting", "running"]:
        st.session_state.elapsed_time = time.time() - st.session_state.start_time

# Format elapsed time as mm:ss
def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

# Get translated UI text based on detected language
def get_ui_text(key, language_code='en'):
    """Get UI text in the appropriate language (English, Spanish, or French)"""
    translations = {
        'title': {
            'en': "AI Research Assistant (Multilingual)",
            'es': "Asistente de Investigación IA (Multilingüe)",
            'fr': "Assistant de Recherche IA (Multilingue)"
        },
        'about_header': {
            'en': "About",
            'es': "Acerca de",
            'fr': "À propos"
        },
        'about_text': {
            'en': "This research assistant uses AI to:\n\n1. Break down your research question\n2. Gather information on each subtask\n3. Analyse the collected information\n4. Generate a research report\n\nOptimised for speed with caching and parallel processing. Responds in English, Spanish, or French based on your query.",
            'es': "Este asistente de investigación utiliza IA para:\n\n1. Desglosar su pregunta de investigación\n2. Recopilar información sobre cada subtarea\n3. Analizar la información recopilada\n4. Generar un informe de investigación\n\nOptimizado para velocidad con almacenamiento en caché y procesamiento paralelo. Responde en inglés, español o francés según su consulta.",
            'fr': "Cet assistant de recherche utilise l'IA pour :\n\n1. Décomposer votre question de recherche\n2. Recueillir des informations sur chaque sous-tâche\n3. Analyser les informations collectées\n4. Générer un rapport de recherche\n\nOptimisé pour la vitesse avec mise en cache et traitement parallèle. Répond en anglais, espagnol ou français selon votre requête."
        },
        'settings_header': {
            'en': "Settings",
            'es': "Configuración",
            'fr': "Paramètres"
        },
        'provider': {
            'en': "Select AI Provider:",
            'es': "Seleccionar Proveedor de IA:",
            'fr': "Sélectionner le Fournisseur d'IA:"
        },
        'language_selection': {
            'en': "Interface Language:",
            'es': "Idioma de la Interfaz:",
            'fr': "Langue de l'Interface:"
        },
        'mistral': {
            'en': "Mistral AI",
            'es': "Mistral AI",
            'fr': "Mistral AI"
        },
        'openai': {
            'en': "OpenAI",
            'es': "OpenAI",
            'fr': "OpenAI"
        },
        'mistral_api_key': {
            'en': "Mistral API Key:",
            'es': "Clave API de Mistral:",
            'fr': "Clé API Mistral:"
        },
        'openai_api_key': {
            'en': "OpenAI API Key:",
            'es': "Clave API de OpenAI:",
            'fr': "Clé API OpenAI:"
        },
        'intro': {
            'en': "This tool helps you conduct research on any topic by breaking down your question into subtasks, gathering and analyzing information, and generating a comprehensive report. Available in English, Spanish, and French.",
            'es': "Esta herramienta le ayuda a realizar investigaciones sobre cualquier tema, desglosando su pregunta en subtareas, recopilando y analizando información, y generando un informe completo. Disponible en inglés, español y francés.",
            'fr': "Cet outil vous aide à mener des recherches sur n'importe quel sujet en décomposant votre question en sous-tâches, en recueillant et en analysant des informations, et en générant un rapport complet. Disponible en anglais, espagnol et français."
        },
        'model_select_label_mistral': {
            'en': "Select Mistral Model:",
            'es': "Seleccionar modelo Mistral:",
            'fr': "Sélectionner le modèle Mistral:"
        },
        'model_select_label_openai': {
            'en': "Select OpenAI Model:",
            'es': "Seleccionar modelo OpenAI:",
            'fr': "Sélectionner le modèle OpenAI:"
        },
        'mistral_fastest': {
            'en': "Mistral Small (Fastest ⚡)",
            'es': "Mistral Small (Más rápido ⚡)",
            'fr': "Mistral Small (Plus rapide ⚡)"
        },
        'mistral_balanced': {
            'en': "Mistral Medium (Balanced)",
            'es': "Mistral Medium (Equilibrado)",
            'fr': "Mistral Medium (Équilibré)"
        },
        'mistral_capable': {
            'en': "Mistral Large (Most Capable)",
            'es': "Mistral Large (Más capaz)",
            'fr': "Mistral Large (Plus performant)"
        },
        'openai_turbo': {
            'en': "GPT-3.5 Turbo (Fastest ⚡)",
            'es': "GPT-3.5 Turbo (Más rápido ⚡)",
            'fr': "GPT-3.5 Turbo (Plus rapide ⚡)"
        },
        'openai_4turbo': {
            'en': "GPT-4 Turbo (Balanced)",
            'es': "GPT-4 Turbo (Equilibrado)",
            'fr': "GPT-4 Turbo (Équilibré)"
        },
        'openai_4o': {
            'en': "GPT-4o (Most Capable)",
            'es': "GPT-4o (Más capaz)",
            'fr': "GPT-4o (Plus performant)"
        },
        'perf_header': {
            'en': "Performance",
            'es': "Rendimiento",
            'fr': "Performance"
        },
        'use_cache': {
            'en': "Use Cache",
            'es': "Usar caché",
            'fr': "Utiliser le cache"
        },
        'cache_help': {
            'en': "Speeds up repeated research by saving previous results",
            'es': "Acelera la investigación repetida guardando resultados anteriores",
            'fr': "Accélère les recherches répétées en sauvegardant les résultats précédents"
        },
        'clear_cache': {
            'en': "Clear Cache",
            'es': "Limpiar caché",
            'fr': "Vider le cache"
        },
        'cache_cleared': {
            'en': "Cache cleared!",
            'es': "¡Caché limpiado!",
            'fr': "Cache vidé !"
        },
        'clear_results': {
            'en': "Clear Results",
            'es': "Borrar resultados",
            'fr': "Effacer les résultats"
        },
        'api_warning': {
            'en': "No Mistral API key found. Please enter your API key in the sidebar to use this service.",
            'es': "No se encontró la clave API de Mistral. Por favor, ingrese su clave API en la barra lateral para usar este servicio.",
            'fr': "Aucune clé API Mistral trouvée. Veuillez entrer votre clé API dans la barre latérale pour utiliser ce service."
        },
        'openai_api_warning': {
            'en': "No OpenAI API key found. Please enter your API key in the sidebar to use this service.",
            'es': "No se encontró la clave API de OpenAI. Por favor, ingrese su clave API en la barra lateral para usar este servicio.",
            'fr': "Aucune clé API OpenAI trouvée. Veuillez entrer votre clé API dans la barre latérale pour utiliser ce service."
        },
        'question_placeholder': {
            'en': "e.g., What are the implications of quantum computing on cybersecurity?",
            'es': "p. ej., ¿Cuáles son las implicaciones de la computación cuántica en la ciberseguridad?",
            'fr': "ex., Quelles sont les implications de l'informatique quantique sur la cybersécurité?"
        },
        'start_research': {
            'en': "Start Research",
            'es': "Comenzar investigación",
            'fr': "Démarrer la recherche"
        },
        'enter_question': {
            'en': "Please enter a research question.",
            'es': "Por favor, ingrese una pregunta de investigación.",
            'fr': "Veuillez entrer une question de recherche."
        },
        'provide_api_key': {
            'en': "Please provide a valid API key in the sidebar.",
            'es': "Por favor, proporcione una clave API válida en la barra lateral.",
            'fr': "Veuillez fournir une clé API valide dans la barre latérale."
        },
        'progress_title': {
            'en': "Research in Progress",
            'es': "Investigación en progreso",
            'fr': "Recherche en cours"
        },
        'time_elapsed': {
            'en': "Time Elapsed",
            'es': "Tiempo transcurrido",
            'fr': "Temps écoulé"
        },
        'research_plan': {
            'en': "Research Plan",
            'es': "Plan de investigación",
            'fr': "Plan de recherche"
        },
        'subtask': {
            'en': "Subtask",
            'es': "Subtarea",
            'fr': "Sous-tâche"
        },
        'search_queries': {
            'en': "Search Queries",
            'es': "Consultas de búsqueda",
            'fr': "Requêtes de recherche"
        },
        'completed': {
            'en': "Research completed in",
            'es': "Investigación completada en",
            'fr': "Recherche terminée en"
        },
        'report_tab': {
            'en': "Report",
            'es': "Informe",
            'fr': "Rapport"
        },
        'plan_tab': {
            'en': "Research Plan",
            'es': "Plan de investigación",
            'fr': "Plan de recherche"
        },
        'download_report': {
            'en': "Download Report as Markdown",
            'es': "Descargar informe como Markdown",
            'fr': "Télécharger le rapport au format Markdown"
        },
        'try_again': {
            'en': "Try Again",
            'es': "Intentar de nuevo",
            'fr': "Réessayer"
        },
        'footer': {
            'en': "Built with Streamlit and AI | Supporting English, Spanish, and French",
            'es': "Creado con Streamlit e IA | Compatible con inglés, español y francés",
            'fr': "Construit avec Streamlit et IA | Prend en charge l'anglais, l'espagnol et le français"
        }
    }
    
    # Default to English if the language or key is not found
    if key not in translations or language_code not in translations[key]:
        return translations[key].get('en', f"Missing: {key}")
    
    return translations[key][language_code]
    
    # Default to English if the language or key is not found
    if key not in translations or language_code not in translations[key]:
        return translations[key].get('en', f"Missing: {key}")
    
    return translations[key][language_code]

# Main UI layout
language_code = st.session_state.language_code
st.title(get_ui_text('title', language_code))
st.markdown(get_ui_text('intro', language_code))

# Sidebar for configuration
with st.sidebar:
    st.header(get_ui_text('about_header', language_code))
    st.markdown(get_ui_text('about_text', language_code))
    
    st.header(get_ui_text('settings_header', language_code))
    
    # Provider selection
    provider_options = {
        "mistral": get_ui_text('mistral', language_code),
        "openai": get_ui_text('openai', language_code)
    }
    
    st.selectbox(
        get_ui_text('provider', language_code),
        list(provider_options.keys()),
        format_func=lambda x: provider_options[x],
        key="ai_provider",
        on_change=on_provider_change
    )
    
    # API Key inputs based on provider
    if st.session_state.ai_provider == "mistral":
        if not MISTRAL_API_KEY:
            st.session_state.mistral_api_key = st.text_input(get_ui_text('mistral_api_key', language_code), type="password", value=st.session_state.mistral_api_key)
            if st.session_state.mistral_api_key:
                os.environ["MISTRAL_API_KEY"] = st.session_state.mistral_api_key
        
        # Mistral Model selection
        mistral_model_options = {
            "mistral-small-latest": get_ui_text('mistral_fastest', language_code),
            "mistral-medium-latest": get_ui_text('mistral_balanced', language_code),
            "mistral-large-latest": get_ui_text('mistral_capable', language_code)
        }
        
        selected_model = st.selectbox(
            get_ui_text('model_select_label_mistral', language_code),
            list(mistral_model_options.keys()),
            index=0,  # Default to small/fastest
            format_func=lambda x: mistral_model_options[x]
        )
        
        # Set the selected model in the environment
        set_model(selected_model)
    else:  # OpenAI
        if not OPENAI_API_KEY:
            st.session_state.openai_api_key = st.text_input(get_ui_text('openai_api_key', language_code), type="password", value=st.session_state.openai_api_key)
            if st.session_state.openai_api_key:
                os.environ["OPENAI_API_KEY"] = st.session_state.openai_api_key
        
        # OpenAI Model selection
        openai_model_options = {
            "gpt-3.5-turbo": get_ui_text('openai_turbo', language_code),
            "gpt-4-turbo": get_ui_text('openai_4turbo', language_code),
            "gpt-4o": get_ui_text('openai_4o', language_code)
        }
        
        selected_model = st.selectbox(
            get_ui_text('model_select_label_openai', language_code),
            list(openai_model_options.keys()),
            index=0,  # Default to 3.5 Turbo
            format_func=lambda x: openai_model_options[x]
        )
        
        # Set the selected model in the environment
        set_model(selected_model)
    
    # Cache control
    st.subheader(get_ui_text('perf_header', language_code))
    
    use_cache = st.checkbox(get_ui_text('use_cache', language_code), value=True, help=get_ui_text('cache_help', language_code))
    if not use_cache:
        if st.button(get_ui_text('clear_cache', language_code)):
            import shutil
            if os.path.exists("cache"):
                shutil.rmtree("cache")
                os.makedirs("cache")
                st.success(get_ui_text('cache_cleared', language_code))
    
    # Button to clear results
    if st.button(get_ui_text('clear_results', language_code)):
        st.session_state.research_status = None
        st.session_state.research_progress = 0
        st.session_state.research_message = ""
        st.session_state.research_report = ""
        st.session_state.subtasks = []
        st.session_state.research_complete = False
        st.session_state.start_time = None
        st.session_state.elapsed_time = 0
        st.rerun()

# Check if we have the necessary API key
api_available = check_api_key()

if not api_available:
    st.warning(get_ui_text('api_warning', language_code))

# Input form
with st.form("research_form"):
    research_question = st.text_area(
        "Enter your research question:",
        placeholder=get_ui_text('question_placeholder', language_code),
        height=100
    )
    
    submit = st.form_submit_button(get_ui_text('start_research', language_code))
    
    if submit:
        if not research_question:
            st.error(get_ui_text('enter_question', language_code))
        elif not api_available:
            st.error(get_ui_text('provide_api_key', language_code))
        else:
            start_research(research_question)

# Process any updates from the queue
if st.session_state.research_status in ["starting", "running"]:
    process_updates()
    # Update language code based on detected language
    language_code = st.session_state.language_code

# Progress tracking
if st.session_state.research_status in ["starting", "running"]:
    st.subheader(get_ui_text('progress_title', language_code))
    
    # Show both progress bar and elapsed time
    col1, col2 = st.columns([3, 1])
    with col1:
        progress_bar = st.progress(st.session_state.research_progress / 100)
    with col2:
        st.metric(get_ui_text('time_elapsed', language_code), format_time(st.session_state.elapsed_time))
    
    # Use a spinner to indicate activity
    with st.spinner(st.session_state.research_message):
        status_container = st.empty()
        status_container.info(st.session_state.research_message)
    
    # If we have subtasks, display them
    if st.session_state.subtasks:
        with st.expander(get_ui_text('research_plan', language_code), expanded=True):
            for i, subtask in enumerate(st.session_state.subtasks):
                if st.session_state.research_progress > 20 + (i * 15):
                    st.success(f"**{get_ui_text('subtask', language_code)} {i+1}:** {subtask['description']}")
                else:
                    st.markdown(f"**{get_ui_text('subtask', language_code)} {i+1}:** {subtask['description']}")
                st.markdown(f"{get_ui_text('search_queries', language_code)}: " + ", ".join([f"`{q}`" for q in subtask['search_queries']]))
    
    # Auto-refresh the page to update status
    if not st.session_state.research_complete:
        time.sleep(0.5)  # Shorter refresh time for more responsive UI
        st.rerun()

# Display results if completed
if st.session_state.research_status == "completed":
    st.success(f"{get_ui_text('completed', language_code)} {format_time(st.session_state.elapsed_time)}!")
    
    # Show the report in a tabbed layout
    tab1, tab2 = st.tabs([get_ui_text('report_tab', language_code), get_ui_text('plan_tab', language_code)])
    
    with tab1:
        st.markdown(st.session_state.research_report)
        
        # Download button for the report
        st.download_button(
            label=get_ui_text('download_report', language_code),
            data=st.session_state.research_report,
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown"
        )
    
    with tab2:
        if st.session_state.subtasks:
            for i, subtask in enumerate(st.session_state.subtasks):
                with st.expander(f"{get_ui_text('subtask', language_code)} {i+1}: {subtask['description']}", expanded=i==0):
                    st.markdown(f"**{get_ui_text('search_queries', language_code)}:**")
                    for query in subtask['search_queries']:
                        st.markdown(f"- {query}")

# Display error if there was one
if st.session_state.research_status == "error":
    st.error(st.session_state.research_message)
    if st.session_state.thread_error:
        st.error(f"Thread error: {st.session_state.thread_error}")
    st.button(get_ui_text('try_again', language_code))

# Footer
st.markdown("---")
st.markdown(get_ui_text('footer', language_code))