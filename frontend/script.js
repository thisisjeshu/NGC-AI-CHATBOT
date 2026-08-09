const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const chatContainer = document.getElementById("chatContainer");
const sendButton = document.getElementById("sendButton");
const clearChat = document.getElementById("clearChat");


// Add a message to the chat
function addMessage(message, sender) {

    const messageElement = document.createElement("div");

    messageElement.classList.add("message", sender);

    const content = document.createElement("div");

    content.classList.add("message-content");

    content.textContent = message;

    messageElement.appendChild(content);

    chatContainer.appendChild(messageElement);

    chatContainer.scrollTop = chatContainer.scrollHeight;

    return messageElement;
}


// Show loading message
function showLoading() {

    return addMessage(
        "Thinking...",
        "ai"
    );
}


// Send message
async function sendMessage(message) {

    addMessage(message, "user");

    sendButton.disabled = true;
    messageInput.disabled = true;

    const loadingMessage = showLoading();

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/chat",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    message: message
                })
            }
        );


        if (!response.ok) {

            throw new Error(
                `Server error: ${response.status}`
            );
        }


        const data = await response.json();


        // Remove "Thinking..."
        loadingMessage.remove();


        addMessage(
            data.response,
            "ai"
        );


    } catch (error) {

        console.error(error);

        loadingMessage.remove();

        addMessage(
            "Sorry, I couldn't connect to the AI server. Please try again.",
            "ai"
        );

    } finally {

        sendButton.disabled = false;
        messageInput.disabled = false;

        messageInput.focus();
    }
}


// Form submission
chatForm.addEventListener(
    "submit",
    function (event) {

        event.preventDefault();

        const message = messageInput.value.trim();

        if (!message) {
            return;
        }

        messageInput.value = "";

        sendMessage(message);
    }
);


// Suggestion buttons
document.querySelectorAll(".suggestion").forEach(
    button => {

        button.addEventListener(
            "click",
            () => {

                const message = button.textContent.trim();

                sendMessage(message);
            }
        );

    }
);


// Clear chat
clearChat.addEventListener(
    "click",
    () => {

        chatContainer.innerHTML = `
            <div class="welcome">

                <div class="welcome-icon">
                    ✦
                </div>

                <h2>Hello 👋</h2>

                <p>
                    I'm NGC AI, your college assistant.
                    Ask me anything to get started.
                </p>

                <div class="suggestions">

                    <button class="suggestion">
                        What can you help me with?
                    </button>

                    <button class="suggestion">
                        Tell me about BCA
                    </button>

                    <button class="suggestion">
                        How can I use this chatbot?
                    </button>

                </div>

            </div>
        `;

        // Reconnect suggestion buttons
        document.querySelectorAll(".suggestion").forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        sendMessage(
                            button.textContent.trim()
                        );

                    }
                );

            }
        );

    }
);


// Enter = send
messageInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            chatForm.requestSubmit();
        }

    }
);