document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const clearChatButton = document.getElementById('clearChatButton');

    // Function to sanitize message by removing asterisks
    function sanitizeMessage(message) {
        return message.replace(/\*/g, '');
    }

    // Function to sanitize HTML content
    function sanitizeHTML(text) {
        if (!text) return '';
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Function to add a new message to the chat
    function addMessage(message, type) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', type);
        
        if (type === 'bot' || type === 'assistant') {
            // For bot/assistant messages, preserve HTML formatting
            if (message.startsWith('<pre>')) {
                // Command output format
                messageElement.innerHTML = message;
            } else {
                const preElement = document.createElement('pre');
                preElement.innerHTML = sanitizeHTML(message);
                messageElement.appendChild(preElement);
            }
        } else {
            // For user messages, sanitize and use text content
            messageElement.textContent = sanitizeMessage(message);
        }
        
        chatMessages.appendChild(messageElement);
        smoothScroll(chatMessages);
    }

    function smoothScroll(element) {
        const target = element.scrollHeight;
        element.scrollTo({
            top: target,
            behavior: 'smooth'
        });
    }
    
    // Function to show loading indicator
    function showLoading() {
        const loadingElement = document.createElement('div');
        loadingElement.classList.add('message', 'bot', 'loading');
        loadingElement.id = 'loadingIndicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.classList.add('dot');
            loadingElement.appendChild(dot);
        }
        
        chatMessages.appendChild(loadingElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to remove loading indicator
    function removeLoading() {
        const loadingElement = document.getElementById('loadingIndicator');
        if (loadingElement) {
            loadingElement.remove();
        }
    }

    // Function to send message to server
    async function sendMessage() {
        let message = userInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addMessage(message, 'user');
        userInput.value = '';
        showLoading();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            });
            
            const data = await response.json();
            removeLoading();
            
            if (data.status === 'success') {
                addMessage(data.message, 'assistant');
            } else {
                addMessage(data.message || 'An error occurred', 'error');
            }
        } catch (error) {
            removeLoading();
            console.error('Error:', error);
            addMessage('Sorry, a connection error occurred.', 'error');
        }
    }

    // Function to clear chat
    async function clearChat() {
        try {
            const response = await fetch('/api/clear_chat', {
                method: 'POST',
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Clear chat messages
                chatMessages.innerHTML = '';
                
                // Add welcome message
                addMessage('Hello! You can ask questions about Kubernetes. For example, you can ask "What is Kubernetes?" or "What is a Pod?"', 'system');
            } else {
                addMessage('Sorry, there was an error clearing the chat history', 'system');
            }
        } catch (error) {
            addMessage('Sorry, a connection error occurred.', 'system');
            console.error('Error:', error);
        }
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Clear chat button event listener
    clearChatButton.addEventListener('click', clearChat);
});