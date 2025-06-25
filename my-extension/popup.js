document.addEventListener('DOMContentLoaded', () => {
  const generateBtn = document.getElementById('generate-btn');
  const statusDiv = document.getElementById('status');
  const levelSelect = document.getElementById('level-select');
  const typeSelect = document.getElementById('type-select');

  generateBtn.addEventListener('click', async () => {
    statusDiv.textContent = '⏳ Fetching selected PDF...';

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab) {
        statusDiv.textContent = '❌ No active tab found.';
        return;
      }

      chrome.tabs.sendMessage(
        tab.id,
        { action: 'getSelectedPdfBase64' },
        async (response) => {
          if (chrome.runtime.lastError) {
            statusDiv.textContent = `❌ Message send error: ${chrome.runtime.lastError.message}`;
            return;
          }

          if (!response || response.error) {
            statusDiv.textContent = `❌ ${response?.error || 'Unknown error getting PDF base64'}`;
            return;
          }

          const { pdfBase64 } = response;
          statusDiv.textContent = '📤 Sending PDF to backend for processing...';

          const payload = {
            pdf_base64: pdfBase64,
            level: levelSelect.value,
            output_type: typeSelect.value
          };

          try {
            const res = await fetch('http://localhost:5050/generate_blob', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(payload)
            });

            if (!res.ok) {
              const errorText = await res.text();
              statusDiv.textContent = `❌ Backend error: ${errorText || res.statusText}`;
              return;
            }

            const pdfBlob = await res.blob();
            const pdfUrl = URL.createObjectURL(pdfBlob);
            window.open(pdfUrl);
            statusDiv.textContent = '✅ Study materials generated successfully!';
          } catch (backendErr) {
            statusDiv.textContent = `❌ Backend request failed: ${backendErr.message}`;
          }
        }
      );
    } catch (err) {
      statusDiv.textContent = `❌ Unexpected error: ${err.message}`;
    }
  });
});
