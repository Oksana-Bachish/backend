function toggleAIChat() {
    const windowDiv = document.getElementById('ai-chat-window');
    const launcherDiv = document.getElementById('ai-chat-launcher');

    // Открытие/закрытие окна чата
    if (windowDiv.style.display === 'none' || windowDiv.style.display === '') {
        windowDiv.style.display = 'flex';
        launcherDiv.style.transform = 'scale(0.9) rotate(90deg)';
        document.getElementById('ai-chat-input').focus();
    } else {
        windowDiv.style.display = 'none';
        launcherDiv.style.transform = 'scale(1) rotate(0deg)';
    }
}

function handleChatKeyPress(event) {
    // Отправка по Enter
    if (event.key === 'Enter') {
        sendAIChatMessage();
    }
}

async function sendAIChatMessage() {
    const inputEl = document.getElementById('ai-chat-input');
    const messageText = inputEl.value.trim();

    if (!messageText) return;

    inputEl.value = '';

    const messagesContainer = document.getElementById('ai-chat-messages');
    const loadingEl = document.getElementById('ai-chat-loading');

    // Рендер сообщения пользователя
    const userMessageHtml = `<div class="ai-message-user">${messageText}</div>`;
    messagesContainer.insertAdjacentHTML('beforeend', userMessageHtml);

    loadingEl.style.display = 'block';
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        // CSRF для Django API
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

        // Запрос к Django → FastAPI микросервису
        const response = await fetch('/products/api/ai-consultant/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ message: messageText })
        });

        const data = await response.json();
        loadingEl.style.display = 'none';

        if (data.status === 'success') {
            // Рендер ответа ИИ
            const formattedResponse = data.response.replace(/\n/g, '<br>');
            const botMessageHtml = `<div class="ai-message-bot">${formattedResponse}</div>`;
            messagesContainer.insertAdjacentHTML('beforeend', botMessageHtml);
        } else {
            throw new Error(data.message || 'Ошибка сервера');
        }

    } catch (error) {
        loadingEl.style.display = 'none';
        const errorHtml = `<div class="ai-message-error">🤖 Ой, что-то пошло не так: ${error.message}.</div>`;
        messagesContainer.insertAdjacentHTML('beforeend', errorHtml);
    }

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
