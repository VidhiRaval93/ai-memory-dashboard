export function initPerplexityExtractor() {
    console.log("🧠 Perplexity extractor activated");
    const observer = new MutationObserver(() => {
        const thread = document.querySelector('[data-testid="thread"]');
        const questions = Array.from(thread?.querySelectorAll('[data-testid="user-message"]') || []);
        const answers = Array.from(thread?.querySelectorAll('[data-testid="bot-message"]') || []);
        const lastQuestion = questions[questions.length - 1]?.textContent?.trim();
        const lastAnswer = answers[answers.length - 1]?.textContent?.trim();
        if (lastQuestion && lastAnswer) {
            const payload = {
                question: lastQuestion,
                answer: lastAnswer,
                url: window.location.href,
                timestamp: new Date().toISOString(),
            };
            console.log("🟦 [Perplexity] Sending to backend:", payload);
            fetch("http://localhost:8001/save_perplexity", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            }).then(res => {
                if (!res.ok) {
                    console.warn("❌ Perplexity send failed - Status:", res.status, res.statusText);
                }
                else {
                    console.log("✅ Perplexity data sent successfully");
                }
            }).catch(err => {
                console.error("❌ Perplexity send error:", err);
            });
            observer.disconnect();
        }
    });
    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });
}
if (window.location.hostname.includes("perplexity.ai")) {
    initPerplexityExtractor();
}
