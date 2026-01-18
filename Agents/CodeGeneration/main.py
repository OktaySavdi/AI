import git
import subprocess
import os
import shutil
import logging
from dotenv import load_dotenv
from openai import AzureOpenAI

# Model Libraries
import anthropic
import openai
import google.generativeai as genai
import requests
import time

# ==========================
# VARIABLES
# ==========================
# Load environment variables
load_dotenv()

# AI Model Configuration
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER")

# Terraform Configuration
TARGET_DIR = "./git_repo"
MODULE_NAME = "azure_firewall"
TERRAFORM_FILES = ["main.tf", "variables.tf", "outputs.tf", "providers.tf", "terraform.tfvars"]

# Sample Code Directory
SAMPLE_DIR = f"{TARGET_DIR}/modules/{MODULE_NAME}"

# Logging Configuration
LOG_FILE = "terraform_agent_debug.log"

# Prompt File Path
file_path = "./prompt.txt"

# ==========================
# Functions
# ==========================
# Measure execution time
def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL").upper(), logging.DEBUG),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE)
    ]
)

# Load prompt from file
def load_prompt_from_file(filename):
    """Load a Terraform prompt from a local file."""
    file_path = "./prompt.txt"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt file {file_path} not found.")
    
    with open(file_path, "r") as file:
        prompt = file.read()
    
    # Replace {filename} placeholder with the actual Terraform file name
    return prompt.replace("{filename}", filename)

# Step 1: Clone GitLab Repo
@measure_execution_time
def clone_repo(repo_url, target_dir):
    logging.debug(f"Cloning GitLab repository from {repo_url} into {target_dir}")
    if os.path.exists(target_dir):
        logging.debug(f"Removing existing directory: {target_dir}")
        shutil.rmtree(target_dir)
    try:
        git.Repo.clone_from(repo_url, target_dir, branch=os.getenv("GIT_BRANCH", "main"))
        logging.info(f"Repository successfully cloned to {target_dir}")
    except Exception as e:
        logging.error(f"Failed to clone repository: {e}")
        raise

# Step 2: Initialize AI Model
@measure_execution_time
def init_model():
    logging.debug(f"Initializing AI model: {MODEL_PROVIDER}")

    if MODEL_PROVIDER == "gemini":
        genai.configure(api_key=os.getenv("GENAI_API_KEY"))
        return genai.GenerativeModel(os.getenv("GEMINI_MODEL"))

    elif MODEL_PROVIDER == "openai":
        openai.api_key = os.getenv("OPENAI_API_KEY")
        return os.getenv("OPENAI_MODEL")
    
    if MODEL_PROVIDER == "azure_openai":
        return "azure_openai"

    elif MODEL_PROVIDER == "deepseek":
        return "deepseek"

    elif MODEL_PROVIDER == "claude":
        client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
        return client

    else:
        raise ValueError("Unsupported MODEL_PROVIDER specified")
    
# Step 3: Generate Terraform Code from Scratch
@measure_execution_time
def generate_terraform_code(model, prompt):
    logging.debug(f"Generating Terraform code with model: {MODEL_PROVIDER}")

    try:
        full_prompt = f"{prompt}"

        if MODEL_PROVIDER == "gemini":
            response = model.generate_content(full_prompt)
            return response.text

        elif MODEL_PROVIDER == "openai":
            response = openai.Completion.create(engine=os.getenv("OPENAI_MODEL"), prompt=full_prompt, max_tokens=500)
            return response['choices'][0]['text']        
        
        elif MODEL_PROVIDER == "azure_openai": 
            # #Initialize Azure OpenAI Service client with key-based authentication    
            client = AzureOpenAI(  
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),  
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            )
            # Call Azure OpenAI
            response = client.chat.completions.create( 
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                messages=[
                    #{"role": "system", "content": "You are an AI assistant specializing in Terraform code generation."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=1500,  
                temperature=0.1,  
                top_p=0.95,  
                frequency_penalty=0,  
                presence_penalty=0,
                stop=None,  
                stream=False,
                seed=42
            )
            # # Extract response text
            return response.choices[0].message.content

        elif MODEL_PROVIDER == "deepseek":
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {os.getenv("DEEPSEEK_API_KEY")}",
                "Content-Type": "application/json"
            }
            data = {
                "model": os.getenv("DEEPSEEK_MODEL"),
                "messages": [
                    {"role": "system", "content": "You're an assistant who writes code"},
                    {"role": "user", "content": full_prompt}
                ],
                "max_tokens": 500
            }
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")

        elif MODEL_PROVIDER == "claude":
            # Corrected Anthropic API call
            response = model.messages.create(
                model=os.getenv("CLAUDE_MODEL"),
                max_tokens=500,
                messages=[
                    {"role": "system", "content": "You're an assistant who writes code"},
                    {"role": "user", "content": full_prompt}
                ],
            )
            return response.content[0].text

        else:
            raise ValueError("Invalid model provider")

    except Exception as e:
        logging.error(f"Failed to generate Terraform code: {e}")
        raise

# Step 4: Save Generated Code to Separate Files
@measure_execution_time
def save_code(target_dir, filename, code):
    module_dir = os.path.join(target_dir, 'modules', MODULE_NAME)
    logging.debug(f"Creating directory for new module: {module_dir}")
    os.makedirs(module_dir, exist_ok=True)
    file_path = os.path.join(module_dir, filename)
    try:
        with open(file_path, 'w') as f:
            f.write(code)
        logging.info(f"Terraform code saved in {file_path}")
    except Exception as e:
        logging.error(f"Failed to save Terraform code: {e}")
        raise

