const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const chatContainer = document.getElementById("chatContainer");
const sendButton = document.getElementById("sendButton");
const clearChat = document.getElementById("clearChat");


// =========================================
// CONFIGURATION
// =========================================

// Local FastAPI during development.
// Vercel uses /api/chat.
const isLocal =
    window.location.protocol === "file:" ||
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1" ||
    window.location.hostname === "";

const API_URL = isLocal
    ? "http://127.0.0.1:8000/chat"
    : "/api/chat";


// =========================================
// CONVERSATION HISTORY
// =========================================

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


    // -----------------------------------------
    // Render AI messages as Markdown
    // -----------------------------------------

    if (
        typeof marked !== "undefined" &&
        typeof DOMPurify !== "undefined"
    ) {

        const rendered =
            marked.parse(
                message || "",
                {
                    gfm: true,
                    breaks: true
                }
            );

        content.innerHTML =
            DOMPurify.sanitize(
                rendered
            );

    } else {

        content.textContent =
            message || "";

    }


    messageElement.appendChild(
        content
    );


    chatContainer.appendChild(
        messageElement
    );


    // Scroll to newest message
    chatContainer.scrollTop =
        chatContainer.scrollHeight;


    return messageElement;
}


// =========================================
// SHOW AI THINKING
// =========================================

function showLoading() {

    const message =
        addMessage(
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


    if (!orb || !label) {
        return message;
    }


    // -----------------------------------------
    // Thinking states
    // -----------------------------------------

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


            // Stop at final state
            if (
                index >=
                states.length
            ) {
                clearInterval(
                    thinkingTimer
                );

                thinkingTimer = null;

                return;
            }


            const current =
                states[index];


            // Change orb state
            orb.dataset.state =
                current.state;


            // Animate label
            label.style.opacity =
                "0";


            setTimeout(() => {

                label.textContent =
                    current.text;

                label.style.opacity =
                    "1";

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

    if (
        !message ||
        !message.trim()
    ) {
        return;
    }


    // -----------------------------------------
    // Add user message
    // -----------------------------------------

    addMessage(
        message,
        "user"
    );


    // -----------------------------------------
    // Disable controls
    // -----------------------------------------

    sendButton.disabled =
        true;

    messageInput.disabled =
        true;


    // -----------------------------------------
    // Show thinking state
    // -----------------------------------------

    const loadingMessage =
        showLoading();


    try {

        // -------------------------------------
        // Send request
        // -------------------------------------

        const response =
            await fetch(
                API_URL,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message:
                            message,

                        history:
                            conversationHistory
                    })
                }
            );


        // -------------------------------------
        // Check response
        // -------------------------------------

        if (!response.ok) {

            let errorMessage =
                `Server error: ${response.status}`;

            try {

                const errorData =
                    await response.json();

                if (errorData.detail) {
                    errorMessage =
                        errorData.detail;
                }

            } catch {
                // Keep default error message
            }


            throw new Error(
                errorMessage
            );
        }


        // -------------------------------------
        // Read response
        // -------------------------------------

        const data =
            await response.json();


        // -------------------------------------
        // Stop thinking
        // -------------------------------------

        stopThinking();


        // -------------------------------------
        // Remove thinking message
        // -------------------------------------

        if (loadingMessage) {
            loadingMessage.remove();
        }


        // -------------------------------------
        // Validate AI response
        // -------------------------------------

        const aiResponse =
            data?.response;


        if (!aiResponse) {

            throw new Error(
                "AI returned an empty response."
            );
        }


        // -------------------------------------
        // Add AI response
        // -------------------------------------

        addMessage(
            aiResponse,
            "ai"
        );


        // -------------------------------------
        // Save conversation history
        // -------------------------------------

        conversationHistory.push({

            role: "user",

            content:
                message

        });


        conversationHistory.push({

            role: "assistant",

            content:
                aiResponse

        });


    } catch (error) {

        console.error(
            "Chat error:",
            error
        );


        // -------------------------------------
        // Stop thinking
        // -------------------------------------

        stopThinking();


        // -------------------------------------
        // Remove thinking message
        // -------------------------------------

        if (loadingMessage) {
            loadingMessage.remove();
        }


        // -------------------------------------
        // Error response
        // -------------------------------------

        addMessage(
            "Sorry, I couldn't connect to the AI server. Please try again.",
            "ai"
        );

    } finally {

        // -------------------------------------
        // Re-enable controls
        // -------------------------------------

        sendButton.disabled =
            false;

        messageInput.disabled =
            false;


        // -------------------------------------
        // Focus input
        // -------------------------------------

        messageInput.focus();


        // -------------------------------------
        // Scroll to bottom
        // -------------------------------------

        chatContainer.scrollTo({

            top:
                chatContainer.scrollHeight,

            behavior:
                "smooth"

        });

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
                        button.textContent
                            .trim();


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


// =========================================
// CONNECT INITIAL SUGGESTIONS
// =========================================

connectSuggestionButtons();


// =========================================
// CLEAR CHAT
// =========================================

clearChat.addEventListener(
    "click",
    () => {

        // -------------------------------------
        // Clear conversation history
        // -------------------------------------

        conversationHistory = [];


        // -------------------------------------
        // Stop thinking animation
        // -------------------------------------

        stopThinking();


        // -------------------------------------
        // Restore welcome screen
        // -------------------------------------

        chatContainer.innerHTML = `

            <div class="welcome">

                <div class="welcome-orb">
                    <i data-lucide="sparkles"></i>
                </div>


                <h2>
                    Hello
                    <i
                        data-lucide="hand"
                        class="hello-hand"
                    ></i>
                </h2>


                <h3>
                    How can I help you today?
                </h3>


                <p>
                    Ask about courses, admissions,
                    notices, programs and college
                    information.
                </p>


                <div class="suggestions">


                    <button class="suggestion">

                        <span class="suggestion-icon">
                            <i
                                data-lucide="book-open"
                            ></i>
                        </span>

                        <span>
                            <strong>
                                Courses
                            </strong>

                            <small>
                                Explore available courses
                            </small>
                        </span>

                    </button>


                    <button class="suggestion">

                        <span class="suggestion-icon">
                            <i
                                data-lucide="megaphone"
                            ></i>
                        </span>

                        <span>
                            <strong>
                                Notices
                            </strong>

                            <small>
                                Find the latest updates
                            </small>
                        </span>

                    </button>


                    <button class="suggestion">

                        <span class="suggestion-icon">
                            <i
                                data-lucide="graduation-cap"
                            ></i>
                        </span>

                        <span>
                            <strong>
                                Programs
                            </strong>

                            <small>
                                Explore academic programs
                            </small>
                        </span>

                    </button>


                    <button class="suggestion">

                        <span class="suggestion-icon">
                            <i
                                data-lucide="sparkles"
                            ></i>
                        </span>

                        <span>
                            <strong>
                                Ask AI
                            </strong>

                            <small>
                                Ask me anything
                            </small>
                        </span>

                    </button>


                </div>

            </div>

        `;


        // -------------------------------------
        // Recreate Lucide icons
        // -------------------------------------

        if (
            typeof lucide !== "undefined"
        ) {

            lucide.createIcons();

        }


        // -------------------------------------
        // Reconnect suggestions
        // -------------------------------------

        connectSuggestionButtons();


        // -------------------------------------
        // Reset scroll
        // -------------------------------------

        chatContainer.scrollTop = 0;


        // -------------------------------------
        // Focus input
        // -------------------------------------

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