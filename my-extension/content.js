console.log("Content script loaded!");
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "extractPdfUrl") {
    // Find all selected rows (those with aria-selected="true")
    const selectedRows = Array.from(document.querySelectorAll('tr[aria-selected="true"]'));
    
    if (selectedRows.length === 0) {
      sendResponse({ error: "No PDF files selected. Please click on PDF files to select them." });
      return true;
    }
    
    // Extract PDF links from each selected row
    const urls = selectedRows.map(row => {
      const link = row.querySelector('a[href$=".pdf"]');
      return link ? link.href : null;
    }).filter(Boolean);
    
    if (urls.length === 0) {
      sendResponse({ error: "No PDF links found in selected rows." });
      return true;
    }
    
    sendResponse({ pdfUrls: urls });
    return true;
  }

  // Unknown message type fallback
  sendResponse({ error: "Unknown message type." });
  return true;
});
