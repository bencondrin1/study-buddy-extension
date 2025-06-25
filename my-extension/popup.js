document.addEventListener('DOMContentLoaded', () => {
  const generateBtn = document.getElementById('generate-btn');
  const statusDiv = document.getElementById('status');
  const levelSelect = document.getElementById('level-select');
  const typeSelect = document.getElementById('type-select');

  generateBtn.addEventListener('click', async () => {
    statusDiv.textContent = '⏳ Fetching selected PDF...';

    try {
      // Get active tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab) {
        statusDiv.textContent = '❌ No active tab found.';
        return;
      }

      // Ask content script for base64 PDF of the selected item
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
              const errorData = await res.json().catch(() => ({}));
              statusDiv.textContent = `❌ Backend error: ${errorData.error || res.statusText}`;
              return;
            }

            // Receive PDF blob and open it in a new tab
            const blob = await res.blob();
            const pdfUrl = URL.createObjectURL(blob);
            window.open(pdfUrl, '_blank');

            statusDiv.textContent = '✅ Study materials generated and opened!';

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