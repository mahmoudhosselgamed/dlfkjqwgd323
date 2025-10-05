const sendBtn = document.getElementById("send-btn");
const userInput = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");

// 🧠 Format bot responses with color, spacing, and structure
function formatResponse(title, summary) {
  let formatted = summary
    .replace(/(Impacts:)/gi, '<strong style="color:#00ffff;">$1</strong>')
    .replace(/(Results:)/gi, '<strong style="color:#ff66cc;">$1</strong>')
    .replace(/(Areas_of Scientific Progress:)/gi, '<strong style="color:#66ff99;">$1</strong>')
    .replace(/(Knowledge Gaps:)/gi, '<strong style="color:#ffcc00;">$1</strong>')
    .replace(/(Areas_of Consensus or Disagreement:)/gi, '<strong style="color:#ff9966;">$1</strong>')
    .replace(/(Actionable Insights to Mission Planners:)/gi, '<strong style="color:#00ffcc;">$1</strong>');

  // Add line breaks between sentences
  formatted = formatted.replace(/\. /g, '.<br><br>');

  return `
    <div class="nasa-response">
      <h3 class="nasa-title">🛰️ ${title || "Untitled Research"}</h3>
      <div class="nasa-summary">${formatted || "No summary found."}</div>
    </div>
  `;
}

// 🚀 Send user message and handle response
async function sendMessage() {
  const query = userInput.value.trim();
  if (!query) return;

  addMessage("user", query);
  userInput.value = "";
  addMessage("bot", "Searching NASA research... 🛰️");

  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });

    if (!response.ok) throw new Error("Server error");

    const data = await response.json();

    // Remove “Searching…” placeholder
    const lastBotMsg = document.querySelector(".bot-msg:last-child");
    if (lastBotMsg) lastBotMsg.remove();

    // 🪐 Add formatted bot message
    const formatted = formatResponse(data.title, data.summary);
    addMessage("bot", formatted);

  } catch (err) {
    console.error("Fetch error:", err);
    const lastBotMsg = document.querySelector(".bot-msg:last-child");
    if (lastBotMsg) lastBotMsg.remove();
    addMessage("bot", "❌ Error: Could not reach the NASA bot server.");
  }
}

// 💬 Add messages to chat window
function addMessage(sender, text) {
  const msgDiv = document.createElement("div");
  msgDiv.className = sender === "user" ? "user-msg" : "bot-msg";
  msgDiv.innerHTML = text;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// ⚡ Event listeners
sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
