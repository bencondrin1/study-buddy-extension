chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message && message.type === 'pdfUrl') {
    console.log("✅ PDF URL received in background:", message.pdfUrl);

    fetch('http://127.0.0.1:5050/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pdf_urls: [message.pdfUrl],
        level: message.level || 'Intermediate',
        output_type: message.output_type || 'Study Guide'
      })
    })
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        return res.json();
      })
      .then(data => {
        console.log('✅ Backend response:', data);
        sendResponse({ success: true, data });
      })
      .catch(err => {
        console.error('❌ Backend fetch failed:', err);
        sendResponse({ success: false, error: err.message });
      });

    return true; // Keep message channel open for async response
  }
});
