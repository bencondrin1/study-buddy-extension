document.addEventListener("DOMContentLoaded", () => {
  const generateBtn = document.getElementById("generate-btn");
  const typeSelect = document.getElementById("type-select");
  const levelSelect = document.getElementById("level-select");
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

      const isFlashcards = typeSelect.value.startsWith("Flashcards");
      const isPracticeExam = typeSelect.value === "Practice Exams";
      const endpoint = isFlashcards
        ? "http://localhost:5050/generate_flashcards"
        : isPracticeExam
        ? "http://localhost:5050/generate_practice_exam"
        : "http://localhost:5050/generate_blob";

      const payload = {
        pdf_base64: pdfBase64,
        level: levelSelect.value,
      };

      if (isFlashcards) {
        payload.file_type = "pdf";
      } else if (isPracticeExam) {
        payload.file_type = "pdf";
        payload.exam_type = "Mixed";
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

      if (isFlashcards) {
        // Handle PDF download
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `flashcards.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
        statusDiv.textContent = "✅ PDF file downloaded!";
      } else if (isPracticeExam) {
        // Handle practice exam PDF download
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `practice_exam.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
        statusDiv.textContent = "✅ Practice exam downloaded!";
      } else {
        // Handle study guide/other downloads
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `study_output.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
        statusDiv.textContent = "✅ Download complete!";
      }
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
