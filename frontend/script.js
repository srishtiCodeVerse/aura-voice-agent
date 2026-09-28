const API_URL = "https://aura-voice-agent-bm5f.onrender.com";

const chatBox = document.getElementById("chatBox");
const input = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const micButton = document.getElementById("micButton");


// =====================================================
// ADD MESSAGE TO CHAT
// =====================================================

function addMessage(message, sender = "bot") {
    if (!chatBox) return;

    const messageDiv = document.createElement("div");

    messageDiv.className =
        sender === "user"
            ? "message user-message"
            : "message bot-message";

    messageDiv.textContent = message;

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}


// =====================================================
// AURA VOICE
// =====================================================

function speak(text) {

    if (!("speechSynthesis" in window)) {
        console.log("Speech synthesis is not supported.");
        return;
    }

    // Stop previous speech
    window.speechSynthesis.cancel();

    const speech = new SpeechSynthesisUtterance(text);

    speech.lang = "en-IN";
    speech.rate = 0.90;
    speech.pitch = 1.05;
    speech.volume = 1;

    // Get available voices
    let voices = window.speechSynthesis.getVoices();

    // Prefer Indian English voice
    let selectedVoice = voices.find(
        voice => voice.lang.toLowerCase() === "en-in"
    );

    // If Indian English voice is unavailable,
    // use any English voice
    if (!selectedVoice) {
        selectedVoice = voices.find(
            voice => voice.lang.toLowerCase().startsWith("en")
        );
    }

    if (selectedVoice) {
        speech.voice = selectedVoice;
    }

    speech.onstart = function () {
        console.log("🔊 Aura started speaking");
    };

    speech.onend = function () {
        console.log("🔊 Aura finished speaking");
    };

    speech.onerror = function (event) {
        console.error("Speech error:", event.error);
    };

    // Speak
    window.speechSynthesis.speak(speech);
}


// =====================================================
// LOAD VOICES
// =====================================================

if ("speechSynthesis" in window) {

    window.speechSynthesis.onvoiceschanged = function () {

        const voices = window.speechSynthesis.getVoices();

        console.log(
            "Available voices:",
            voices.map(voice => `${voice.name} (${voice.lang})`)
        );

    };
}


// =====================================================
// SEND MESSAGE
// =====================================================

async function sendMessage(message = null) {

    if (!input) return;

    const text = message || input.value.trim();

    if (!text) {
        return;
    }

    // Show user message
    addMessage(text, "user");

    input.value = "";

    // Thinking message
    const thinking = document.createElement("div");

    thinking.className = "message bot-message";
    thinking.textContent = "Thinking... 🤔";

    if (chatBox) {
        chatBox.appendChild(thinking);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    try {

        const response = await fetch(`${API_URL}/chat`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: text
            })

        });

        if (!response.ok) {
            throw new Error(
                `Server returned ${response.status}`
            );
        }

        const data = await response.json();

        // Remove Thinking
        thinking.remove();

        const reply =
            data.reply ||
            "Sorry, I couldn't understand that.";

        // Show reply
        addMessage(reply, "bot");

        // Speak reply
        speak(reply);

    } catch (error) {

        console.error("Chat error:", error);

        thinking.remove();

        addMessage(
            "I can't connect to the Aura server. Please make sure the backend is running.",
            "bot"
        );
    }
}


// =====================================================
// SEND BUTTON
// =====================================================

if (sendButton) {

    sendButton.addEventListener("click", function () {

        sendMessage();

    });

}


// =====================================================
// ENTER KEY
// =====================================================

if (input) {

    input.addEventListener("keydown", function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage();

        }

    });

}


// =====================================================
// MICROPHONE / SPEECH RECOGNITION
// =====================================================

let recognition = null;

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;


if (SpeechRecognition) {

    recognition = new SpeechRecognition();

    recognition.lang = "en-IN";

    recognition.continuous = false;

    recognition.interimResults = false;


    // -----------------------------
    // Microphone started
    // -----------------------------

    recognition.onstart = function () {

        console.log("🎙️ Listening...");

        if (micButton) {
            micButton.textContent = "🔴";
        }

    };


    // -----------------------------
    // Speech received
    // -----------------------------

    recognition.onresult = function (event) {

        const transcript =
            event.results[0][0].transcript;

        console.log(
            "🎙️ You said:",
            transcript
        );

        if (input) {
            input.value = transcript;
        }

        sendMessage(transcript);

    };


    // -----------------------------
    // Microphone error
    // -----------------------------

    recognition.onerror = function (event) {

        console.error(
            "Microphone error:",
            event.error
        );

        if (micButton) {
            micButton.textContent = "🎙️";
        }

    };


    // -----------------------------
    // Microphone stopped
    // -----------------------------

    recognition.onend = function () {

        console.log("🎙️ Listening stopped");

        if (micButton) {
            micButton.textContent = "🎙️";
        }

    };


    // -----------------------------
    // Microphone button
    // -----------------------------

    if (micButton) {

        micButton.addEventListener("click", function () {

            try {

                // Make browser allow speech
                if ("speechSynthesis" in window) {
                    window.speechSynthesis.cancel();
                }

                recognition.start();

            } catch (error) {

                console.log(
                    "Microphone already active."
                );

            }

        });

    }


} else {

    console.log(
        "Speech recognition is not supported."
    );

    if (micButton) {

        micButton.addEventListener("click", function () {

            alert(
                "Speech recognition is not supported. Please use Google Chrome or Microsoft Edge."
            );

        });

    }

}


// =====================================================
// QUICK BUTTONS
// =====================================================

document.addEventListener("click", function (event) {

    const button =
        event.target.closest("[data-message]");

    if (!button) {
        return;
    }

    const message =
        button.getAttribute("data-message");

    if (message) {

        sendMessage(message);

    }

});