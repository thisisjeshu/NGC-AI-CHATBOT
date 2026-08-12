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

        const list =
            document.getElementById("noticesList");

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

        console.error(
            "Notice loading error:",
            error
        );
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
// Load Events
// --------------------------------------------------

async function loadEvents() {

    try {

        const response = await fetch(
            `${API_URL}/admin/events/`,
            {
                headers: authHeaders()
            }
        );

        if (!response.ok) {
            throw new Error("Failed to load events");
        }

        const events = await response.json();

        document.getElementById("eventCount").textContent =
            events.length;

        const list =
            document.getElementById("eventsList");

        if (events.length === 0) {

            list.innerHTML =
                '<div class="empty">No events available.</div>';

            return;
        }

        list.innerHTML = events.map(event => `

            <div class="item">

                <div>

                    <strong>
                        ${escapeHTML(event.title)}
                    </strong>

                    <p>
                        ${escapeHTML(
                            event.venue || "Venue not specified"
                        )}
                    </p>

                    ${
                        event.event_date
                        ? `<small>
                            ${escapeHTML(
                                new Date(event.event_date)
                                    .toLocaleString()
                            )}
                           </small>`
                        : ""
                    }

                </div>

                <button
                    class="delete-btn"
                    onclick="deleteEvent(${event.id})"
                >
                    Delete
                </button>

            </div>

        `).join("");

    } catch (error) {

        console.error(
            "Event loading error:",
            error
        );
    }
}

// --------------------------------------------------
// Add Event
// --------------------------------------------------

async function addEvent() {

    const title = prompt("Event title:");

    if (!title) {
        return;
    }

    const description =
        prompt("Event description (optional):") || null;

    const venue =
        prompt("Event venue (optional):") || null;

    const eventDate =
        prompt(
            "Event date and time (optional):\nExample: 2026-08-20T10:00"
        ) || null;

    const imageUrl =
        prompt("Image URL (optional):") || null;

    const registrationUrl =
        prompt("Registration URL (optional):") || null;

    try {

        const response = await fetch(
            `${API_URL}/admin/events/`,
            {
                method: "POST",
                headers: authHeaders(),

                body: JSON.stringify({

                    title: title,

                    description: description,

                    venue: venue,

                    event_date: eventDate,

                    image_url: imageUrl,

                    registration_url: registrationUrl,

                    published: true
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail || "Failed to create event"
            );
        }

        alert("Event created successfully.");

        await loadEvents();

    } catch (error) {

        console.error(
            "Event creation error:",
            error
        );

        alert(error.message);
    }
}

// --------------------------------------------------
// Delete Event
// --------------------------------------------------

async function deleteEvent(eventId) {

    const confirmed = confirm(
        "Are you sure you want to delete this event?"
    );

    if (!confirmed) {
        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/admin/events/${eventId}`,
            {
                method: "DELETE",
                headers: authHeaders()
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail || "Failed to delete event"
            );
        }

        alert("Event deleted successfully.");

        await loadEvents();

    } catch (error) {

        console.error(
            "Event deletion error:",
            error
        );

        alert(error.message);
    }
}

// --------------------------------------------------
// Logout
// --------------------------------------------------

function logout() {

    localStorage.removeItem(
        "ngc_admin_token"
    );

    localStorage.removeItem(
        "ngc_admin_username"
    );

    localStorage.removeItem(
        "ngc_admin_role"
    );

    window.location.replace("login.html");
}

// --------------------------------------------------
// Button Events
// --------------------------------------------------

const addNoticeBtn =
    document.getElementById("addNoticeBtn");

if (addNoticeBtn) {

    addNoticeBtn.addEventListener(
        "click",
        addNotice
    );
}

const addEventBtn =
    document.getElementById("addEventBtn");

if (addEventBtn) {

    addEventBtn.addEventListener(
        "click",
        addEvent
    );
}

// --------------------------------------------------
// Start Dashboard
// --------------------------------------------------

loadNotices();
loadEvents();