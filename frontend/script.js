const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const chatContainer = document.getElementById("chatContainer");
const sendButton = document.getElementById("sendButton");
const clearChat = document.getElementById("clearChat");
// Conversation history
let conversationHistory = [];

// =========================================
// THINKING STATE
// =========================================

let thinkingTimer = null;


// =========================================
// ADD MESSAGE
// =========================================

function addMessage(message, sender) {

    const messageElement =
        document.createElement("div");

    messageElement.classList.add(
        "message",
        sender
    );

    const content =
        document.createElement("div");

    content.classList.add(
        "message-content"
    );


    // AI messages → Markdown
    if (sender === "ai") {

        if (
            typeof marked !== "undefined" &&
            typeof DOMPurify !== "undefined"
        ) {

            const rendered =
                marked.parse(message, {
                    gfm: true,
                    breaks: true
                });

            content.innerHTML =
                DOMPurify.sanitize(rendered);

        } else {

            content.textContent = message;

        }

    }

    // User messages → plain text
    else {

        content.textContent = message;

    }


    messageElement.appendChild(
        content
    );

    chatContainer.appendChild(
        messageElement
    );

    chatContainer.scrollTop =
        chatContainer.scrollHeight;

    return messageElement;
}


// =========================================
// SHOW AI THINKING
// =========================================

function showLoading() {

    const message = addMessage(
        "",
        "ai"
    );

    const content =
        message.querySelector(
            ".message-content"
        );

    if (!content) {
        return message;
    }


    content.innerHTML = `

        <div class="thinking-state">

            <div
                class="thinking-orb"
                data-state="searching"
                aria-label="AI is thinking"
            >

                <span
                    class="orb-ring ring-1"
                ></span>

                <span
                    class="orb-ring ring-2"
                ></span>

                <span
                    class="orb-core"
                ></span>

            </div>


            <span class="thinking-label">
                Searching...
            </span>

        </div>

    `;


    const orb =
        content.querySelector(
            ".thinking-orb"
        );

    const label =
        content.querySelector(
            ".thinking-label"
        );


    // Thinking states
    const states = [

        {
            state: "searching",
            text: "Searching..."
        },

        {
            state: "weaving",
            text: "Finding relevant information..."
        },

        {
            state: "composing",
            text: "Composing..."
        }

    ];


    let index = 0;


    thinkingTimer =
        setInterval(() => {

            index++;

            if (
                index >=
                states.length
            ) {
                return;
            }


            const current =
                states[index];


            // Change orb state
            orb.dataset.state =
                current.state;


            // Animate text transition
            label.style.opacity = "0";


            setTimeout(() => {

                label.textContent =
                    current.text;

                label.style.opacity = "1";

            }, 150);


        }, 1600);


    return message;
}


// =========================================
// STOP THINKING
// =========================================

function stopThinking() {

    if (thinkingTimer) {

        clearInterval(
            thinkingTimer
        );

        thinkingTimer = null;
    }
}


// =========================================
// SEND MESSAGE
// =========================================

async function sendMessage(message) {

    if (!message || !message.trim()) {
        return;
    }


    // Add user message
    addMessage(
        message,
        "user"
    );


    // Disable controls
    sendButton.disabled = true;
    messageInput.disabled = true;


    // Show AI thinking animation
    const loadingMessage =
        showLoading();


    try {

        const response =
            await fetch(
                "http://127.0.0.1:8000/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message,
                        history: conversationHistory
                    })
                }
            );




        // Check server response
        if (!response.ok) {

            throw new Error(
                `Server error: ${response.status}`
            );
        }


        // Read response
        const data =
            await response.json();


        // Stop thinking animation
        stopThinking();


        // Remove thinking message
        loadingMessage.remove();


        // Add AI response
        addMessage(
            data.response,
            "ai"
        );


    } catch (error) {

        console.error(
            "Chat error:",
            error
        );


        // Stop thinking animation
        stopThinking();


        // Remove thinking message
        loadingMessage.remove();


        // Show error
        addMessage(
            "Sorry, I couldn't connect to the AI server. Please try again.",
            "ai"
        );


    } finally {

        // Re-enable controls
        sendButton.disabled = false;
        messageInput.disabled = false;


        // Focus input
        messageInput.focus();


        // Scroll to bottom
        chatContainer.scrollTo({
            top:
                chatContainer.scrollHeight,
            behavior: "smooth"
        });

    }
}

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
                    message: message,
                    history: conversationHistory
                })
            }
        );


        if (!response.ok) {

            throw new Error(
                `Server error: ${response.status}`
            );

        }


        const data = await response.json();


        loadingMessage.remove();


        addMessage(
            data.response,
            "ai"
        );


        // Save conversation
        conversationHistory.push({
            role: "user",
            content: message
        });

        conversationHistory.push({
            role: "assistant",
            content: data.response
        });


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


