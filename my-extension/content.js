chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "extractPdfUrl") {
    // Look for selected rows on Canvas file pages
    const selectedRows = Array.from(document.querySelectorAll("tr[aria-selected='true']"));
    if (selectedRows.length === 0) {
      sendResponse({ error: "No PDF selected on Canvas." });
      return true;
    }
    const urls = selectedRows.map(row => {
      const link = row.querySelector("a[href$='.pdf']");
      return link ? link.href : null;
    }).filter(Boolean);
    if (urls.length === 0) {
      sendResponse({ error: "No PDF links found in selected rows." });
      return true;
    }
    sendResponse({ pdfUrls: urls });
    return true;
  }
});
