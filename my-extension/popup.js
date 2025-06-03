document.addEventListener("DOMContentLoaded", () => {
  const submitBtn = document.getElementById("submitBtn");

  submitBtn.addEventListener("click", async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

      // Ask content script for selected PDF URLs
      chrome.tabs.sendMessage(tab.id, { type: "extractPdfUrl" }, async (response) => {
        if (chrome.runtime.lastError) {
          alert("Error communicating with content script. Make sure to reload the Canvas page after installing/updating the extension.");
          return;
        }

        if (response?.error) {
          alert(response.error);
          return;
        }

        const level = document.getElementById("level").value;
        const output = document.getElementById("tool").value;

        // Send the PDF URLs to your backend
        const res = await fetch("http://localhost:5000/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            pdf_urls: response.pdfUrls,
            level: level,
            output_type: output,
          }),
        });

        if (!res.ok) throw new Error(await res.text());

        const data = await res.json();
        alert(`Success: ${data.message}`);
      });
    } catch (error) {
      alert(`Failed: ${error.message}`);
    }
  });
});
