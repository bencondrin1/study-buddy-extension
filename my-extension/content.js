chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getSelectedPdfBase64') {
    (async () => {
      try {
        const anchor = document.querySelector('.ef-item-row.ef-item-selected a.ef-name-col__link');
        if (!anchor) {
          return sendResponse({ error: "Please select a PDF box." });
        }

        const response = await fetch(anchor.href);
        if (!response.ok) {
          return sendResponse({ error: `Failed to fetch PDF (${response.status})` });
        }

        const blob = await response.blob();
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64 = reader.result.split(',')[1]; // strip data URI
          sendResponse({ pdfBase64: base64 });
        };
        reader.readAsDataURL(blob);
      } catch (err) {
        sendResponse({ error: err.message });
      }
    })();

    return true;
  }
});
