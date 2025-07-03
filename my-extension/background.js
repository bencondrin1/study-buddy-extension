chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === 'pdfUrl') {
    console.log("✅ Received PDF URL:", message.pdfUrl);

    fetch('http://127.0.0.1:5050/generate_blob', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pdf_urls: [message.pdfUrl],
        level: message.level || 'Basic',
        output_type: message.output_type || 'Study Guide'
      })
    })
    .then(response => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then(data => {
      console.log("✅ Backend success:", data);
      sendResponse({ success: true, data });
    })
    .catch(err => {
      console.error("❌ Backend error:", err);
      sendResponse({ success: false, error: err.message });
    });

    return true;
  }
});
