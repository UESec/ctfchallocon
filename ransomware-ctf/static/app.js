const countdown = document.getElementById("countdown");
const decryptButton = document.getElementById("decrypt-button");
const decryptKey = document.getElementById("decrypt-key");
const decryptMessage = document.getElementById("decrypt-message");
const fileList = document.getElementById("file-list");
const viewerTitle = document.getElementById("viewer-title");
const viewerStatus = document.getElementById("viewer-status");
const viewerContent = document.getElementById("viewer-content");
const noteTrigger = document.getElementById("ransom-note-trigger");
const noteModal = document.getElementById("note-modal");
const closeModal = document.getElementById("close-modal");

let restoredFiles = {};

function startCountdown() {
    let seconds = 48 * 60 * 60;

    setInterval(() => {
        seconds--;

        const h = String(Math.floor(seconds / 3600)).padStart(2, "0");
        const m = String(Math.floor((seconds % 3600) / 60)).padStart(2, "0");
        const s = String(seconds % 60).padStart(2, "0");

        countdown.textContent = `${h}:${m}:${s}`;

        if (seconds <= 0) {
            seconds = 48 * 60 * 60;
        }
    }, 1000);
}

function openRansomNote() {
    noteModal.classList.add("show");
}

function closeRansomNote() {
    noteModal.classList.remove("show");
}

function bindEncryptedFileButtons() {
    document.querySelectorAll(".encrypted-file").forEach((button) => {
        button.addEventListener("click", () => {
            viewerTitle.textContent = button.innerText.split("\n")[0].replace("🔒", "").trim();
            viewerStatus.textContent = "ENCRYPTED";
            viewerContent.textContent =
                "File content cannot be previewed.\n\n" +
                "The object is encrypted with .cl0p recovery protection.\n" +
                "Use the decryptor after obtaining the recovery key.";
        });
    });
}

function renderRestoredFiles(files) {
    restoredFiles = {};

    fileList.innerHTML = "";

    files.forEach((file) => {
        restoredFiles[file.name] = file.content;

        const button = document.createElement("button");
        button.className = "file restored-file";
        button.innerHTML = `
            <span>🔓 ${file.name}</span>
            <small>${file.size} bytes · restored</small>
        `;

        button.addEventListener("click", () => {
            viewerTitle.textContent = file.name;
            viewerStatus.textContent = "RESTORED";
            viewerContent.textContent = file.content;
        });

        fileList.appendChild(button);
    });
}

async function decryptFiles() {
    const key = decryptKey.value.trim();

    decryptMessage.textContent = "Trying recovery key...";
    decryptButton.disabled = true;

    try {
        const response = await fetch("/api/decrypt", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ key })
        });

        const data = await response.json();

        if (!data.ok) {
            decryptMessage.textContent = data.message;
            decryptButton.disabled = false;
            return;
        }

        decryptMessage.textContent = data.message;
        renderRestoredFiles(data.files);

        viewerTitle.textContent = "recovery.log";
        viewerStatus.textContent = "SUCCESS";
        viewerContent.textContent =
            "Recovery key accepted.\n" +
            "Encrypted objects restored.\n\n" +
            "Open the restored files from the left panel.";

    } catch (error) {
        decryptMessage.textContent = "Recovery utility failed. Try again.";
    }

    decryptButton.disabled = false;
}

function startMatrix() {
    const canvas = document.getElementById("matrix");
    const ctx = canvas.getContext("2d");

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    resize();
    window.addEventListener("resize", resize);

    const chars = "01XMONCL0PKIMSUKY橙LOCKED";
    const fontSize = 16;
    let columns = Math.floor(canvas.width / fontSize);
    let drops = Array(columns).fill(1);

    setInterval(() => {
        ctx.fillStyle = "rgba(5, 0, 0, 0.08)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = "rgba(255, 30, 30, 0.78)";
        ctx.font = `${fontSize}px monospace`;

        for (let i = 0; i < drops.length; i++) {
            const text = chars[Math.floor(Math.random() * chars.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }

            drops[i]++;
        }
    }, 45);
}

noteTrigger.addEventListener("mouseenter", openRansomNote);
noteTrigger.addEventListener("click", openRansomNote);
closeModal.addEventListener("click", closeRansomNote);
decryptButton.addEventListener("click", decryptFiles);

bindEncryptedFileButtons();
startCountdown();
startMatrix();
