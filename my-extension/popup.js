document.addEventListener("DOMContentLoaded", () => {
  const generateBtn = document.getElementById("generate-btn");
  const levelSelect = document.getElementById("level-select");
  const typeSelect = document.getElementById("type-select");
  const statusDiv = document.getElementById("status");

  generateBtn.addEventListener("click", async () => {
    const level = levelSelect.value;
    const type = typeSelect.value;

    statusDiv.textContent = "Generating...";

    try {
      // Send message or call background/content script to start generation
      // Example sending message to content script or background:
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.tabs.sendMessage(
          tabs[0].id,
          { action: "generate", level, type },
          (response) => {
            if (chrome.runtime.lastError) {
              statusDiv.textContent = `Error: ${chrome.runtime.lastError.message}`;
              return;
            }
            statusDiv.textContent = response?.status || "Generation complete!";
          }
        );
      });
    } catch (err) {
      statusDiv.textContent = "Error: " + err.message;
    }
  });
});