// =========================================
// FORM SUBMISSION
// =========================================

chatForm.addEventListener(
    "submit",
    function (event) {

        event.preventDefault();


        const message =
            messageInput.value.trim();


        if (!message) {
            return;
        }


        // Clear input
        messageInput.value = "";


        // Send message
        sendMessage(
            message
        );

    }
);


// =========================================
// SUGGESTION BUTTONS
// =========================================

function connectSuggestionButtons() {

    document
        .querySelectorAll(".suggestion")
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    const message =
                        button.textContent.trim();


                    if (!message) {
                        return;
                    }


                    sendMessage(
                        message
                    );

                }
            );

        });
}


// Connect initial buttons
connectSuggestionButtons();


// =========================================
// CLEAR CHAT
// =========================================

clearChat.addEventListener(
    "click",
    () => {

        // Clear conversation history
        conversationHistory = [];


        // Restore the current welcome screen
        chatContainer.innerHTML = `
            <div class="welcome">

                <div class="welcome-orb">
                    <i data-lucide="sparkles"></i>
                </div>

                <h2>
                    Hello
                    <i data-lucide="hand" class="hello-hand"></i>
                </h2>

                <h3>
                    How can I help you today?
                </h3>

                <p>
                    Ask about courses, admissions, notices,
                    programs and college information.
                </p>


                <div class="suggestions">

                    <button class="suggestion">

                        <span class="suggestion-icon">
                            <i data-lucide="book-open"></i>
                        </span>

                        <span>
                            <strong>Courses</strong>
                            <small>Explore available courses</small>
                        </span>

                    </button>


                    <button class="suggestion">

                        <span class="suggestion-icon">
                            <i data-lucide="megaphone"></i>
                        </span>

                        <span>
                            <strong>Notices</strong>
                            <small>Find the latest updates</small>
                        </span>

                    </button>


                    <button class="suggestion">

                        <span class="suggestion-icon">
                            <i data-lucide="graduation-cap"></i>
                        </span>

                        <span>
                            <strong>Programs</strong>
                            <small>Explore academic programs</small>
                        </span>

                    </button>


                    <button class="suggestion">

                        <span class="suggestion-icon">
                            <i data-lucide="sparkles"></i>
                        </span>

                        <span>
                            <strong>Ask AI</strong>
                            <small>Ask me anything</small>
                        </span>

                    </button>

                </div>

            </div>
        `;


        // Recreate Lucide icons
        lucide.createIcons();


        // Reconnect suggestion buttons
        document
            .querySelectorAll(".suggestion")
            .forEach(button => {

                button.addEventListener(
                    "click",
                    () => {

                        sendMessage(
                            button.textContent.trim()
                        );

                    }
                );

            });


        // Reset scroll
        chatContainer.scrollTop = 0;


        // Focus input
        messageInput.focus();

    }
);

// =========================================
// ENTER = SEND
// =========================================

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


// =========================================
// LUCIDE ICONS
// =========================================

if (
    typeof lucide !== "undefined"
) {

    lucide.createIcons();

}