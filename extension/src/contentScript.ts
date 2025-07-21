import { initChatGPTExtractor } from './agents/chatgptExtractor';
import { initPerplexityExtractor } from './agents/perplexityExtractor';

console.log("🚀 AI Chat Extractor loaded for:", window.location.hostname);

if (window.location.hostname.includes("chatgpt.com")) {
  console.log("🧠 ChatGPT script running...");
  initChatGPTExtractor();
}

if (window.location.hostname.includes("perplexity.ai")) {
  console.log("🧠 Perplexity script running...");
  initPerplexityExtractor();
}