# Step 5: Run Terraform Validation and Planning with Auto-Fix on Failure
@measure_execution_time
def run_terraform_tests(module_dir):
    logging.debug(f"Initializing Terraform in directory: {module_dir}")
    
    try:
        logging.debug("Running Terraform formatting")
        subprocess.run(["terraform", "fmt", "-recursive"], cwd=module_dir, check=True)
        logging.info("Terraform files formatted successfully")

        logging.debug("Running Terraform initialization")
        init_result = subprocess.run(
            ["terraform", "init"], cwd=module_dir, capture_output=True, text=True
        )
        if init_result.returncode != 0:
            logging.error(f"Terraform initialization failed with errors: {init_result.stderr}")
            handle_terraform_errors(module_dir, init_result.stderr, "init")
            return  # Exit after handling errors

        logging.info("Terraform initialization successful")

        logging.debug("Running Terraform validation")
        validation_result = subprocess.run(
            ["terraform", "validate"], cwd=module_dir, capture_output=True, text=True
        )
        if validation_result.returncode != 0:
            logging.error(f"Terraform validation failed with errors: {validation_result.stderr}")
            handle_terraform_errors(module_dir, validation_result.stderr, "validate")
            return  # Exit after handling errors

        logging.info("Terraform Validation successful")

    except subprocess.CalledProcessError as e:
        logging.error(f"Terraform command failed: {e}")
        raise

# Step 6: Handle Terraform Errors
@measure_execution_time
def handle_terraform_errors(module_dir, error_message, step):
    """Handle Terraform errors by analyzing error messages and fixing them accordingly."""
    # Parsing the error message to determine which Terraform file needs fixing
    errors = parse_terraform_errors(error_message, step)
    
    for error in errors:
        filename = error['file']
        fix_terraform_errors(module_dir, error['message'], filename)

@measure_execution_time
def parse_terraform_errors(error_message, step):
    """Parse error messages to extract detailed error information including filename and specific message."""
    # This simple parser assumes you know which file types are typically involved in each step
    errors = []
    if step == "init":
        # init errors often don't pertain to a specific file, handle generically or improve parsing logic
        errors.append({'file': 'providers.tf', 'message': error_message})  # Example
    elif step == "validate":
        # Example of parsing, customize based on real error patterns
        if "main.tf" in error_message:
            errors.append({'file': 'main.tf', 'message': error_message})
        if "variables.tf" in error_message:
            errors.append({'file': 'variables.tf', 'message': error_message})
        if "outputs.tf" in error_message:
            errors.append({'file': 'outputs.tf', 'message': error_message})
    
    return errors

# Function to analyze and fix Terraform errors automatically
@measure_execution_time
def fix_terraform_errors(module_dir, error_message, filename):
    logging.debug("Analyzing Terraform errors and attempting to fix them...")

    try:
        # Ensure the module directory exists before modifying files
        if not os.path.exists(module_dir):
            logging.error(f"Module directory does not exist: {module_dir}. Skipping fix for {filename}")
            return

        # Load the appropriate prompt based on the Terraform file involved in the error
        prompt = load_prompt_from_file(filename)  
        
        # Initialize the AI model
        model = init_model()
        
        # Generate fixed Terraform code using AI
        fix_prompt = f"Fix the following Terraform error automatically:\n\n{error_message}\n\n{prompt}"
        fixed_code = generate_terraform_code(model, fix_prompt)

        # Ensure the AI response is a string before writing to the file
        if not isinstance(fixed_code, str):
            logging.error(f"AI model returned unexpected output type: {type(fixed_code)}. Expected a string.")
            return

        # Save the fixed Terraform code to the existing file
        file_path = os.path.join(module_dir, filename)
        try:
            with open(file_path, 'w') as f:
                f.write(fixed_code)
            logging.info(f"Successfully updated Terraform file: {file_path}")

        except Exception as e:
            logging.error(f"Failed to update Terraform file {file_path}: {e}")
            raise

    except Exception as e:
        logging.error(f"Failed to auto-fix Terraform errors: {e}")
        raise

# Step 7: Commit and Push to GitLab
def push_to_gitlab(target_dir):
    logging.debug(f"Pushing generated code to GitLab repository: {target_dir}")
    try:
        repo = git.Repo(target_dir)
        repo.git.add(A=True)
        repo.index.commit(f"Generated new Terraform module for Azure Resource Group with {MODEL_PROVIDER.capitalize()}")
        repo.remote(name='origin').push()
        logging.info("Code pushed to GitLab repository successfully")
    except Exception as e:
        logging.error(f"Failed to push code to GitLab: {e}")
        raise

# Main Workflow
def main():
    logging.info("Starting AI-based Terraform code generation workflow")
    
    # Step 1: Clone GitLab repository
    clone_repo(os.getenv("GITLAB_REPO"), TARGET_DIR)
    
    # Step 2: Initialize AI Model
    model = init_model()

    # Attempt to generate and save Terraform code, handle potential initial errors
    try:
        for tf_file in TERRAFORM_FILES:
            prompt = load_prompt_from_file(tf_file)
            # Step 3: Generate Terraform Code from Scratch
            terraform_code = generate_terraform_code(model, prompt)
            # Step 4: Save Generated Code to Separate Files
            save_code(TARGET_DIR, tf_file, terraform_code)

        # Step 5: Run Terraform Validation and Planning with Auto-Fix on Failure
        module_path = os.path.join(TARGET_DIR, 'modules', MODULE_NAME)
        run_terraform_tests(module_path)

    except subprocess.CalledProcessError as e:
        logging.error(f"Initial Terraform command failed: {e}")
        # Step 6: Handle Terraform Errors
        handle_terraform_errors(module_path, str(e))

        # Step 7: Commit and Push to GitLab
        push_to_gitlab(TARGET_DIR)

    logging.info("AI-based Terraform code generation workflow completed successfully")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Workflow failed with an error: {e}")
