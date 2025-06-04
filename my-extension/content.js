chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "extractPdfUrl") {
    // 1. Grab all <div class="ef-item-row"> elements where aria-selected="true"
    const selectedRows = Array.from(
      document.querySelectorAll("div.ef-item-row[aria-selected='true']")
    );

    if (selectedRows.length === 0) {
      sendResponse({ error: "No PDF selected on Canvas." });
      return true;
    }

    // 2. From each selected <div>, pull out the <a> whose href ends in ".pdf"
    const urls = selectedRows
      .map(row => {
        const link = row.querySelector("a[href$='.pdf']");
        return link ? link.href : null;
      })
      .filter(Boolean);

    if (urls.length === 0) {
      sendResponse({ error: "No PDF links found in selected rows." });
      return true;
    }

    // 3. Return the array of URLs
    sendResponse({ pdfUrls: urls });
    return true;
  }
});
