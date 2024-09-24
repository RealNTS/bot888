// Function to send user message and bot response
function sendMessage() {
  const inputField = document.getElementById("chat-input");
  const message = inputField.value.trim();

  if (message !== "") {
    appendMessage(message, "user-message");
    
    // Show typing indicator
    showTypingIndicator();

    // Bot response after a delay
    setTimeout(() => {
      hideTypingIndicator();
      appendMessage("This is sample", "bot-message");
    }, 1000);

    inputField.value = "";
  } else {
    alert("Please enter a message.");
  }
}

// Function to append message to chat
function appendMessage(message, className) {
  const chatBox = document.getElementById("chat-box");
  const messageElement = document.createElement("div");
  messageElement.classList.add("chat-message", className);
  messageElement.textContent = message;
  chatBox.appendChild(messageElement);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to clear chat history
function clearChat() {
  const chatBox = document.getElementById("chat-box");
  chatBox.innerHTML = "";
}

// Function to show typing indicator
function showTypingIndicator() {
  const chatBox = document.getElementById("chat-box");
  const typingElement = document.createElement("div");
  typingElement.classList.add("chat-message", "bot-message", "typing-indicator");
  typingElement.textContent = "ChatGPT is typing...";
  typingElement.id = "typing-indicator";
  chatBox.appendChild(typingElement);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to hide typing indicator
function hideTypingIndicator() {
  const typingElement = document.getElementById("typing-indicator");
  if (typingElement) {
    typingElement.remove();
  }
}

// Function to handle Enter key press to send message
document.getElementById("chat-input").addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});
