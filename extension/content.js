// Listen for selected text and store it for the popup
document.addEventListener("mouseup", () => {
  const selected = window.getSelection().toString().trim();
  if (selected.length > 0) {
    chrome.storage.session.set({ selectedText: selected });
  }
});