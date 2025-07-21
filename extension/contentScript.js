// ChatGPT Extractor Functions
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

function sendChatGPTToBackend(payload) {
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

function initChatGPTExtractor() {
    console.log("🧠 ChatGPT extractor activated");
    const observer = new MutationObserver(() => {
        const result = extractChatGptPair();
        if (result) {
            console.log("🟦 [ChatGPT FIRST PAIR] ❓", result.question);
            console.log("🟦 [ChatGPT FIRST PAIR] 💬", result.answer);
            sendChatGPTToBackend(result);
            observer.disconnect();
        }
    });
    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });
}

// Perplexity Extractor Functions
function extractPerplexityMessages() {
  const markdownBlocks = Array.from(document.querySelectorAll('.markdown, .prose, .group'))
    .map(el => el.innerText.trim())
    .filter(text => text.length > 50 && !text.includes("Related") && !text.startsWith("Sources"));

  if (markdownBlocks.length >= 2) {
    const lastQuestion = markdownBlocks[markdownBlocks.length - 2];
    const lastAnswer = markdownBlocks[markdownBlocks.length - 1];

    return {
      question: lastQuestion,
      answer: lastAnswer
    };
  } else {
    console.warn("❌ Not enough meaningful markdown blocks found.");
    return null;
  }
}

function sendPerplexityToBackend(payload) {
  console.log("🟦 [Perplexity] Sending to backend:", payload);
  fetch("http://localhost:8001/save_perplexity", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then(res => {
    if (!res.ok) {
      console.warn("❌ Perplexity send failed - Status:", res.status, res.statusText);
    } else {
      console.log("✅ Perplexity data sent successfully");
    }
  }).catch(err => {
    console.error("❌ Perplexity send error:", err);
  });
}

function initPerplexityExtractor() {
  console.log("🧠 Perplexity extractor activated");

  const observer = new MutationObserver(() => {
    const qa = extractPerplexityMessages();
    if (qa) {
      console.log("🟦 [Perplexity] Q:", qa.question);
      console.log("🟦 [Perplexity] A:", qa.answer);

      sendPerplexityToBackend({
        question: qa.question,
        answer: qa.answer,
        url: window.location.href,
        timestamp: new Date().toISOString()
      });

      observer.disconnect();
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
}

// Main initialization
console.log("🚀 AI Chat Extractor loaded for:", window.location.hostname);

if (window.location.hostname.includes("chatgpt.com") || window.location.hostname.includes("chat.openai.com")) {
    console.log("🧠 ChatGPT script running...");
    initChatGPTExtractor();
}

if (window.location.hostname.includes("perplexity.ai")) {
    console.log("🧠 Perplexity script running...");
    initPerplexityExtractor();
}
