document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const clearChatButton = document.getElementById('clearChatButton');

    // Function to sanitize message by removing asterisks
    function sanitizeMessage(message) {
        return message.replace(/\*/g, '');
    }

    // Function to add a new message to the chat
    function addMessage(message, type) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', type);
        
        // Sanitize message before displaying
        message = sanitizeMessage(message);
        
        // If message contains a table or code, format it properly
        if (type === 'bot' && (message.includes('\n') || message.includes('  '))) {
            const preElement = document.createElement('pre');
            preElement.textContent = message;
            messageElement.appendChild(preElement);
        } else {
            messageElement.textContent = message;
        }
        
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
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
        
        // Sanitize message before sending
        message = sanitizeMessage(message);
        
        // Add user message to chat
        addMessage(message, 'user');
        userInput.value = '';
        
        // Show loading indicator
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
            
            // Remove loading indicator
            removeLoading();
            
            if (data.error) {
                addMessage('Sorry, an error occurred: ' + data.error, 'bot');
            } else {
                addMessage(data.response, 'bot');
            }
        } catch (error) {
            // Remove loading indicator
            removeLoading();
            addMessage('Sorry, a connection error occurred.', 'bot');
            console.error('Error:', error);
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