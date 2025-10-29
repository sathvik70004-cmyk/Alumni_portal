// Chatbot functionality using Gemini API
class AlumniChatbot {
    constructor() {
        this.chatContainer = null;
        this.messagesList = null;
        this.inputField = null;
        this.sendButton = null;
        this.toggleButton = null;
        this.init();
    }

    init() {
        // Create chatbot UI elements
        this.createChatbotUI();
        this.attachEventListeners();
    }

    createChatbotUI() {
        // Create main container
        this.chatContainer = document.createElement('div');
        this.chatContainer.className = 'chatbot-container';
        this.chatContainer.style.display = 'none';

        // Create toggle button
        this.toggleButton = document.createElement('button');
        this.toggleButton.className = 'chatbot-toggle';
        this.toggleButton.innerHTML = '<i class="fas fa-comments"></i>';

        // Create chat interface
        const chatInterface = document.createElement('div');
        chatInterface.className = 'chatbot-interface';

        // Create header
        const header = document.createElement('div');
        header.className = 'chatbot-header';
        header.innerHTML = `
            <h3>Alumni Assistant</h3>
            <button class="chatbot-close"><i class="fas fa-times"></i></button>
        `;

        // Create messages container
        this.messagesList = document.createElement('div');
        this.messagesList.className = 'chatbot-messages';

        // Create input area
        const inputArea = document.createElement('div');
        inputArea.className = 'chatbot-input';

        this.inputField = document.createElement('input');
        this.inputField.type = 'text';
        this.inputField.placeholder = 'Type your message...';

        this.sendButton = document.createElement('button');
        this.sendButton.className = 'chatbot-send';
        this.sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';

        inputArea.appendChild(this.inputField);
        inputArea.appendChild(this.sendButton);

        // Assemble the interface
        chatInterface.appendChild(header);
        chatInterface.appendChild(this.messagesList);
        chatInterface.appendChild(inputArea);

        this.chatContainer.appendChild(chatInterface);

        // Add to document
        document.body.appendChild(this.toggleButton);
        document.body.appendChild(this.chatContainer);

        // Add welcome message
        this.addMessage('bot', 'Hello! I\'m your Alumni Portal assistant. How can I help you today?');
    }

    attachEventListeners() {
        // Toggle chatbot visibility
        this.toggleButton.addEventListener('click', () => {
            this.chatContainer.style.display = this.chatContainer.style.display === 'none' ? 'block' : 'none';
        });

        // Close button
        const closeButton = this.chatContainer.querySelector('.chatbot-close');
        closeButton.addEventListener('click', () => {
            this.chatContainer.style.display = 'none';
        });

        // Send message on button click
        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Send message on Enter key
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addMessage('user', message);
        this.inputField.value = '';

        // Show typing indicator
        this.addTypingIndicator();

        try {
            const response = await this.getGeminiResponse(message);
            this.removeTypingIndicator();
            this.addMessage('bot', response);
        } catch (error) {
            this.removeTypingIndicator();
            this.addMessage('bot', 'Sorry, I encountered an error. Please try again.');
            console.error('Chatbot error:', error);
        }
    }

    async getGeminiResponse(message) {
        try {
            const response = await fetch('/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            const data = await response.json();
            return data.response;
        } catch (error) {
            throw new Error('Failed to get response from Gemini API');
        }
    }

    addMessage(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${sender}-message`;
        messageDiv.textContent = content;
        this.messagesList.appendChild(messageDiv);
        this.messagesList.scrollTop = this.messagesList.scrollHeight;
    }

    addTypingIndicator() {
        const typing = document.createElement('div');
        typing.className = 'typing-indicator';
        typing.innerHTML = '<span></span><span></span><span></span>';
        this.messagesList.appendChild(typing);
        this.messagesList.scrollTop = this.messagesList.scrollHeight;
    }

    removeTypingIndicator() {
        const typing = this.messagesList.querySelector('.typing-indicator');
        if (typing) {
            typing.remove();
        }
    }
}

// Initialize chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new AlumniChatbot();
});