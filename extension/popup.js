const BACKEND_URL = "https://intentra-3406.onrender.com";
let currentTab = "login";

const app = document.getElementById("app");

// ── Storage helpers ─────────────────────────────
function getToken() {
  return new Promise(resolve => {
    chrome.storage.local.get("intentra_token", data => {
      resolve(data.intentra_token || null);
    });
  });
}

function saveToken(token) {
  chrome.storage.local.set({ intentra_token: token });
}

function clearToken() {
  chrome.storage.local.remove("intentra_token");
}

// ── Boot ────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
  const token = await getToken();
  if (token) showSaveScreen(token);
  else showAuthScreen();
});

// ── Auth Screen ─────────────────────────────────
function showAuthScreen() {
  app.innerHTML = `
    <div class="logo">Intentra</div>
    <div class="tabs">
      <button class="tab active" id="tabLogin">Login</button>
      <button class="tab" id="tabRegister">Register</button>
    </div>
    <div id="fields"></div>
    <div class="status error" id="authErr"></div>
  `;

  renderFields();

  document.getElementById("tabLogin").onclick = () => {
    currentTab = "login";
    document.getElementById("tabLogin").classList.add("active");
    document.getElementById("tabRegister").classList.remove("active");
    renderFields();
  };

  document.getElementById("tabRegister").onclick = () => {
    currentTab = "register";
    document.getElementById("tabRegister").classList.add("active");
    document.getElementById("tabLogin").classList.remove("active");
    renderFields();
  };
}

function renderFields() {
  const container = document.getElementById("fields");

  if (currentTab === "register") {
    container.innerHTML = `
      <input class="field" id="nameInput" placeholder="Name" />
      <input class="field" id="emailInput" placeholder="Email" />
      <input class="field" id="passInput" type="password" placeholder="Password" />
      <button class="submit" id="submitBtn">Create Account</button>
    `;
  } else {
    container.innerHTML = `
      <input class="field" id="emailInput" placeholder="Email" />
      <input class="field" id="passInput" type="password" placeholder="Password" />
      <button class="submit" id="submitBtn">Login</button>
    `;
  }

  document.getElementById("submitBtn").onclick = handleAuth;
}

async function handleAuth() {
  const email = document.getElementById("emailInput")?.value?.trim();
  const password = document.getElementById("passInput")?.value;
  const name = document.getElementById("nameInput")?.value?.trim();
  const errEl = document.getElementById("authErr");

  if (!email || !password) {
    errEl.textContent = "Fill all fields.";
    return;
  }

  const endpoint = currentTab === "login" ? "/auth/login" : "/auth/register";
  const body = currentTab === "login"
    ? { email, password }
    : { email, password, name: name || email.split("@")[0] };

  try {
    const res = await fetch(BACKEND_URL + endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail);

    saveToken(data.access_token);
    showSaveScreen(data.access_token);

  } catch (err) {
    errEl.textContent = err.message || "Auth failed.";
  }
}

// ── Save Screen ─────────────────────────────────
async function showSaveScreen(token) {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  app.innerHTML = `
    <div class="logo">Intentra</div>
    <button class="logout" id="logoutBtn">Logout</button>
    <div class="page-title">${tab.title || tab.url}</div>
    <textarea id="selectedText" placeholder="Optional note..."></textarea>
    <button class="btn-save" id="saveBtn">Save</button>
    <div class="status" id="status"></div>
  `;

  document.getElementById("logoutBtn").onclick = () => {
    clearToken();
    showAuthScreen();
  };

  chrome.storage.local.get("selectedText", data => {
    if (data.selectedText) {
      document.getElementById("selectedText").value = data.selectedText;
      chrome.storage.local.remove("selectedText");
    }
  });

  document.getElementById("saveBtn").onclick = () => {
    doSave(tab.url, tab.title, token);
  };
}

