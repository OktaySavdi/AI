# Core Application Imports: Essential Flask and utility libraries for web application functionality
from flask import Flask, render_template, request, jsonify, session, send_from_directory
import logging
from logging.handlers import RotatingFileHandler
from openai import AzureOpenAI, OpenAI
import sqlite3
from datetime import datetime
import os
import os.path
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import hashlib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from kubernetes import client, config
import subprocess
import re
from kubernetes.config.kube_config import list_kube_config_contexts, load_kube_config
from kubernetes.client.rest import ApiException
from kubernetes.client import CoreV1Api
import json
import anthropic
import openai
import google.generativeai as genai
import requests

# Load environment variables
load_dotenv()

# Logging configuration
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = 'logs/app.log'
os.makedirs('logs', exist_ok=True)
file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
file_handler.setFormatter(log_formatter)
logger = logging.getLogger('chatops')
logger.setLevel(os.getenv('LOG_LEVEL'))
logger.addHandler(file_handler)

# AI Configuration: Defines the AI assistant's behavior, rules, and response format
SYSTEM_PROMPT = """You are a Kubernetes Operations Assistant that converts natural language queries into kubectl commands.

Your role is to:
1. Interpret user questions about Kubernetes resources
2. Convert questions into appropriate kubectl commands
3. Execute the commands and explain the results
4. Provide troubleshooting guidance

Example conversions:
User: "Show me all pods in the default namespace"
Response: {"command": "kubectl get pods -n default", "explanation": "Retrieving all pods in default namespace"}

User: "Is my cluster healthy?"
Response: {"command": "kubectl get nodes; kubectl cluster-info", "explanation": "Checking node status and cluster health"}

Rules:
- Always return a JSON object with 'command' and 'explanation' fields
- Only include safe kubectl commands (get, describe, logs)
- Never execute destructive commands
- Verify resource types and namespaces
"""

# Database Configuration: SQLite setup for persistent conversation storage
DB_PATH = os.path.join('db', 'conversations.db')

app = Flask(__name__, 
    static_url_path='/static',
    static_folder='static',
    template_folder='templates'
)
app.secret_key = os.urandom(24)

# Datetime Adapter: Converts Python datetime objects for SQLite storage
def adapt_datetime(ts):
    return ts.isoformat()

# Register the adapter
sqlite3.register_adapter(datetime, adapt_datetime)

# System Prompt Hash: Generates MD5 hash of system prompt for tracking changes
def get_system_prompt_hash():
    return hashlib.md5(SYSTEM_PROMPT.encode()).hexdigest()

