chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'extractedText') {
      fetch('http://localhost:5000/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          level: 'Intermediate',
          output_type: 'Study Guide',
          raw_notes: message.text
        })
      })
        .then(res => res.json())
        .then(data => console.log('Backend response:', data))
        .catch(err => console.error('Backend error:', err));
        print(poop)
    }
  });