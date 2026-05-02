// Aegis Portal Core Intelligence
const BASE_URL = window.location.origin + "/api/v1";
let authToken = localStorage.getItem("aegis_token");

// --- DOM Elements ---
const chatCanvas = document.getElementById("chat-canvas");
const userInput = document.getElementById("user-input");
const btnExecute = document.getElementById("btn-execute");
const loginModal = document.getElementById("login-modal");
const engineStatus = document.getElementById("engine-status");
const authStatus = document.getElementById("auth-status");

// --- Auth Management ---
function checkAuth() {
    if (!authToken) {
        loginModal.classList.remove("hidden");
    } else {
        loginModal.classList.add("hidden");
        authStatus.innerText = "Clearance: Level 4";
        document.getElementById("btn-logout").classList.remove("hidden");
    }
}

async function login() {
    const user = document.getElementById("login-username").value;
    const pass = document.getElementById("login-password").value;
    const errorMsg = document.getElementById("login-error");

    try {
        const response = await fetch(`${BASE_URL}/auth/token`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `username=${user}&password=${pass}`
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem("aegis_token", authToken);
            checkAuth();
        } else {
            errorMsg.classList.remove("hidden");
        }
    } catch (e) {
        console.error("Auth Error", e);
    }
}

function logout() {
    localStorage.removeItem("aegis_token");
    location.reload();
}

// --- Chat & Streaming ---
async function executeQuery() {
    const query = userInput.value.trim();
    if (!query) return;

    userInput.value = "";
    addMessage("user", query);

    const aiMsgId = "ai-" + Date.now();
    addMessage("ai", "", aiMsgId);
    const aiContentEl = document.querySelector(`#${aiMsgId} .content`);
    const aiStatusEl = document.querySelector(`#${aiMsgId} .status-text`);

    try {
        const response = await fetch(`${BASE_URL}/chat`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Authorization": `Bearer ${authToken}`
            },
            body: JSON.stringify({ query: query })
        });

        if (!response.ok) throw new Error("Stream failed");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split("\n");

            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const data = JSON.parse(line.substring(6));
                    handleStreamEvent(data, aiContentEl, aiStatusEl);
                }
            }
        }
    } catch (e) {
        console.error("Stream error", e);
        aiContentEl.innerText = "Aegis has detected an anomaly in the legal grid. Please try again.";
    }
}

function handleStreamEvent(data, contentEl, statusEl) {
    if (data.type === "status") {
        statusEl.innerText = data.content;
        engineStatus.innerText = "Engine: " + data.content;
    } else if (data.type === "token") {
        contentEl.innerHTML = markdownToHtml(contentEl.getAttribute("raw-text") + data.content);
        contentEl.setAttribute("raw-text", contentEl.getAttribute("raw-text") + data.content);
        chatCanvas.scrollTop = chatCanvas.scrollHeight;
    } else if (data.type === "final") {
...
function markdownToHtml(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/^\* (.*$)/gm, '<li>$1</li>')
        .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
        .replace(/\n/g, '<br>');
}
        statusEl.innerText = "Analysis Complete";
        engineStatus.innerText = "Engine: Ready";
        if (data.documents && data.documents.length > 0) {
             addCitations(contentEl.parentElement, data.documents);
        }
    } else if (data.type === "error") {
        contentEl.innerText = data.content;
    }
}

// --- UI Helpers ---
function addMessage(role, content, id = "") {
    const div = document.createElement("div");
    div.id = id;
    div.className = role === "user" ? "self-end max-w-[80%]" : "self-start max-w-[95%] w-full";
    
    if (role === "user") {
        div.innerHTML = `
            <div class="bg-slate-100 border border-slate-200 p-4 rounded-lg">
                <p class="text-slate-800">${content}</p>
            </div>
            <p class="text-[10px] uppercase font-bold text-slate-400 mt-1 text-right">User</p>
        `;
    } else {
        div.innerHTML = `
            <div class="bg-white border border-slate-200 shadow-sm flex flex-col">
                <div class="bg-slate-50 border-b border-slate-100 p-2 flex items-center justify-between">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined text-amber-600 text-[14px]">analytics</span>
                        <span class="status-text text-[10px] uppercase font-bold text-slate-500">Thinking...</span>
                    </div>
                </div>
                <div class="p-4 content text-slate-800 whitespace-pre-wrap" raw-text=""></div>
            </div>
            <p class="text-[10px] uppercase font-bold text-slate-400 mt-1 text-left">Aegis AI</p>
        `;
    }
    chatCanvas.appendChild(div);
    chatCanvas.scrollTop = chatCanvas.scrollHeight;
}

