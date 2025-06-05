chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Content.js loaded"); 
  if (request.type === "extractPdfUrl") {
    // Get all selected rows with class ef-item-row and aria-selected=true
    const selectedRows = Array.from(
      document.querySelectorAll("div.ef-item-row[aria-selected='true']")
    );

    if (selectedRows.length === 0) {
      sendResponse({ error: "No PDF selected on Canvas." });
      return true;
    }

    // Look inside each row for a link that likely points to a PDF
    const urls = selectedRows
      .map(row => {
        const links = Array.from(row.querySelectorAll("a"));
        const pdfLink = links.find(link => {
          const textIsPdf = link.textContent.trim().toLowerCase().endsWith(".pdf");
          const hrefLooksLikePdf = link.href.includes("/download?download_frd=");
          return textIsPdf || hrefLooksLikePdf;
        });
        return pdfLink?.href || null;
      })
      .filter(Boolean);

    if (urls.length === 0) {
      sendResponse({ error: "No PDF links found in selected rows." });
      return true;
    }

    sendResponse({ pdfUrls: urls });
    return true;
  }
});
