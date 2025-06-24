chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'generate') {
    try {
      // Find the selected row
      const selectedRow = document.querySelector('.ef-item-row.ef-item-selected');
      if (!selectedRow) {
        sendResponse({ status: '❌ No selected item found.' });
        return;
      }

      // Find the link to the PDF
      const link = selectedRow.querySelector('a.ef-name-col__link');
      if (!link || !link.href.includes('/download')) {
        sendResponse({ status: '❌ No PDF link found in selected item.' });
        return;
      }

      const pdfUrl = link.href;
      console.log('📄 PDF URL:', pdfUrl);

      chrome.runtime.sendMessage({
        type: 'pdfUrl',
        url: pdfUrl,
        level: request.level,
        output_type: request.type
      });

      sendResponse({ status: '✅ PDF URL sent to backend.' });
    } catch (err) {
      console.error('❌ Error extracting PDF URL:', err);
      sendResponse({ status: '❌ Error extracting PDF URL.' });
    }
  }
});
