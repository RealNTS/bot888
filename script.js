function sendMessage() {
  const inputField = document.getElementById("chat-input");
  const message = inputField.value.trim();

  if (message !== "") {
    appendMessage(message, "user-message");

    // Simulating bot response
    setTimeout(() => {
      appendMessage("This is a bot response to: " + message, "bot-message");
    }, 1000);

    inputField.value = "";
  }
}

function appendMessage(message, className) {
  const chatBox = document.getElementById("chat-box");
  const messageElement = document.createElement("div");
  messageElement.classList.add("chat-message", className);
  messageElement.textContent = message;
  chatBox.appendChild(messageElement);
  chatBox.scrollTop = chatBox.scrollHeight;
}
