// Background service worker — keeps extension alive
chrome.runtime.onInstalled.addListener(() => {
  console.log("Intentra extension installed.");
});