function addCitations(parent, docs) {
    const div = document.createElement("div");
    div.className = "p-4 border-t border-slate-50 flex gap-2 flex-wrap";
    docs.forEach(doc => {
        div.innerHTML += `<span class="bg-slate-50 border border-slate-200 px-2 py-1 text-[10px] font-mono text-slate-600 rounded">Source: Document Vault</span>`;
    });
    parent.appendChild(div);
}

// --- Document Vault Logic ---
async function loadDocuments() {
    const docListEl = document.getElementById("document-list");
    try {
        const response = await fetch(`${BASE_URL}/documents`, {
            headers: { "Authorization": `Bearer ${authToken}` }
        });
        const docs = await response.json();
        
        docListEl.innerHTML = "";
        docs.forEach(doc => {
            const div = document.createElement("div");
            div.className = "p-sm border border-slate-200 bg-white flex items-center gap-sm relative border-l-2 border-l-amber-600";
            div.innerHTML = `
                <span class="material-symbols-outlined text-amber-600">description</span>
                <div class="flex-grow min-w-0">
                    <p class="text-xs font-bold text-slate-700 truncate">${doc.filename}</p>
                    <p class="text-[10px] text-slate-400 uppercase">${doc.status} • ${doc.size}</p>
                </div>
            `;
            docListEl.appendChild(div);
        });
    } catch (e) {
        console.error("Failed to load documents", e);
    }
}

async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
        engineStatus.innerText = "Engine: Uploading...";
        const response = await fetch(`${BASE_URL}/upload`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${authToken}` },
            body: formData
        });

        if (response.ok) {
            engineStatus.innerText = "Engine: Ready";
            loadDocuments();
        }
    } catch (e) {
        console.error("Upload failed", e);
    }
}

// --- Authentication State Management ---
function switchState(state) {
    document.getElementById("state-login").classList.add("hidden");
    document.getElementById("state-signup").classList.add("hidden");
    document.getElementById("state-forgot").classList.add("hidden");
    document.getElementById("login-error").classList.add("hidden");
    
    document.getElementById("state-" + state).classList.remove("hidden");
}

async function handleSignup() {
    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;
    const question = document.getElementById("reg-question").value;
    const answer = document.getElementById("reg-answer").value;
    const dob = document.getElementById("reg-dob").value;

    try {
        const response = await fetch(`${BASE_URL}/auth/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                email, password, 
                security_question: question, 
                security_answer: answer, 
                dob 
            })
        });

        if (response.ok) {
            alert("Account created! Please log in.");
            switchState("login");
        } else {
            document.getElementById("login-error").innerText = "Signup failed.";
            document.getElementById("login-error").classList.remove("hidden");
        }
    } catch (e) { console.error(e); }
}

async function handleRecoveryVerify() {
    const email = document.getElementById("recovery-email").value;
    const answer = document.getElementById("recovery-answer").value;
    const dob = document.getElementById("recovery-dob").value;

    try {
        const response = await fetch(`${BASE_URL}/auth/reset-password-verify`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, answer, dob })
        });

        if (response.ok) {
            const newPass = prompt("Identity Verified. Enter new password:");
            if (newPass) {
                await fetch(`${BASE_URL}/auth/reset-password-confirm`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, new_password: newPass })
                });
                alert("Password updated!");
                switchState("login");
            }
        } else {
            document.getElementById("login-error").innerText = "Recovery failed. Incorrect Answer or DOB.";
            document.getElementById("login-error").classList.remove("hidden");
        }
    } catch (e) { console.error(e); }
}

// --- Event Listeners ---
btnExecute.addEventListener("click", executeQuery);
userInput.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); executeQuery(); } });
document.getElementById("btn-login-submit").addEventListener("click", login);
document.getElementById("btn-signup-submit").addEventListener("click", handleSignup);
document.getElementById("btn-logout").addEventListener("click", logout);
document.getElementById("upload-area").addEventListener("click", () => document.getElementById("file-input").click());
document.getElementById("file-input").addEventListener("change", handleUpload);

// Recovery Listeners
document.getElementById("btn-recovery-next").addEventListener("click", () => {
    document.getElementById("recovery-step-1").classList.add("hidden");
    document.getElementById("recovery-step-2").classList.remove("hidden");
    document.getElementById("display-question").innerText = "Security Challenge: Active";
});
document.getElementById("btn-recovery-verify").addEventListener("click", handleRecoveryVerify);

// Initialize
checkAuth();
if (authToken) loadDocuments();
