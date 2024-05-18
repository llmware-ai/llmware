function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() === '') return;

    const chatBox = document.getElementById('chat-box');
    const userMessage = `
                <div class="flex justify-end">
                    <div class="bg-gray-600 text-gray-200 text-lg rounded-lg px-4 py-2 max-w-xl">
                        <p>${userInput}</p>
                    </div>
                </div>
            `;
    chatBox.innerHTML += userMessage;

    document.getElementById('user-input').value = '';

    chatBox.scrollTop = chatBox.scrollHeight;

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userInput })
    })
        .then(response => response.json())
        .then(data => {
            const botMessage = `
                    <div class="flex justify-start">
                        <div class="bg-gray-700 text-gray-200 text-lg rounded-lg px-4 py-2 max-w-4xl">
                            <p>${data.response}</p>
                        </div>
                    </div>
                `;
            chatBox.innerHTML += botMessage;

            chatBox.scrollTop = chatBox.scrollHeight;
        });
}