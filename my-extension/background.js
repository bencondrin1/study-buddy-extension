chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'pdfUrl') {
    console.log("✅ PDF URL sent to backend:", message.pdfUrl);

    fetch('http://127.0.0.1:5000/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        level: message.level,
        output_type: message.output_type,
        pdf_urls: [message.pdfUrl]
      })
    })
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        return res.json();
      })
      .then(data => {
        console.log('✅ Backend response:', data);
      })
      .catch(err => {
        console.error('❌ Backend fetch failed:', err);
      });
  }
});
