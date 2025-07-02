document.addEventListener('DOMContentLoaded', () => {
  const generateBtn = document.getElementById('generate-btn');
  const statusDiv = document.getElementById('status');
  const levelSelect = document.getElementById('level-select');
  const typeSelect = document.getElementById('type-select');
  const filetypeSelect = document.getElementById('filetype-select');
  const flashcardOptions = document.getElementById('flashcard-options');

  // Toggle flashcard file type dropdown
  typeSelect.addEventListener('change', () => {
    flashcardOptions.style.display = typeSelect.value === 'Flashcards' ? 'block' : 'none';
  });

  generateBtn.addEventListener('click', async () => {
    statusDiv.textContent = '📄 Fetching selected PDF...';

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab) {
        statusDiv.textContent = '❌ No active tab found.';
        return;
      }

      chrome.tabs.sendMessage(tab.id, { action: 'getSelectedPdfBase64' }, async (response) => {
        if (chrome.runtime.lastError) {
          statusDiv.textContent = `❌ Chrome error: ${chrome.runtime.lastError.message}`;
          return;
        }

        if (!response || response.error) {
          statusDiv.textContent = `❌ ${response?.error || 'Unknown error'}`;
          return;
        }

        const payload = {
          pdf_base64: response.pdfBase64,
          level: levelSelect.value,
          output_type: typeSelect.value,
          file_type: filetypeSelect?.value || 'csv'
        };

        const endpoint = typeSelect.value === 'Flashcards'
          ? 'http://localhost:5050/generate_flashcards'
          : 'http://localhost:5050/generate_blob';

        statusDiv.textContent = '⚙️ Generating study materials...';

        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          const errText = await res.text();
          statusDiv.textContent = `❌ Backend error: ${errText}`;
          return;
        }

        const blob = await res.blob();
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = typeSelect.value === 'Flashcards'
          ? (payload.file_type === 'apkg' ? 'flashcards.apkg' : 'flashcards.csv')
          : 'study_materials.pdf';
        a.click();

        statusDiv.textContent = '✅ Download ready!';
      });
    } catch (err) {
      statusDiv.textContent = `❌ Unexpected error: ${err.message}`;
    }
  });
});
