document.addEventListener("DOMContentLoaded", () => {
  const generateBtn = document.getElementById("generate-btn");
  const typeSelect = document.getElementById("type-select");
  const levelSelect = document.getElementById("level-select");
  const fileTypeSelect = document.getElementById("filetype-select");
  const statusDiv = document.getElementById("status");

  generateBtn.addEventListener("click", async () => {
    try {
      statusDiv.textContent = "📄 Extracting PDF content...";

      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const [response] = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: extractSelectedPdfBase64,
      });

      const pdfBase64 = response.result;
      if (!pdfBase64) {
        statusDiv.textContent = "⚠️ Failed to extract PDF data.";
        return;
      }

      const isFlashcards = typeSelect.value === "Flashcards";
      const endpoint = isFlashcards
        ? "http://localhost:5050/generate_flashcards"
        : "http://localhost:5050/generate_blob";

      const payload = {
        pdf_base64: pdfBase64,
        level: levelSelect.value,
      };

      if (isFlashcards) {
        payload.file_type = fileTypeSelect.value;
      } else {
        payload.output_type = typeSelect.value;
      }

      statusDiv.textContent = "⚙️ Generating study materials...";

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;

      const extension = isFlashcards
        ? (fileTypeSelect.value === "apkg" ? "apkg" : "csv")
        : "pdf";

      link.download = `study_output.${extension}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);

      statusDiv.textContent = "✅ Download complete!";
    } catch (error) {
      console.error("❌ Error:", error);
      statusDiv.textContent = `❌ Error: ${error.message}`;
    }
  });
});

function extractSelectedPdfBase64() {
  const selected = document.querySelector(".ef-item-row.ef-item-selected a");
  if (!selected) return null;

  return fetch(selected.href)
    .then(res => res.blob())
    .then(blob => {
      return new Promise(resolve => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64 = reader.result.split(",")[1]; // remove "data:application/pdf;base64,"
          resolve(base64);
        };
        reader.readAsDataURL(blob);
      });
    });
}
