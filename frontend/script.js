
const responses = {
    "admission": "📌 <b>Admission Requirements:</b><br>1. Completed application form<br>2. High school transcripts<br>3. Standardized test scores<br>4. Personal statement<br><br>Deadline: June 30, 2024",
    "exam": "📅 <b>Exam Schedule 2025:</b><br>-The exams are scheduled in the first week of December.",
    "fee": "💵 <b>Fee Structure (2025-26):</b><br>- Tuition: $2000/semester<br>- Hostel: $500/month<br>- Lab Fee: $100 (one-time)<br>- Library Deposit: $50 (refundable)<br><br>Payment plans available.",
    "contact": "📞 <b>Contact Support:</b><br>- Email: admissions@abcuniv.edu<br>- Phone: +1 (555) 123-4567<br>- Office Hours: Mon-Fri, 9AM-5PM<br><br>Location: Administration Building, Room 101",
    "courses": "📚 <b>Our Programs:</b><br>1. Computer Science<br>2. Business Administration<br>3. Engineering<br>4. Liberal Arts<br><br>.",
    "scholarship": "🎓 <b>Scholarship Opportunities:</b><br>1. Merit-based (GPA 3.5+)<br>2. Need-based<br>3. Sports scholarships<br>4. Research fellowships<br><br>Deadline: May 15, 2025",
    "campus": "🏛️ <b>Campus Facilities:</b><br>- 24/7 Library<br>- Sports Complex<br>- Student Center<br>- Research Labs<br><br>",
    "default": "I'm not sure I understand. Try asking about:<br>• Admissions<br>• Programs<br>• Fees<br>• Scholarships<br>• Campus life"
};

const chatIcon = document.getElementById('chatIcon');
const chatPopup = document.getElementById('chatPopup');
const closeChat = document.getElementById('closeChat');
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const quickReplies = document.getElementById('quickReplies');
const micBtn = document.getElementById('micBtn');

// Move all event listeners and functions AFTER DOM elements are declared

// Clear input field when clicking into it
userInput.addEventListener('focus', () => {
    userInput.value = '';
});

// Chat trigger functionality
document.querySelectorAll('.chat-trigger').forEach(el => {
    el.addEventListener('click', () => {
        const isOpening = chatPopup.style.display !== 'flex';
        chatPopup.style.display = isOpening ? 'flex' : 'none';
        el.classList.remove('pulse');

        if (isOpening) {
            clearConversationHistory();
            userInput.value = '';
            userInput.focus();
        }
    });
});

// Close chat popup
closeChat.addEventListener('click', () => {
    chatPopup.style.display = 'none';
});

// Clear only the conversation history (keeps welcome message)
function clearConversationHistory() {
    const welcomeMessage = chatMessages.querySelector('.bot-message:first-child');
    chatMessages.innerHTML = '';
    if (welcomeMessage) {
        chatMessages.appendChild(welcomeMessage);
    } else {
        addWelcomeMessage();
    }
}

// Add welcome message
function addWelcomeMessage() {
    addMessage('bot', 
        `Hello! 👋 I'm EduBot, your college assistant. I can help with:<br>
        <ul style="margin-top: 5px; padding-left: 20px;">
            <li>Admissions process</li>
            <li>Program information</li>
            <li>Scholarships & fees</li>
            <li>Campus facilities</li>
        </ul>`
    );
}

// Add message to chat
function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (sender === 'bot') {
        messageDiv.innerHTML = `
            <div class="avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="content">
                <p>${text}</p>
                <span class="time">${time}</span>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="content">
                <p>${text}</p>
                <span class="time">${time}</span>
            </div>
        `;
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show typing indicator
function showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.innerHTML = `
        <div class="avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return typingDiv;
}

// Single function for message sending
async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) {
        return;
    }
    
    addMessage('user', text);
    userInput.value = '';
    
    const typing = showTyping();
    
    try {
        const response = await fetch('http://localhost:5000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        
        if (!response.ok) throw new Error('API error');
        const data = await response.json();
        chatMessages.removeChild(typing);
        addMessage('bot', data.response);
    } catch (error) {
        chatMessages.removeChild(typing);
        addMessage('bot', "Sorry, I'm having trouble connecting. Please try again later.");
        console.error("Chat error:", error);
    }
}

// Button click handler
sendBtn.addEventListener('click', () => {
    sendMessage();
});

// Enter key handler
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
    }
});

// Quick reply buttons
function sendQuickReply(type) {
    const questions = {
        "admission": "What are the admission requirements?",
        "exam": "When are the exams scheduled?",
        "fee": "What is the fee structure?",
        "contact": "How can I contact the college?",
        "courses": "What programs do you offer?",
        "scholarship": "What scholarships are available?",
        "campus": "What campus facilities do you have?"
    };
    
    addMessage('user', questions[type]);
    
    // Show typing indicator
    const typing = showTyping();
    
    setTimeout(() => {
        chatMessages.removeChild(typing);
        addMessage('bot', responses[type]);
    }, 1500);
}

// Voice Recognition Setup
let recognition;

// Check browser support
if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
} else if ('SpeechRecognition' in window) {
    recognition = new SpeechRecognition();
} else {
    micBtn.style.display = 'none';
    console.warn("Speech recognition not supported in this browser");
}

// Configure recognition
if (recognition) {
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        micBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
        micBtn.style.color = 'red';
        addMessage('bot', "I'm listening...");
    };

    recognition.onend = () => {
        micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        micBtn.style.color = '#4a6fa5';
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        sendMessage();
    };

    recognition.onerror = (event) => {
        addMessage('bot', `Error: ${event.error}`);
        micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        micBtn.style.color = '#4a6fa5';
    };
}

// Button click handler
micBtn.addEventListener('click', () => {
    if (recognition) {
        if (micBtn.innerHTML.includes('fa-microphone')) {
            recognition.start();
        } else {
            recognition.stop();
        }
    }
});

// Initialize chat popup as hidden by default
document.addEventListener('DOMContentLoaded', function() {
    if (chatPopup) {
        chatPopup.style.display = 'none';
    }
});