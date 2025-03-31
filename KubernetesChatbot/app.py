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

# Model Librariespic
import anthropic
import openai
import google.generativeai as genai
import requests

# Load environment variables
load_dotenv()

# Logging Configuration: Sets up rotating file logs with timestamps and debug levels
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = 'logs/app.log'
os.makedirs('logs', exist_ok=True)

file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
file_handler.setFormatter(log_formatter)

logger = logging.getLogger('chatbox')
logger.setLevel(os.getenv('LOG_LEVEL', 'DEBUG'))
logger.addHandler(file_handler)

# AI Configuration: Defines the AI assistant's behavior, rules, and response format
SYSTEM_PROMPT = """You are a concise Kubernetes expert assistant.

Your expertise includes:
- Kubernetes architecture and components
- Pod management and deployments
- Service configuration and networking
- Storage and persistence
- Security and RBAC
- Troubleshooting and debugging
- Best practices and patterns

Rules:
- Respond only in HTML
- Do not use the * character or Markdown
- Do not use analogies, examples, or lists
- Do not explain unless explicitly asked
- Keep responses short and factual
- Limit responses to 250 characters
- Use one sentence only unless absolutely necessary
- No extra context, intros, or summaries

Example:
Q: What is a Pod?
A: A Pod is the smallest deployable unit in Kubernetes that can host one or more containers sharing network and storage.
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
        session_id = session.get('session_id', os.urandom(16).hex())
        provider = os.getenv('MODEL_PROVIDER').lower()
        assistant_message = None  # Initialize the variable
        
        # Get conversation history which will handle system prompt changes
        messages = get_conversation_history(session_id)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        save_message(session_id, "user", user_message)

        logger.debug(f"Chat request received - Session: {session_id}, Provider: {provider}")

        # Handle different providers
        if provider == 'azure':
            logger.debug("Using Azure OpenAI provider")
            client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            )
            logger.debug("Azure OpenAI client initialized")

            response = client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=messages,
                max_tokens=300, 
                temperature=0.1,  
                top_p=0.95,  
                frequency_penalty=0,  
                presence_penalty=0,
                stop=None,  
                stream=False,
                seed=42
            )
            assistant_message = response.choices[0].message.content

        elif provider == 'openai':
            logger.debug("Using OpenAI provider")
            openai.api_key = os.getenv("OPENAI_API_KEY")
            response = openai.chat.completions.create(
                model=os.getenv('OPENAI_MODEL'),
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            assistant_message = response.choices[0].message.content

        elif provider == 'gemini':
            logger.debug("Using Gemini provider")
            try:
                logger.debug("Using Gemini provider")
                genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
                model = genai.GenerativeModel(os.getenv("GEMINI_MODEL"))
                response = model.generate_content(
                user_message,
                generation_config={
                        'max_output_tokens': 300,
                        'temperature': 0.7,
                        "top_p": 0.95,
                        "top_k": 64,
                    }
                )
                
                if response and hasattr(response, 'text'):
                    assistant_message = response.text
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
            assistant_message = message.content[0].text

        elif provider == 'deepseek':
            logger.debug("Using DeepSeek provider")
            # Implement DeepSeek specific logic here
            headers = {"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"}
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                json={"model": os.getenv('DEEPSEEK_MODEL'), "messages": messages},
                headers=headers
            )
            assistant_message = response.json()['choices'][0]['message']['content']
        
        if not assistant_message:
            raise Exception("No response generated from the AI provider")
            
        logger.debug(f"Response generated successfully for session {session_id}")
        save_message(session_id, "assistant", assistant_message)
        
        return jsonify({
            'response': assistant_message,
            'conversation': get_conversation_history(session_id)
        })
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        error_message = f"Error processing request: {str(e)}"
        return jsonify({
            'error': error_message,
            'status': 'error'
        }), 500

# Clear Chat API: Removes conversation history for current session
@app.route('/api/clear_chat', methods=['POST'])
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

# Main Entry Point: Initializes application components and starts server
if __name__ == '__main__':
    logger.info("Starting application")
    os.makedirs(os.path.join('static', 'db'), exist_ok=True)
    init_db()
    logger.info("Database initialized")
    
    # Initialize Gemini only if it's the selected provider
    if os.getenv('MODEL_PROVIDER').lower() == 'gemini':
        if not init_gemini():
            logger.error("Failed to initialize Gemini, application may not work properly")
    
    app.run(debug=True)