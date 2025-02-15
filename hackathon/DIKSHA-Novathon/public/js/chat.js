// Define a function to add a message to the chatbox
function addMessage(text, sender) {
    var chatbox = document.getElementById("chatbox");
    var messageDiv = document.createElement("div");
    messageDiv.textContent = (sender === "user" ? "You: " : "Chatbot: ") + text;
    chatbox.appendChild(messageDiv);
    chatbox.scrollTop = chatbox.scrollHeight; // Auto-scroll to the bottom
}

// Function to handle user input and chatbot response
function sendMessage() {
    var userInput = document.getElementById("userInput").value;
    addMessage(userInput, "user");

    // Send the user input to the server for processing by the chatbot
    fetch("/chatbot", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        // Display the chatbot's response in the chatbox
        addMessage(data.message, "chatbot");
    })
    .catch(error => console.error("Error:", error));

    // Clear the input field after sending the message
    document.getElementById("userInput").value = "";
}

// Add an event listener to the send button
document.getElementById("sendBtn").addEventListener("click", sendMessage);

// Pressing Enter key also sends the message
document.getElementById("userInput").addEventListener("keyup", function(event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        document.getElementById("sendBtn").click();
    }
});
