document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const chatbotNameElement = document.getElementById('chatbot-name');
    const typingIndicator = document.getElementById('typing-indicator');

    const USER_ID = "test_user_123"; // 임시 사용자 ID

    // Fetch and set chatbot name
    async function setChatbotName() {
        try {
            const response = await fetch('/api/chat/sender');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            chatbotNameElement.textContent = `💬 ${data.sender}`;
        } catch (error) {
            console.error('Error fetching chatbot name:', error);
            chatbotNameElement.textContent = '💬 나만의 스마트 챗봇';
        }
    }

    setChatbotName();

    function showTypingIndicator() {
        typingIndicator.style.display = 'flex';
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
    }

    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        messageElement.textContent = message;
        chatMessages.insertBefore(messageElement, typingIndicator); // 타이핑 인디케이터 전에 메시지 추가
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        appendMessage('user', `${message}`);
        messageInput.value = '';
        showTypingIndicator();

        try {
            const response = await await fetch('/api/chat/', { // URL 수정
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: USER_ID,
                    message: message
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            appendMessage('ai', `${data.response_msg}`);

        } catch (error) {
            console.error('채팅 요청 중 오류 발생:', error);
            appendMessage('ai', '죄송합니다. 메시지를 처리하는 중 오류가 발생했습니다.');
        } finally {
            hideTypingIndicator();
        }
    }

    sendButton.addEventListener('click', sendMessage);

    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    appendMessage('ai', '안녕하세요! 무엇을 도와드릴까요? 😊');
    hideTypingIndicator();
});