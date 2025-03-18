"""
Setup script for Mistral-powered Research Assistant
This script sets up the necessary directories, configuration files, and 
installs required dependencies.
"""

import os
import subprocess
import sys
import shutil

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

def create_init_files():
    """Create __init__.py files for Python packages."""
    print("Creating __init__.py files...")
    
    # Create __init__.py files in all directories
    packages = ['agents', 'utils']
    
    for package in packages:
        init_file = os.path.join(package, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                pass  # Create an empty file
            print(f"Created {init_file}")
    
    print("__init__.py files created successfully.\n")

def install_dependencies():
    """Install required Python dependencies."""
    print("Installing required dependencies...")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Dependencies installed successfully.\n")
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies. Please install them manually using 'pip install -r requirements.txt'.\n")

def create_env_file():
    """Create a .env file from the template if it doesn't exist."""
    print("Setting up environment file...")
    
    if not os.path.exists('.env') and os.path.exists('.env.template'):
        shutil.copy('.env.template', '.env')
        print("Created .env file from template. Please edit it to add your Mistral and/or OpenAI API keys.\n")
    elif not os.path.exists('.env.template'):
        print("Warning: .env.template not found. Please create a .env file manually with your API keys.\n")
    else:
        print(".env file already exists. No changes made.\n")

def create_agents_init():
    """Create or update the agents __init__.py file with proper imports."""
    print("Setting up agents package...")
    
    agents_init_content = """from .task_manager import create_research_plan
from .information_retrieval import retrieve_information
from .analysis import analyse_information
from .report_generator import generate_report

# Make sure these are available at the package level
__all__ = [
    'create_research_plan',
    'retrieve_information',
    'analyse_information',
    'generate_report'
]"""

    with open(os.path.join('agents', '__init__.py'), 'w') as f:
        f.write(agents_init_content)
    
    print("Agents package setup successfully.\n")

def create_utils_init():
    """Create or update the utils __init__.py file."""
    print("Setting up utils package...")
    
    # This can be empty or include specific imports if needed
    with open(os.path.join('utils', '__init__.py'), 'w') as f:
        f.write("# Utils package\n")
    
    print("Utils package setup successfully.\n")

def main():
    """Main function to set up the project."""
    print("\n=== Setting up Mistral Research Assistant ===\n")
    
    create_directory_structure()
    create_init_files()
    create_agents_init()
    create_utils_init()
    install_dependencies()
    create_env_file()
    
    print("Setup completed!")
    print("\nTo run the application, execute: streamlit run streamlit_app.py")
    print("Make sure to set your Mistral API key in the .env file or through the Streamlit interface.\n")

if __name__ == "__main__":
    main()