// ── Save Logic ──────────────────────────────────
async function doSave(url, title, token) {
  const statusEl = document.getElementById("status");
  statusEl.textContent = "Saving...";
  statusEl.className = "status loading";

  try {
    const res = await fetch(`${BACKEND_URL}/saves/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        url,
        title,
        selected_text: document.getElementById("selectedText").value || null
      })
    });

    if (res.status === 401) {
      clearToken();
      showAuthScreen();
      return;
    }

    if (!res.ok) throw new Error("Server error");

    const data = await res.json();
    statusEl.textContent = `Saved as "${data.intent}"`;
    statusEl.className = "status success";

  } catch (err) {
    statusEl.textContent = "Failed to connect.";
    statusEl.className = "status error";
  }
}

// const BACKEND_URL = "https://intentra-3406.onrender.com";

// let currentTab = 'login';

// // ── Storage helpers ──────────────────────────────────
// async function getToken() {
//   return new Promise(resolve => {
//     chrome.storage.local.get("intentra_token", data => {
//       resolve(data.intentra_token || null);
//     });
//   });
// }

// function saveToken(token) {
//   chrome.storage.local.set({ intentra_token: token });
// }

// function clearToken() {
//   chrome.storage.local.remove("intentra_token");
// }

// // ── Boot ─────────────────────────────────────────────
// document.addEventListener("DOMContentLoaded", async () => {
//   const token = await getToken();
//   if (token) {
//     showSaveScreen(token);
//   } else {
//     showAuthScreen();
//   }
// });

// // ── Auth screen ──────────────────────────────────────
// function showAuthScreen() {
//   document.body.innerHTML = `
//     <style>
//       * { margin:0; padding:0; box-sizing:border-box; }
//       body {
//         width:320px;
//         font-family:-apple-system,BlinkMacSystemFont,sans-serif;
//         background:#080808; color:#f0ece4; padding:24px;
//       }
//       .logo { font-size:20px; font-weight:700; color:#e8d5a3; margin-bottom:4px; }
//       .sub { font-size:11px; color:#555; margin-bottom:24px; }
//       .tabs {
//         display:flex; margin-bottom:20px;
//         border:1px solid #222; border-radius:8px; overflow:hidden;
//       }
//       .tab {
//         flex:1; padding:9px; background:none; border:none;
//         color:#666; font-size:12px; cursor:pointer;
//       }
//       .tab.active { background:#1a1a1a; color:#e8d5a3; }
//       .field {
//         width:100%; background:#111; border:1px solid #222; border-radius:7px;
//         color:#f0ece4; font-size:13px; padding:9px 12px; outline:none;
//         margin-bottom:10px; font-family:inherit; display:block;
//       }
//       .field:focus { border-color:#444; }
//       .field::placeholder { color:#444; }
//       .submit {
//         width:100%; padding:10px; background:#e8d5a3; color:#080808;
//         border:none; border-radius:7px; font-size:13px; font-weight:600;
//         cursor:pointer; margin-top:2px;
//       }
//       .err { color:#e05252; font-size:11px; margin-top:10px; text-align:center; min-height:14px; }
//     </style>
//     <div class="logo">Intentra</div>
//     <div class="sub">Your AI intent engine</div>
//     <div class="tabs">
//       <button class="tab active" id="tabLogin">Login</button>
//       <button class="tab" id="tabRegister">Register</button>
//     </div>
//     <div id="authFields"></div>
//     <div class="err" id="authErr"></div>
//   `;

//   renderFields();

//   document.getElementById('tabLogin').addEventListener('click', () => {
//     currentTab = 'login';
//     document.getElementById('tabLogin').classList.add('active');
//     document.getElementById('tabRegister').classList.remove('active');
//     renderFields();
//   });

//   document.getElementById('tabRegister').addEventListener('click', () => {
//     currentTab = 'register';
//     document.getElementById('tabRegister').classList.add('active');
//     document.getElementById('tabLogin').classList.remove('active');
//     renderFields();
//   });
// }

// function renderFields() {
//   const container = document.getElementById('authFields');
//   if (!container) return;

//   if (currentTab === 'register') {
//     container.innerHTML = `
//       <input class="field" id="nameInput" type="text" placeholder="Your name" />
//       <input class="field" id="emailInput" type="email" placeholder="Email" />
//       <input class="field" id="passInput" type="password" placeholder="Password" />
//       <button class="submit" id="submitBtn">Create Account</button>
//     `;
//   } else {
//     container.innerHTML = `
//       <input class="field" id="emailInput" type="email" placeholder="Email" />
//       <input class="field" id="passInput" type="password" placeholder="Password" />
//       <button class="submit" id="submitBtn">Login</button>
//     `;
//   }

//   document.getElementById('submitBtn').addEventListener('click', handleAuth);

//   // Allow pressing Enter to submit
//   container.querySelectorAll('input').forEach(input => {
//     input.addEventListener('keydown', e => {
//       if (e.key === 'Enter') handleAuth();
//     });
//   });
// }

// async function handleAuth() {
//   const email = document.getElementById('emailInput')?.value?.trim();
//   const password = document.getElementById('passInput')?.value;
//   const name = document.getElementById('nameInput')?.value?.trim();
//   const errEl = document.getElementById('authErr');

//   if (!email || !password) {
//     errEl.textContent = 'Please fill in all fields.';
//     return;
//   }

//   const btn = document.getElementById('submitBtn');
//   btn.disabled = true;
//   btn.textContent = 'Please wait...';
//   errEl.textContent = '';

//   const endpoint = currentTab === 'login' ? '/auth/login' : '/auth/register';
//   const body = currentTab === 'login'
//     ? { email, password }
//     : { email, password, name: name || email.split('@')[0] };

//   try {
//     const res = await fetch(BACKEND_URL + endpoint, {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify(body)
//     });

//     const data = await res.json();

//     if (!res.ok) {
//       errEl.textContent = data.detail || 'Something went wrong.';
//       btn.disabled = false;
//       btn.textContent = currentTab === 'login' ? 'Login' : 'Create Account';
//       return;
//     }

//     saveToken(data.access_token);
//     showSaveScreen(data.access_token);

//   } catch (e) {
//     errEl.textContent = 'Cannot reach backend. Is it running?';
//     btn.disabled = false;
//     btn.textContent = currentTab === 'login' ? 'Login' : 'Create Account';
//   }
// }

// // ── Save screen ──────────────────────────────────────
// async function showSaveScreen(token) {
//   const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

//   document.body.innerHTML = `
//     <style>
//       * { margin:0; padding:0; box-sizing:border-box; }
//       body {
//         width:340px;
//         font-family:-apple-system,BlinkMacSystemFont,sans-serif;
//         background:#080808; color:#f0ece4; padding:20px;
//       }
//       .header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
//       .logo { font-size:16px; font-weight:700; color:#e8d5a3; }
//       .logout {
//         font-size:10px; background:none; border:1px solid #222;
//         color:#666; padding:3px 8px; border-radius:4px; cursor:pointer;
//       }
//       .logout:hover { color:#f0ece4; border-color:#444; }
//       .page-title {
//         font-size:12px; color:#777; background:#111; border:1px solid #1e1e1e;
//         border-radius:7px; padding:9px 12px; margin-bottom:10px;
//         white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
//       }
//       textarea {
//         width:100%; height:70px; background:#111; border:1px solid #1e1e1e;
//         border-radius:7px; color:#f0ece4; font-size:12px; padding:9px 12px;
//         resize:none; outline:none; font-family:inherit; margin-bottom:10px;
//         display:block;
//       }
//       textarea:focus { border-color:#333; }
//       textarea::placeholder { color:#444; }
//       .btn-row { display:flex; gap:8px; }
//       .btn-save {
//         flex:1; padding:10px; background:#e8d5a3; color:#080808;
//         border:none; border-radius:7px; font-size:12px; font-weight:600; cursor:pointer;
//       }
//       .btn-save:disabled { background:#333; color:#666; cursor:not-allowed; }
//       .btn-screenshot {
//         padding:10px 14px; background:none; border:1px solid #222;
//         color:#888; border-radius:7px; font-size:14px; cursor:pointer;
//       }
//       .btn-screenshot:hover { border-color:#444; color:#f0ece4; }
//       #screenshotPreview {
//         width:100%; border-radius:6px; margin-bottom:10px;
//         border:1px solid #222; display:none;
//       }
//       input[type=file] { display:none; }
//       .status { margin-top:10px; font-size:11px; text-align:center; min-height:16px; }
//       .success { color:#52c97a; }
//       .error { color:#e05252; }
//       .loading { color:#e8d5a3; }
//     </style>

//     <div class="header">
//       <div class="logo">Intentra</div>
//       <button class="logout" id="logoutBtn">logout</button>
//     </div>

//     <div class="page-title">${escapeHtml(tab.title || tab.url || 'Unknown page')}</div>

//     <img id="screenshotPreview" alt="preview" />
//     <input type="file" id="screenshotFile" accept="image/*" />

//     <textarea id="selectedText" placeholder="Add a note or paste selected text (optional)..."></textarea>

//     <div class="btn-row">
//       <button class="btn-save" id="saveBtn">Save with Intent</button>
//       <button class="btn-screenshot" id="screenshotBtn" title="Upload screenshot">📷</button>
//     </div>

//     <div class="status" id="status"></div>
//   `;

//   // Event listeners — no inline onclick
//   document.getElementById('logoutBtn').addEventListener('click', () => {
//     clearToken();
//     showAuthScreen();
//   });

//   document.getElementById('screenshotBtn').addEventListener('click', () => {
//     document.getElementById('screenshotFile').click();
//   });

//   document.getElementById('screenshotFile').addEventListener('change', () => {
//     const file = document.getElementById('screenshotFile').files[0];
//     if (!file) return;
//     const reader = new FileReader();
//     reader.onload = e => {
//       const img = document.getElementById('screenshotPreview');
//       img.src = e.target.result;
//       img.style.display = 'block';
//     };
//     reader.readAsDataURL(file);
//   });

//   document.getElementById('saveBtn').addEventListener('click', () => {
//     doSave(tab.url, tab.title || '', token);
//   });

//   // Pre-fill selected text
//   chrome.storage.session.get("selectedText", (data) => {
//     if (data.selectedText) {
//       document.getElementById("selectedText").value = data.selectedText;
//       chrome.storage.session.remove("selectedText");
//     }
//   });
// }

// // ── Do save ──────────────────────────────────────────
// async function doSave(url, title, token) {
//   const btn = document.getElementById('saveBtn');
//   const statusEl = document.getElementById('status');
//   const screenshotFile = document.getElementById('screenshotFile')?.files[0];

//   btn.disabled = true;
//   btn.textContent = 'Saving...';
//   statusEl.className = 'status loading';
//   statusEl.textContent = 'Gemini is analyzing intent...';

//   try {
//     let res;

//     if (screenshotFile) {
//       const formData = new FormData();
//       formData.append('file', screenshotFile);
//       formData.append('url', url);
//       formData.append('title', title || 'Screenshot');

//       res = await fetch(`${BACKEND_URL}/saves/screenshot`, {
//         method: 'POST',
//         headers: { 'Authorization': `Bearer ${token}` },
//         body: formData
//       });
//     } else {
//       res = await fetch(`${BACKEND_URL}/saves/`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//           'Authorization': `Bearer ${token}`
//         },
//         body: JSON.stringify({
//           url,
//           title,
//           selected_text: document.getElementById('selectedText')?.value || null
//         })
//       });
//     }

//     if (res.status === 401) {
//       clearToken();
//       showAuthScreen();
//       return;
//     }

//     if (!res.ok) throw new Error('Server error');

//     const data = await res.json();
//     statusEl.className = 'status success';
//     statusEl.textContent = `✓ "${data.intent}" intent — ${data.suggested_action}`;
//     btn.textContent = 'Saved!';
//     setTimeout(() => window.close(), 2500);

//   } catch (e) {
//     statusEl.className = 'status error';
//     statusEl.textContent = '❌ Could not connect to backend.';
//     btn.disabled = false;
//     btn.textContent = 'Save with Intent';
//   }
// }

// // ── Escape HTML helper ───────────────────────────────
// function escapeHtml(str) {
//   return str
//     .replace(/&/g, '&amp;')
//     .replace(/</g, '&lt;')
//     .replace(/>/g, '&gt;')
//     .replace(/"/g, '&quot;')
//     .replace(/'/g, '&#039;');
// }

// // const BACKEND_URL = "http://localhost:8000";

// // // Load current tab info when popup opens
// // document.addEventListener("DOMContentLoaded", async () => {
// //   const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

// //   document.getElementById("pageTitle").textContent =
// //     tab.title || tab.url || "Unknown page";

// //   // Pre-fill with any text the user had selected on the page
// //   chrome.storage.session.get("selectedText", (data) => {
// //     if (data.selectedText) {
// //       document.getElementById("selectedText").value = data.selectedText;
// //       chrome.storage.session.remove("selectedText");
// //     }
// //   });

// //   // Save button handler
// //   document.getElementById("saveBtn").addEventListener("click", async () => {
// //     const btn = document.getElementById("saveBtn");
// //     const status = document.getElementById("status");

// //     btn.disabled = true;
// //     btn.textContent = "Saving...";
// //     status.className = "status loading";
// //     status.textContent = "Analyzing intent...";

// //     try {
// //       const response = await fetch(`${BACKEND_URL}/saves/`, {
// //         method: "POST",
// //         headers: { "Content-Type": "application/json" },
// //         body: JSON.stringify({
// //           url: tab.url,
// //           title: tab.title,
// //           selected_text: document.getElementById("selectedText").value || null,
// //         }),
// //       });

// //       if (!response.ok) throw new Error("Server error");

// //       const data = await response.json();

// //       status.className = "status success";
// //       status.textContent =
// //         `✓ Saved as "${data.intent}" intent — ${data.suggested_action}`;

// //       btn.textContent = "Saved!";

// //       // Close popup after 2.5 seconds
// //       setTimeout(() => window.close(), 2500);

// //     } catch (err) {
// //       status.className = "status error";
// //       status.textContent = "❌ Could not connect to Intentra backend.";
// //       btn.disabled = false;
// //       btn.textContent = "Save with Intent";
// //     }
// //   });
// // });