# Database Initialization: Creates tables and handles schema migrations
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS conversations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT,
                  role TEXT,
                  content TEXT,
                  timestamp DATETIME)''')
    
    # Check if system_prompt_hash column exists
    cursor = c.execute('PRAGMA table_info(conversations)')
    columns = [column[1] for column in cursor.fetchall()]
    
    # Add system_prompt_hash column if it doesn't exist
    if 'system_prompt_hash' not in columns:
        try:
            c.execute('ALTER TABLE conversations ADD COLUMN system_prompt_hash TEXT')
            logger.info("Added system_prompt_hash column to conversations table")
        except sqlite3.OperationalError as e:
            logger.warning(f"Column system_prompt_hash might already exist: {e}")
    
    conn.commit()
    conn.close()

# Message Storage: Saves chat messages with metadata and system prompt hash
def save_message(session_id, role, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now()  # Create timestamp before insertion
    prompt_hash = get_system_prompt_hash() if role == "system" else None
    c.execute('INSERT INTO conversations (session_id, role, content, timestamp, system_prompt_hash) VALUES (?, ?, ?, ?, ?)',
              (session_id, role, content, timestamp, prompt_hash))
    conn.commit()
    conn.close()

# Conversation Cleanup: Removes all messages for a given session
def clear_old_conversation(session_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM conversations WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()

# Conversation History: Retrieves messages and handles system prompt changes
def get_conversation_history(session_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if system prompt has changed
    c.execute('SELECT system_prompt_hash FROM conversations WHERE session_id = ? AND role = "system" ORDER BY timestamp DESC LIMIT 1', (session_id,))
    result = c.fetchone()
    current_hash = get_system_prompt_hash()
    
    if not result or result[0] != current_hash:
        # System prompt has changed or doesn't exist, clear conversation
        clear_old_conversation(session_id)
        save_message(session_id, "system", SYSTEM_PROMPT)
        conn.close()
        return [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Get all messages and ensure system prompt is first
    messages = []
    c.execute('SELECT role, content FROM conversations WHERE session_id = ? ORDER BY timestamp', (session_id,))
    for role, content in c.fetchall():
        if role == "system" and not messages:
            messages.insert(0, {"role": role, "content": content})
        else:
            messages.append({"role": role, "content": content})
    
    conn.close()
    
    # If no system prompt found, add it
    if not messages or messages[0]["role"] != "system":
        save_message(session_id, "system", SYSTEM_PROMPT)
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    
    return messages

# Update SCOPES for Gemini API
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

# get Gemini fine tuned cred
def load_creds():
    # Only load credentials if Gemini is the provider
    if os.getenv('MODEL_PROVIDER').lower() != 'gemini':
        logger.debug("Skipping credentials load - provider is not Gemini")
        return None
        
    logger.debug("Starting load_creds function for Gemini...")
    creds = None
    
    # Check if client_secret.json exists
    if not os.path.exists('client_secret.json'):
        logger.error("client_secret.json not found. Please download OAuth 2.0 credentials from Google Cloud Console")
        raise FileNotFoundError("client_secret.json is required for Gemini OAuth authentication")
    
    try:
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            logger.debug("Loaded credentials from token.json")
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                logger.debug("Refreshed expired credentials")
            else:
                logger.debug("Starting OAuth flow to generate new credentials")
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                    logger.debug("Generated new credentials via OAuth flow")
                except Exception as e:
                    logger.error(f"OAuth flow failed: {str(e)}")
                    raise Exception("Failed to authenticate with Google. Check your client_secret.json configuration.")
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                logger.debug("Saved new credentials to token.json")
    except FileNotFoundError as e:
        logger.error(f"Critical file missing: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in load_creds: {str(e)}", exc_info=True)
        raise
    finally:
        if creds:
            logger.debug("load_creds function completed successfully")
        else:
            logger.warning("load_creds function did not return valid credentials")
    return creds

# Initialize Gemini separately from other initialization code
def init_gemini():
    # Check if Gemini is the selected provider
    if os.getenv('MODEL_PROVIDER').lower() != 'gemini':
        logger.debug("Skipping Gemini initialization - provider is not Gemini")
        return False

    try:
        logger.debug("Initializing Gemini API...")
        creds = load_creds()
        if not creds:
            logger.error("Failed to load credentials for Gemini")
            return False

        # Configure Gemini with credentials
        genai.configure(credentials=creds)
        
        # Verify model access
        try:
            model = genai.GenerativeModel(os.getenv("GEMINI_MODEL"))
            # Test model access with a simple prompt
            response = model.generate_content("test")
            logger.debug("Successfully verified Gemini model access")
        except Exception as e:
            logger.error(f"Failed to access Gemini model: {str(e)}")
            return False

        return True
    except Exception as e:
        logger.error(f"Failed to initialize Gemini: {str(e)}", exc_info=True)
        return False

# Add Kubernetes utility functions
def is_safe_k8s_command(command):
    """Validate if the command is safe to execute"""
    unsafe_patterns = [
        'delete', 'exec',  'apply',
        'patch', 'replace', 'edit'
    ]
    command = command.lower()
    return all(pattern not in command for pattern in unsafe_patterns)

def get_cluster_status():
    """Get detailed cluster connection status and health information"""
    try:
        # Verify kubeconfig path
        kubeconfig_path = os.getenv('KUBECONFIG_PATH', os.path.expanduser('~/.kube/config'))
        if not os.path.exists(kubeconfig_path):
            logger.error(f"Kubeconfig not found at {kubeconfig_path}")
            return {
                "connected": False,
                "message": f"Kubeconfig not found at {kubeconfig_path}",
                "suggested_actions": [
                    "Set KUBECONFIG_PATH environment variable",
                    "Ensure kubeconfig file exists",
                    "Run 'kubectl config view' to verify configuration"
                ]
            }

        # Test API server connectivity
        api_server = subprocess.run(
            ["kubectl", "config", "view", "--minify", "-o", "jsonpath={.clusters[0].cluster.server}"],
            capture_output=True,
            text=True,
            timeout=5
        ).stdout.strip()
        if not api_server:
            logger.error("Failed to retrieve API server URL from kubeconfig")
            return {
                "connected": False,
                "message": "Failed to retrieve API server URL from kubeconfig",
                "suggested_actions": [
                    "Check kubeconfig file for cluster details",
                    "Ensure the cluster is configured correctly"
                ]
            }

        # Test network connectivity to API server
        api_host = api_server.replace("https://", "").split(":")[0]
        ping_result = subprocess.run(
            ["ping", "-c", "1", "-W", "3", api_host],
            capture_output=True,
            timeout=5
        )
        if ping_result.returncode != 0:
            logger.error(f"Cannot reach API server at {api_host}")
            return {
                "connected": False,
                "message": f"Cannot reach API server at {api_host}",
                "suggested_actions": [
                    "Check network connectivity",
                    "Verify VPN connection if required",
                    "Ensure API server is running"
                ]
            }

        # Initialize Kubernetes client
        config.load_kube_config()
        v1 = CoreV1Api()

        # Test basic connectivity
        namespaces = v1.list_namespace(timeout_seconds=5)

        # Get node status
        nodes = v1.list_node(timeout_seconds=5)
        node_status = []
        for node in nodes.items:
            conditions = {cond.type: cond.status for cond in node.status.conditions}
            node_status.append({
                'name': node.metadata.name,
                'ready': conditions.get('Ready', 'Unknown'),
                'conditions': conditions
            })

        return {
            "connected": True,
            "message": "Successfully connected to cluster",
            "node_status": node_status,
            "active_context": subprocess.getoutput("kubectl config current-context"),
            "connection_details": {
                "api_server": api_server,
                "kubeconfig": kubeconfig_path
            }
        }

    except ApiException as e:
        logger.error(f"Kubernetes API error: {e.reason}")
        return {
            "connected": False,
            "message": f"Kubernetes API error: {e.reason}",
            "suggested_actions": [
                "Verify kubeconfig file",
                "Check cluster credentials",
                "Ensure cluster is running"
            ]
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            "connected": False,
            "message": f"Unexpected error: {str(e)}",
            "suggested_actions": [
                "Check application logs for details",
                "Verify network connectivity",
                "Ensure cluster is accessible"
            ]
        }

def execute_k8s_command(command):
    """Execute kubectl command with enhanced error handling"""
    if not is_safe_k8s_command(command):
        return "❌ This command is not allowed for security reasons"
    
    try:
        # Check cluster connection first
        status = get_cluster_status()
        if not status["connected"]:
            error_msg = f"""❌ Cannot connect to cluster
Status: {status['message']}
Please verify:
- KUBECONFIG environment variable is set
- Cluster is running and accessible
- VPN/Network connectivity is active
- You have required permissions"""
            logger.error(f"Cluster connection failed: {status['message']}")
            return error_msg

        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        
        # Handle empty output
        if not result.stdout.strip():
            return "✅ Command executed successfully, but returned no results. This might mean no resources were found."
            
        return f"""✅ Command executed successfully:
{result.stdout}"""
    except subprocess.CalledProcessError as e:
        logger.error(f"Command execution error: {str(e)}")
        return f"""❌ Command execution failed:
Error: {e.stderr}
Exit code: {e.returncode}"""
    except Exception as e:
        logger.error(f"Kubernetes command error: {str(e)}")
        return f"""❌ Unexpected error:
Error: {str(e)}
Please check your configuration and try again"""

def process_k8s_query(query, messages):
    """Process natural language query through AI to get kubectl command"""
    try:
        # Check cluster connectivity first
        status = get_cluster_status()
        if not status["connected"]:
            return "kubectl cluster-info", "Checking cluster connectivity"

        provider = os.getenv('MODEL_PROVIDER').lower()  # Default to OpenAI if not set
        
        # Add K8s context for command generation
        k8s_messages = messages.copy()
        k8s_messages.append({
            "role": "system",
            "content": "Convert the following query into a kubectl command. Respond in JSON format with 'command' and 'explanation' fields."
        })
        k8s_messages.append({"role": "user", "content": query})

        # Process through selected AI provider
        if provider == 'openai':
            logger.debug("Using OpenAI provider")
            openai.api_key = os.getenv("OPENAI_API_KEY")
            response = openai.chat.completions.create(
                model=os.getenv('OPENAI_MODEL'),
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            ai_response = response.choices[0].message.content
        elif provider == 'azure':
            logger.debug("Using Azure OpenAI provider")
            client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            )
            logger.debug("Azure OpenAI client initialized")
            
            # Format messages properly for Azure OpenAI
            formatted_messages = [
                {
                    "role": "system",
                    "content": "You are a Kubernetes assistant. Always respond in JSON format with 'command' and 'explanation' fields."
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
            
            try:
                response = client.chat.completions.create(
                    model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                    messages=formatted_messages,
                    max_tokens=300,
                    temperature=0.1,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None,
                    stream=False,
                    seed=42,
                    response_format={ "type": "json_object" }  # Force JSON response
                )
                
                ai_response = response.choices[0].message.content
                logger.debug(f"Raw Azure OpenAI response: {ai_response}")
                
                # Validate JSON format
                try:
                    parsed_response = json.loads(ai_response)
                    if not all(k in parsed_response for k in ['command', 'explanation']):
                        logger.error("Response missing required fields")
                        return "kubectl get pods", "Showing pods (fallback command)"
                    return parsed_response['command'], parsed_response['explanation']
                except json.JSONDecodeError as je:
                    logger.error(f"JSON parsing error: {str(je)}, Response: {ai_response}")
                    return "kubectl get pods", "Showing pods (fallback command)"
                    
            except Exception as e:
                logger.error(f"Azure OpenAI API error: {str(e)}")
                return None, None

        elif provider == 'gemini':
            logger.debug("Using Gemini provider")
            try:
                logger.debug("Using Gemini provider")
                genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
                model = genai.GenerativeModel(os.getenv("GEMINI_MODEL"))
                response = model.generate_content(query,
                generation_config={
                        'max_output_tokens': 300,
                        'temperature': 0.7,
                        "top_p": 0.95,
                        "top_k": 64,
                    }
                )
                
                if response and hasattr(response, 'text'):
                    ai_response = response.text
                else:
                    raise Exception("No valid response from Gemini fine-tuned model")
                    
            except Exception as e:
                logger.error(f"Gemini API error: {str(e)}")
                raise
        elif provider == 'claude':
            logger.debug("Using Claude provider")
            message = client.messages.create(
                model=os.getenv('CLAUDE_MODEL'),
                messages=messages,
                max_tokens=300
            )
            ai_response = message.content[0].text

        elif provider == 'deepseek':
            logger.debug("Using DeepSeek provider")
            # Implement DeepSeek specific logic here
            headers = {"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"}
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                json={"model": os.getenv('DEEPSEEK_MODEL'), "messages": messages},
                headers=headers
            )
            ai_response = response.json()['choices'][0]['message']['content']
            
            if not ai_response:
                raise Exception("No response generated from the AI provider")
        
        else:
            logger.warning(f"Provider {provider} not supported for K8s command generation")
            return None, None

        # Parse the AI response
        try:
            response_data = json.loads(ai_response)
            return response_data.get('command'), response_data.get('explanation')
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON")
            return None, None

    except Exception as e:
        logger.error(f"Error processing K8s query: {str(e)}")
        return None, None

# Home Route: Initializes session and renders main chat interface
@app.route('/')
def home():
    if 'session_id' not in session:
        session['session_id'] = os.urandom(16).hex()
    return render_template('index.html', conversation=get_conversation_history(session['session_id']))

# Chat API: Handles message processing across multiple AI providers
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({'message': "⚠️ Empty message received", 'status': 'error'})
            
        session_id = session.get('session_id', os.urandom(16).hex())
        messages = get_conversation_history(session_id)

        # Get K8s command
        k8s_command, explanation = process_k8s_query(user_message, messages)
        logger.debug(f"K8s command generated: {k8s_command}, Explanation: {explanation}")
        
        if not k8s_command or not explanation:
            return jsonify({
                'message': "⚠️ Could not generate a valid Kubernetes command. Please try rephrasing your question.",
                'status': 'error'
            })

        # Execute command and capture output
        try:
            result = execute_k8s_command(k8s_command)
            logger.debug(f"Command execution result: {result}")
            
            # Format the response with proper HTML escaping
            assistant_message = f"""{result}""".strip()

            # Save conversation
            save_message(session_id, "user", user_message)
            save_message(session_id, "assistant", assistant_message)
            
            # Return structured response
            return jsonify({
                'message': assistant_message,
                'status': 'success',
                'data': {
                    'command': k8s_command,
                    'explanation': explanation,
                    'result': result
                }
            })
            
        except Exception as e:
            logger.error(f"Command execution error: {str(e)}")
            return jsonify({
                'message': f"❌ Error executing command: {str(e)}",
                'status': 'error'
            })
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}", exc_info=True)
        return jsonify({
            'message': "❌ An unexpected error occurred",
            'status': 'error',
            'error': str(e)
        }), 500

# Clear Chat API: Removes conversation history for current session
@app.route('/api/lear_chat', methods=['POST'])
def clear_chat():
    try:
        session_id = session.get('session_id', os.urandom(16).hex())
        logger.debug(f"Clearing chat for session: {session_id}")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM conversations WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()
        logger.debug(f"Chat cleared successfully for session: {session_id}")
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error clearing chat: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'error': str(e)}), 500

# Static File Server: Serves static assets and favicon
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Add favicon route to prevent 404
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Kubernetes Configuration: Setup and management of cluster connections
def init_kubernetes():
    """Initialize Kubernetes configuration and validate connection"""
    try:
        # Load the kubeconfig file
        load_kube_config()
        # Test connection by listing namespaces
        v1 = CoreV1Api()
        v1.list_namespace()
        logger.info("Successfully connected to Kubernetes cluster")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Kubernetes cluster: {str(e)}")
        return False

def get_available_contexts():
    """Get list of available Kubernetes contexts"""
    try:
        contexts, active_context = list_kube_config_contexts()
        return {
            'contexts': [context['name'] for context in contexts],
            'active': active_context['name']
        }
    except Exception as e:
        logger.error(f"Failed to get Kubernetes contexts: {str(e)}")
        return {'contexts': [], 'active': None}

def switch_context(context_name):
    """Switch Kubernetes context"""
    try:
        os.system(f"kubectl config use-context {context_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to switch context: {str(e)}")
        return False

def get_kubeconfig_content():
    """Get contents of kubeconfig file"""
    try:
        kubeconfig_path = os.path.expanduser(os.getenv('KUBECONFIG_PATH'))
        if os.path.exists(kubeconfig_path):
            with open(kubeconfig_path, 'r') as f:
                return f.read()
        return f"Kubeconfig file not found at {kubeconfig_path}"
    except Exception as e:
        logger.error(f"Failed to read kubeconfig: {str(e)}")
        return f"Error reading kubeconfig: {str(e)}"

# Add new route for cluster management
@app.route('/api/k8s/status', methods=['GET'])
def cluster_status():
    try:
        contexts = get_available_contexts()
        status = get_cluster_status()
        
        # Add connection test
        if status['connected']:
            try:
                # Test specific cluster connectivity
                test_cmd = subprocess.run(
                    ['kubectl', 'cluster-info'], 
                    capture_output=True, 
                    text=True,
                    timeout=5
                )
            except subprocess.TimeoutExpired:
                status['connected'] = False
                status['message'] = "Cluster connection timeout"
                status['suggested_actions'] = ["Check if cluster is responsive", "Verify network connectivity"]
        
        return jsonify({
            **status,
            'contexts': contexts['contexts'],
            'active_context': contexts['active']
        })
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({
            'connected': False,
            'message': str(e),
            'status': 'error',
            'suggested_actions': [
                "Check if kubectl is installed and in PATH",
                "Verify kubeconfig file exists and is valid",
                "Ensure you have proper permissions"
            ]
        }), 500

@app.route('/api/k8s/switch-context', methods=['POST'])
def switch_cluster_context():
    try:
        context = request.json.get('context')
        if not context:
            return jsonify({'error': 'Context name required'}), 400
        
        subprocess.run(["kubectl", "config", "use-context", context], check=True)
        return jsonify({'success': True, 'active_context': context})
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

# Main Entry Point: Initializes application components and starts server
if __name__ == '__main__':
    logger.info("Starting application")
    os.makedirs(os.path.join('static', 'db'), exist_ok=True)
    init_db()
    init_kubernetes()
    logger.info("Database initialized")
    
    # Initialize Kubernetes
    if not init_kubernetes():
        logger.error("Failed to initialize Kubernetes connection")
    
    # Initialize Gemini only if it's the selected provider
    if os.getenv('MODEL_PROVIDER').lower() == 'gemini':
        if not init_gemini():
            logger.error("Failed to initialize Gemini")
    
    app.run(host="0.0.0.0", port=5000, debug=True)