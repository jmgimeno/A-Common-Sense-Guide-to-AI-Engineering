/***
 * Excerpted from "A Common-Sense Guide to AI Engineering",
 * published by The Pragmatic Bookshelf.
 * Copyrights apply to this code. It may not be used to create training material,
 * courses, books, articles, and the like. Contact us if you are in doubt.
 * We make no guarantees that this code is fit for any purpose.
 * Visit https://pragprog.com/titles/jwpaieng for more book information.
***/
// Grab DOM references once so we can reuse them everywhere.
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const newChatButton = document.getElementById('new-chat-button');

// localStorage key used to persist session id across refreshes.
const SESSION_STORAGE_KEY = 'chat_session_id';
// In-memory session id currently used for API calls.
let sessionId = '';

// Ask backend for a brand-new session id (UUID).
async function fetchNewSessionId() {
  const response = await fetch('/new-session', {
    method: 'POST',
  });
  const data = await response.json();
  return data.session_id;
}

// Ensure we always have a session id before chat starts.
async function ensureSessionId() {
  // Try to restore previous session id from browser storage.
  const storedSessionId = localStorage.getItem(SESSION_STORAGE_KEY);
  if (storedSessionId) {
    sessionId = storedSessionId;
    return;
  }

  // No existing session; create one and persist it.
  sessionId = await fetchNewSessionId();
  localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
}

// Render one chat bubble into the message list.
function appendMessage(role, content) {
  const messageEl = document.createElement('div');
  // Role class ("user" or "assistant") controls bubble alignment/style.
  messageEl.className = `message ${role}`;
  messageEl.textContent = content;
  chatMessages.appendChild(messageEl);
  // Keep newest message visible.
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Reset visible chat panel for current session.
function resetChat() {
  // Remove all rendered messages in the UI.
  chatMessages.innerHTML = '';
  // Put cursor in input for fast typing.
  messageInput.focus();
}

// Fetch existing messages for the active session and render them.
async function loadHistory() {
  const response = await fetch(`/history/${sessionId}`);
  const data = await response.json();
  const messages = data.messages;

  // If no history exists, show a starter assistant message.
  if (!messages.length) {
    appendMessage('assistant', 'How can I help you today?');
    return;
  }

  // Replay stored conversation into the UI.
  messages.forEach((message) => {
    appendMessage(message.role, message.content);
  });
}

// Handle send-message form submission.
chatForm.addEventListener('submit', async (event) => {
  // Prevent full page reload.
  event.preventDefault();

  // Read and trim user input.
  const user_input = messageInput.value.trim();
  // Ignore empty submissions.
  if (!user_input) {
    return;
  }

  // Optimistically show the user message.
  appendMessage('user', user_input);
  // Clear input box immediately after send.
  messageInput.value = '';

  // Send chat request to backend.
  const response = await fetch('/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      user_input,
    }),
  });

  // Render model reply.
  const data = await response.json();
  appendMessage('assistant', data.reply);
  messageInput.focus();
});

// Handle "New Chat" button by rotating to a fresh session.
newChatButton.addEventListener('click', async () => {
  sessionId = await fetchNewSessionId();
  localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
  // Rebuild UI for the new session.
  resetChat();
  // Load history for the new session (normally empty).
  await loadHistory();
});

// App startup sequence.
async function initializeChat() {
  // 1) Ensure session id exists.
  await ensureSessionId();
  // 2) Reset display.
  resetChat();
  // 3) Restore saved history.
  await loadHistory();
}

// Kick off initialization when script loads.
initializeChat();
