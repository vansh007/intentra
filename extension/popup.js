const BACKEND_URL = "http://localhost:8000";

// Load current tab info when popup opens
document.addEventListener("DOMContentLoaded", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  document.getElementById("pageTitle").textContent =
    tab.title || tab.url || "Unknown page";

  // Pre-fill with any text the user had selected on the page
  chrome.storage.session.get("selectedText", (data) => {
    if (data.selectedText) {
      document.getElementById("selectedText").value = data.selectedText;
      chrome.storage.session.remove("selectedText");
    }
  });

  // Save button handler
  document.getElementById("saveBtn").addEventListener("click", async () => {
    const btn = document.getElementById("saveBtn");
    const status = document.getElementById("status");

    btn.disabled = true;
    btn.textContent = "Saving...";
    status.className = "status loading";
    status.textContent = "Analyzing intent...";

    try {
      const response = await fetch(`${BACKEND_URL}/saves/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: tab.url,
          title: tab.title,
          selected_text: document.getElementById("selectedText").value || null,
        }),
      });

      if (!response.ok) throw new Error("Server error");

      const data = await response.json();

      status.className = "status success";
      status.textContent =
        `✓ Saved as "${data.intent}" intent — ${data.suggested_action}`;

      btn.textContent = "Saved!";

      // Close popup after 2.5 seconds
      setTimeout(() => window.close(), 2500);

    } catch (err) {
      status.className = "status error";
      status.textContent = "❌ Could not connect to Intentra backend.";
      btn.disabled = false;
      btn.textContent = "Save with Intent";
    }
  });
});