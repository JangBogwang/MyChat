document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');

    const USER_ID = "test_user_123"; // 임시 사용자 ID

    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        messageElement.textContent = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight; // 스크롤을 항상 아래로
    }

    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        appendMessage('user', `나: ${message}`);
        messageInput.value = ''; // 입력창 비우기

        try {
            const response = await fetch('/api/chat', {
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
            appendMessage('ai', `챗봇: ${data.response_msg}`);

        } catch (error) {
            console.error('채팅 요청 중 오류 발생:', error);
            appendMessage('ai', '챗봇: 죄송합니다. 메시지를 처리하는 중 오류가 발생했습니다.');
        }
    }

    sendButton.addEventListener('click', sendMessage);

    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});