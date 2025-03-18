import os
import json #next steps - CLEAR IMPORTS THAT ARE NO LONGER IN USE
import time
from agents.task_manager import create_research_plan
from agents.information_retrieval import retrieve_information
from agents.analysis import analyse_information
from agents.report_generator import generate_report

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

def save_report(report, research_question, output_dir="./reports"):
    """
    Save the research report to a file.
    
    Args:
        report (str): The research report.
        research_question (str): The research question.
        output_dir (str): The directory to save the report to.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate a filename based on the research question
    filename = research_question.lower().replace(" ", "_")[:50]
    filename = "".join(c for c in filename if c.isalnum() or c == "_")
    filename = f"{filename}_{int(time.time())}.md"
    
    # Save the report
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"Report saved to {os.path.join(output_dir, filename)}")

def main():
    """
    Main entry point for the research assistant application.
    """
    # Check for required API keys
    from config import MISTRAL_API_KEY
    
    if not MISTRAL_API_KEY:
        print("Error: MISTRAL_API_KEY environment variable is required.")
        return
    
    # Get the research question
    research_question = input("Enter your research question: ")
    
    # Run the research assistant
    report = run_research_assistant(research_question)
    
    # Save the report
    save_report(report, research_question)
    
    # Print a preview of the report
    print("\n--- Report Preview ---\n")
    print(report[:500] + "...\n")
    print("--- End Preview ---\n")

if __name__ == "__main__":
    main()