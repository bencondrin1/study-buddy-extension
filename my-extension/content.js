chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getSelectedPdfBase64') {
    (async () => {
      try {
        const selectedElement = document.querySelector('.ef-item-row.ef-item-selected a.ef-name-col__link');
        if (!selectedElement) {
          sendResponse({ error: 'No selected PDF link found. Please highlight a PDF box.' });
          return;
        }

        const pdfUrl = selectedElement.href;
        const response = await fetch(pdfUrl);
        if (!response.ok) {
          sendResponse({ error: `Failed to fetch PDF: ${response.statusText}` });
          return;
        }

        const blob = await response.blob();

        const reader = new FileReader();
        reader.onloadend = () => {
          const base64data = reader.result.split(',')[1]; // strip data:*/*;base64,
          sendResponse({ pdfBase64: base64data });
        };
        reader.readAsDataURL(blob);

      } catch (error) {
        sendResponse({ error: error.message });
      }
    })();

    return true; // Indicates async response
  }
});
