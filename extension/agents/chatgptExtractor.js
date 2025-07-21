function extractChatGptPair() {
    const blocks = Array.from(document.querySelectorAll('[data-message-author-role]'));
    for (let i = 0; i < blocks.length - 1; i++) {
        const userBlock = blocks[i];
        const assistantBlock = blocks[i + 1];
        const isUser = userBlock.getAttribute('data-message-author-role') === 'user';
        const isAssistant = assistantBlock.getAttribute('data-message-author-role') === 'assistant';
        const userText = userBlock.querySelector('.markdown.prose')?.innerText?.trim() ||
            userBlock.textContent?.trim();
        const assistantText = assistantBlock.querySelector('.markdown.prose')?.innerText?.trim() ||
            assistantBlock.textContent?.trim();
        if (isUser && isAssistant && userText && assistantText) {
            return {
                question: userText,
                answer: assistantText,
                url: window.location.href,
                timestamp: new Date().toISOString(),
            };
        }
    }
    return null;
}
function sendToBackend(payload) {
    console.log("🟦 [ChatGPT] Sending to backend:", payload);
    fetch("http://localhost:8001/save_chatgpt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    }).then(res => {
        if (!res.ok) {
            console.warn("❌ ChatGPT send failed - Status:", res.status, res.statusText);
        }
        else {
            console.log("✅ ChatGPT data sent successfully");
        }
    }).catch(err => {
        console.error("❌ ChatGPT send error:", err);
    });
}
export function initChatGPTExtractor() {
    console.log("🧠 ChatGPT extractor activated");
    const observer = new MutationObserver(() => {
        const result = extractChatGptPair();
        if (result) {
            console.log("🟦 [ChatGPT FIRST PAIR] ❓", result.question);
            console.log("🟦 [ChatGPT FIRST PAIR] 💬", result.answer);
            sendToBackend(result);
            observer.disconnect();
        }
    });
    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });
}
if (window.location.hostname.includes("chatgpt.com")) {
    initChatGPTExtractor();
}
