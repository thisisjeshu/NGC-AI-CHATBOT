const API_URL = "http://127.0.0.1:8000";

// --------------------------------------------------
// Authentication
// --------------------------------------------------

const token = localStorage.getItem("ngc_admin_token");

if (!token) {
    window.location.replace("login.html");
}

function authHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

// --------------------------------------------------
// HTML Safety
// --------------------------------------------------

function escapeHTML(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

// --------------------------------------------------
// Load Notices
// --------------------------------------------------

async function loadNotices() {
    try {
        const response = await fetch(
            `${API_URL}/admin/notices/`,
            {
                headers: authHeaders()
            }
        );

        if (!response.ok) {
            throw new Error("Failed to load notices");
        }

        const notices = await response.json();

        document.getElementById("noticeCount").textContent =
            notices.length;

        const list = document.getElementById("noticesList");

        if (notices.length === 0) {
            list.innerHTML =
                '<div class="empty">No notices available.</div>';
            return;
        }

        list.innerHTML = notices.map(notice => `
            <div class="item">

                <div>
                    <strong>
                        ${escapeHTML(notice.title)}
                    </strong>

                    <p>
                        ${escapeHTML(
                            notice.category || "General"
                        )}
                    </p>
                </div>

                <button
                    class="delete-btn"
                    onclick="deleteNotice(${notice.id})"
                >
                    Delete
                </button>

            </div>
        `).join("");

    } catch (error) {
        console.error("Notice loading error:", error);
    }
}

// --------------------------------------------------
// Add Notice
// --------------------------------------------------

async function addNotice() {

    const title = prompt("Notice title:");

    if (!title) {
        return;
    }

    const content = prompt("Notice content:");

    if (!content) {
        return;
    }

    const category =
        prompt("Category (optional):") || "General";

    try {

        const response = await fetch(
            `${API_URL}/admin/notices/`,
            {
                method: "POST",
                headers: authHeaders(),

                body: JSON.stringify({
                    title: title,
                    content: content,
                    category: category,
                    priority: "normal",
                    published: true
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Failed to create notice"
            );
        }

        alert("Notice created successfully.");

        await loadNotices();

    } catch (error) {

        console.error(error);

        alert(error.message);
    }
}

// --------------------------------------------------
// Delete Notice
// --------------------------------------------------

async function deleteNotice(noticeId) {

    const confirmed = confirm(
        "Are you sure you want to delete this notice?"
    );

    if (!confirmed) {
        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/admin/notices/${noticeId}`,
            {
                method: "DELETE",
                headers: authHeaders()
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Failed to delete notice"
            );
        }

        alert("Notice deleted successfully.");

        await loadNotices();

    } catch (error) {

        console.error(error);

        alert(error.message);
    }
}

// --------------------------------------------------
// Logout
// --------------------------------------------------

function logout() {

    localStorage.removeItem("ngc_admin_token");
    localStorage.removeItem("ngc_admin_username");
    localStorage.removeItem("ngc_admin_role");

    window.location.replace("login.html");
}

// --------------------------------------------------
// Button Events
// --------------------------------------------------

document
    .getElementById("addNoticeBtn")
    .addEventListener("click", addNotice);

// --------------------------------------------------
// Start Dashboard
// --------------------------------------------------

loadNotices();