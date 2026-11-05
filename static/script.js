
// ============================================
// HEALTHCARE AI CHATBOT
// FRONTEND - FLASK BACKEND CONNECTION
// ============================================


// GET HTML ELEMENTS

const chatBox = document.getElementById("chatBox");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");
const clearButton = document.getElementById("clearChat");
const typingIndicator = document.getElementById("typingIndicator");


// CHECK HTML ELEMENTS

if (
    !chatBox ||
    !chatForm ||
    !userInput ||
    !sendButton ||
    !clearButton ||
    !typingIndicator
) {
    console.error("ERROR: One or more HTML elements are missing.");
}


// ============================================
// DISPLAY CHAT MESSAGE
// ============================================

function addMessage(message, sender, source = null) {

    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message");

    messageDiv.classList.add(
        sender === "user" ? "user-message" : "bot-message"
    );

    const avatar = document.createElement("div");

    avatar.classList.add("avatar");

    avatar.textContent = sender === "user" ? "U" : "✚";

    const content = document.createElement("div");

    content.classList.add("message-content");

    const name = document.createElement("span");

    name.classList.add("sender");

    name.textContent =
        sender === "user" ? "You" : "HealthCare AI";

    const bubble = document.createElement("div");

    bubble.classList.add("bubble");

    bubble.textContent = message;

    content.appendChild(name);
    content.appendChild(bubble);

    // Display source if backend provides one

    if (sender === "bot" && source && source.url) {

        try {

            const parsedURL = new URL(source.url);

            if (
                parsedURL.protocol === "https:" ||
                parsedURL.protocol === "http:"
            ) {

                const sourceLink = document.createElement("a");

                sourceLink.href = parsedURL.href;

                sourceLink.textContent =
                    "Information source: " +
                    (source.name || "Read more");

                sourceLink.target = "_blank";

                sourceLink.rel = "noopener noreferrer";

                content.appendChild(sourceLink);
            }

        } catch (error) {

            console.warn("Invalid source URL:", error);

        }
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    // IMPORTANT: Add message directly to chatBox.
    // typingIndicator is outside chatBox.

    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;
}


// ============================================
// SHOW TYPING INDICATOR
// ============================================

function showTyping() {

    typingIndicator.hidden = false;

}


// ============================================
// HIDE TYPING INDICATOR
// ============================================

function hideTyping() {

    typingIndicator.hidden = true;

}


// ============================================
// SEND MESSAGE TO FLASK BACKEND
// ============================================

async function sendMessage(message) {

    const cleanMessage = message.trim();

    if (!cleanMessage) {
        return;
    }

    if (sendButton.disabled) {
        return;
    }

    // Display user message

    addMessage(cleanMessage, "user");

    // Clear input

    userInput.value = "";

    // Disable controls

    sendButton.disabled = true;

    userInput.disabled = true;

    showTyping();

    try {

        console.log("Sending message to Flask:", cleanMessage);

        // CONNECT TO FLASK BACKEND

        const response = await fetch("/api/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: cleanMessage
            })

        });

        // Read backend response

        const data = await response.json();

        console.log("Backend response:", data);

        // Check response

        if (!response.ok) {

            throw new Error(
                data.message || "Server error: " + response.status
            );

        }

        if (data.status !== "success") {

            throw new Error(
                data.message || "Chatbot could not process your question."
            );

        }

        // Display chatbot answer

        addMessage(
            data.response,
            "bot",
            data.source || null
        );

    } catch (error) {

        console.error("CHATBOT ERROR:", error);

        addMessage(
            "Sorry! Something went wrong while connecting to the healthcare server. Please check the Flask backend and try again.",
            "bot"
        );

    } finally {

        hideTyping();

        sendButton.disabled = false;

        userInput.disabled = false;

        userInput.focus();

    }

}


// ============================================
// CHAT FORM SUBMISSION
// ============================================

chatForm.addEventListener("submit", function(event) {

    event.preventDefault();

    sendMessage(userInput.value);

});


// ============================================
// QUICK QUESTION BUTTONS
// ============================================

const quickButtons = document.querySelectorAll(".quick-btn");

quickButtons.forEach(function(button) {

    button.addEventListener("click", function() {

        const question =
            button.dataset.question || button.textContent.trim();

        sendMessage(question);

    });

});


// ============================================
// CLEAR CONVERSATION
// ============================================

clearButton.addEventListener("click", function() {

    const confirmed = confirm(
        "Do you want to clear the conversation displayed on this page?"
    );

    if (!confirmed) {
        return;
    }

    chatBox.replaceChildren();

    addMessage(
        "Hello! Welcome to HealthCare AI. How can I help you today?",
        "bot"
    );

    hideTyping();

    userInput.value = "";

    console.log("Chat display cleared.");

});


// ============================================
// INITIAL MESSAGE
// ============================================

console.log(
    "Healthcare AI Frontend Successfully Loaded!"
);
