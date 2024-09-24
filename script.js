function sendMessage() {
  const inputField = document.getElementById("chat-input");
  const message = inputField.value.trim();

  if (message !== "") {
    appendMessage(message, "user-message");

    // Bot response
    setTimeout(() => {
      appendMessage("This is sample", "bot-message");
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
