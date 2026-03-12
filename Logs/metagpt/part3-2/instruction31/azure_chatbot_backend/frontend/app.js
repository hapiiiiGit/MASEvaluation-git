/**
 * app.js - Chatbot frontend logic
 * Handles user input, communicates with backend, updates UI, and manages errors.
 */

const BACKEND_URL = "https://<YOUR_BACKEND_DOMAIN_OR_IP>:8000/chat"; // Replace with your backend URL

// DOM Elements
const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");

// State
let isAwaitingResponse = false;

/**
 * Adds a message to the chat window.
 * @param {string} text - The message text.
 * @param {'user'|'bot'} sender - Who sent the message.
 */
function addMessage(text, sender) {
    const messageRow = document.createElement("div");
    messageRow.className = "message-row";

    const messageBubble = document.createElement("div");
    messageBubble.className = sender === "user" ? "message-user" : "message-bot";
    messageBubble.textContent = text;

    messageRow.appendChild(messageBubble);
    chatWindow.appendChild(messageRow);

    // Scroll to bottom
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

/**
 * Shows a temporary loading indicator in the chat window.
 */
function showLoading() {
    const loadingRow = document.createElement("div");
    loadingRow.className = "message-row";
    loadingRow.id = "loading-indicator";

    const loadingBubble = document.createElement("div");
    loadingBubble.className = "message-bot";
    loadingBubble.innerHTML = `<span class="loading-dots">...</span>`;

    loadingRow.appendChild(loadingBubble);
    chatWindow.appendChild(loadingRow);

    chatWindow.scrollTop = chatWindow.scrollHeight;
}

/**
 * Removes the loading indicator from the chat window.
 */
function removeLoading() {
    const loadingIndicator = document.getElementById("loading-indicator");
    if (loadingIndicator) {
        chatWindow.removeChild(loadingIndicator);
    }
}

/**
 * Handles form submission: sends user message to backend and displays response.
 * @param {Event} e
 */
chatForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    if (isAwaitingResponse) return;

    const message = userInput.value.trim();
    if (!message) return;

    addMessage(message, "user");
    userInput.value = "";
    userInput.disabled = true;
    isAwaitingResponse = true;
    showLoading();

    try {
        const response = await fetch(BACKEND_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        removeLoading();
        userInput.disabled = false;
        isAwaitingResponse = false;

        if (!response.ok) {
            let errorMsg = "Network error. Please try again.";
            try {
                const errorData = await response.json();
                if (errorData.detail) errorMsg = errorData.detail;
            } catch (_) {}
            addMessage(errorMsg, "bot");
            return;
        }

        const data = await response.json();
        if (data && data.response) {
            addMessage(data.response, "bot");
        } else {
            addMessage("Sorry, I didn't understand that.", "bot");
        }
    } catch (err) {
        removeLoading();
        userInput.disabled = false;
        isAwaitingResponse = false;
        addMessage("Unable to connect to server. Please check your connection.", "bot");
    }
});

// Optional: Focus input on page load
window.addEventListener("DOMContentLoaded", () => {
    userInput.focus();
});