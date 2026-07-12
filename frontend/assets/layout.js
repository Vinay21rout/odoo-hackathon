const API_BASE_URL = localStorage.getItem("api_base_url") || "http://localhost:8000/api/v1";

// Toast deduplication state
let lastToastText = "";
let lastToastTime = 0;

// Show Alert Toasts
function showToast(message, type = "success") {
    const now = Date.now();
    if (message === lastToastText && now - lastToastTime < 1000) {
        return; // Suppress duplicate alerts in rapid succession
    }
    lastToastText = message;
    lastToastTime = now;

    const container = document.getElementById("toast-container") || createToastContainer();
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    let icon = "fa-check-circle";
    let color = "#10b981";
    if (type === "error") {
        icon = "fa-exclamation-circle";
        color = "#ef4444";
    } else if (type === "warning") {
        icon = "fa-exclamation-triangle";
        color = "#f59e0b";
    }
    toast.innerHTML = `<i class="fas ${icon}" style="color: ${color}"></i> <span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 4000);
}

function createToastContainer() {
    const el = document.createElement("div");
    el.id = "toast-container";
    el.className = "toast-container";
    document.body.appendChild(el);
    return el;
}
// Centralized API Helper
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem("token");
    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
    };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    
    // Auto-inject Loading Spinner on lists matching the endpoint precisely to avoid concurrent clashes
    let activeTbody = null;
    if (!options.method || options.method === "GET") {
        let targetId = null;
        if (endpoint.startsWith("/departments")) {
            targetId = "departments-tbody";
        } else if (endpoint.startsWith("/employees")) {
            targetId = "employees-tbody";
        } else if (endpoint.startsWith("/environmental")) {
            targetId = "metrics-tbody";
        } else if (endpoint.startsWith("/social")) {
            targetId = "social-tbody";
        } else if (endpoint.startsWith("/governance")) {
            targetId = "governance-tbody";
        } else if (endpoint.startsWith("/reports")) {
            targetId = "reports-tbody";
        } else if (endpoint.startsWith("/gamification/leaderboard") && !endpoint.includes("silent=true")) {
            targetId = "leaderboard-tbody";
        }

        if (targetId) {
            const el = document.getElementById(targetId);
            if (el) {
                activeTbody = el;
            }
        }
    }

    if (activeTbody) {
        activeTbody.innerHTML = `
            <tr>
                <td colspan="100%" style="text-align: center; padding: 40px; color: var(--text-secondary);">
                    <i class="fas fa-circle-notch fa-spin" style="font-size: 26px; color: var(--primary-color); margin-bottom: 12px;"></i>
                    <div style="font-weight: 500; font-size: 14px;">Retrieving latest indicators...</div>
                </td>
            </tr>
        `;
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers,
        });
        
        if (response.status === 401) {
            localStorage.removeItem("token");
            localStorage.removeItem("user_email");
            if (!window.location.pathname.includes("login.html")) {
                window.location.href = "login.html?expired=true";
            }
            throw new Error("Session expired. Please log in again.");
        }

        const json = await response.json();
        
        if (!response.ok) {
            const errorMsg = json.message || (json.errors && json.errors.join(", ")) || "An API transaction failure occurred.";
            throw new Error(errorMsg);
        }
        
        // Success Toast trigger for mutations
        if (options.method && options.method !== "GET") {
            let actionWord = "completed";
            if (options.method === "POST") actionWord = "created";
            if (options.method === "PUT") actionWord = "updated";
            if (options.method === "DELETE") actionWord = "deleted";
            showToast(`Record successfully ${actionWord}!`, "success");
        }

        return json;
    } catch (err) {
        if (err.message !== "Session expired. Please log in again.") {
            showToast(err.message || "A network or server connection error occurred.", "error");
        }
        
        // Put error message inside table body for context if query fails
        if (activeTbody) {
            activeTbody.innerHTML = `
                <tr>
                    <td colspan="100%" style="text-align: center; padding: 32px; color: var(--error-color);">
                        <i class="fas fa-exclamation-triangle" style="font-size: 24px; margin-bottom: 12px;"></i>
                        <div style="font-weight: 600;">Failed to Load Dataset</div>
                        <div style="font-size: 13px; color: var(--text-secondary); margin-top: 4px;">${err.message}</div>
                    </td>
                </tr>
            `;
        }
        throw err;
    }
}

// Shared layouts injection
function getSidebarHTML() {
    const activeClass = (path) => window.location.pathname.includes(path) ? "active" : "";
    const userRole = localStorage.getItem("user_role") || "employee";
    const isAdmin = userRole === "admin";
    
    return `
        <div class="sidebar-header">
            <div class="logo-brand-sidebar">
                <span class="eco">Ec</span><span class="logo-o"><i class="fas fa-globe-americas globe"></i><i class="fas fa-leaf leaf"></i></span><span class="sphere">Sphere</span><span class="ai-badge">AI</span>
            </div>
        </div>
        <ul class="sidebar-menu">
            <li class="sidebar-item ${activeClass('dashboard.html')}">
                <a href="dashboard.html"><i class="fas fa-chart-line"></i> Dashboard</a>
            </li>
            ${isAdmin ? `
            <li class="sidebar-item ${activeClass('departments.html')}">
                <a href="departments.html"><i class="fas fa-sitemap"></i> Departments</a>
            </li>
            <li class="sidebar-item ${activeClass('employees.html')}">
                <a href="employees.html"><i class="fas fa-users"></i> Employees</a>
            </li>
            ` : ''}
            <li class="sidebar-item ${activeClass('environmental.html')}">
                <a href="environmental.html"><i class="fas fa-leaf"></i> Environmental</a>
            </li>
            <li class="sidebar-item ${activeClass('social.html')}">
                <a href="social.html"><i class="fas fa-heart"></i> Social</a>
            </li>
            <li class="sidebar-item ${activeClass('governance.html')}">
                <a href="governance.html"><i class="fas fa-shield-alt"></i> Governance</a>
            </li>
            <li class="sidebar-item ${activeClass('challenges.html')}">
                <a href="challenges.html"><i class="fas fa-trophy"></i> Gamification</a>
            </li>
            <li class="sidebar-item ${activeClass('reports.html')}">
                <a href="reports.html"><i class="fas fa-file-invoice"></i> Reports</a>
            </li>
            ${isAdmin ? `
            <li class="sidebar-item ${activeClass('settings.html')}">
                <a href="settings.html"><i class="fas fa-cog"></i> Settings</a>
            </li>
            ` : ''}
        </ul>
        <div class="sidebar-footer">
            <button class="logout-btn" onclick="handleLogout()">
                <i class="fas fa-sign-out-alt"></i> Logout
            </button>
        </div>
    `;
}

function applyRoleBasedAccess() {
    const userRole = localStorage.getItem("user_role") || "employee";
    const isAdmin = userRole === "admin";
    
    // Hide/show admin-only elements
    document.querySelectorAll(".admin-only").forEach(el => {
        if (isAdmin) {
            el.style.display = ""; // restore default display
        } else {
            el.style.display = "none";
        }
    });
    
    // Redirect if on admin page and not admin
    const adminPages = ["departments.html", "employees.html", "settings.html"];
    const isCurrentPageAdmin = adminPages.some(page => window.location.pathname.includes(page));
    if (isCurrentPageAdmin && !isAdmin) {
        window.location.href = "dashboard.html";
    }
}

async function syncUserRole() {
    const token = localStorage.getItem("token");
    const userEmail = localStorage.getItem("user_email");
    if (!token || !userEmail) return;
    
    const prevRole = localStorage.getItem("user_role");
    let currentRole = "employee";
    
    if (userEmail === "admin@ecosphere.ai" || token === "mock-admin-uid") {
        currentRole = "admin";
    }
    
    localStorage.setItem("user_role", currentRole);
    
    // Attempt to fetch profile from DB to verify role
    try {
        const empRes = await apiCall(`/employees?search=${encodeURIComponent(userEmail)}`);
        if (empRes && empRes.success && empRes.data.items.length > 0) {
            const emp = empRes.data.items.find(e => e.email === userEmail) || empRes.data.items[0];
            if (emp.role_id === "c1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d") {
                currentRole = "admin";
            } else {
                currentRole = "employee";
            }
            localStorage.setItem("user_role", currentRole);
        }
    } catch (e) {
        console.warn("Could not verify user role from server, using default.");
    }
    
    if (prevRole !== currentRole) {
        // Re-render sidebar and apply access controls
        const sidebar = document.getElementById("sidebar-container");
        if (sidebar) {
            sidebar.innerHTML = getSidebarHTML();
        }
        applyRoleBasedAccess();
    }
}

function getNavbarHTML() {
    const userEmail = localStorage.getItem("user_email") || "User";
    const userLetter = userEmail.charAt(0).toUpperCase();
    return `
        <div class="header-title" id="page-header-title"></div>
        <div style="display: flex; align-items: center; gap: 20px;">
            <!-- Notification Bell -->
            <div class="notification-bell-container" style="position: relative; cursor: pointer;">
                <i class="fas fa-bell" id="notification-bell" style="font-size: 20px; color: var(--text-secondary); transition: color 0.3s;"></i>
                <span class="notification-badge" id="notification-count" style="display: none; position: absolute; top: -8px; right: -8px; background: var(--error-color, #ef4444); color: white; border-radius: 50%; padding: 2px 6px; font-size: 10px; font-weight: 700;">0</span>
                <!-- Notifications Dropdown -->
                <div class="notifications-dropdown glass-card" id="notifications-dropdown" style="display: none; position: absolute; top: 35px; right: 0; width: 300px; max-height: 400px; overflow-y: auto; z-index: 1000; padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.15); box-shadow: var(--shadow-lg); background: rgba(30, 41, 59, 0.95); backdrop-filter: blur(10px);">
                    <div style="font-weight: 700; font-size: 14px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <span>System Alerts</span>
                        <span style="font-size: 11px; font-weight: 400; color: var(--primary-color); cursor: pointer;" id="clear-notifications-btn">Mark all read</span>
                    </div>
                    <div id="notifications-list" style="display: flex; flex-direction: column; gap: 8px;">
                        <div style="text-align: center; color: var(--text-secondary); font-size: 12px; padding: 10px 0;">No new notifications</div>
                    </div>
                </div>
            </div>

            <div class="user-profile-menu">
                <div class="profile-info" style="text-align: right;">
                    <div style="font-weight: 600; font-size: 14px;">${userEmail}</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">Organization Employee</div>
                </div>
                <div class="profile-avatar">${userLetter}</div>
            </div>
        </div>
    `;
}

// Fetch and render notifications
async function updateNotifications() {
    const bellContainer = document.querySelector(".notification-bell-container");
    if (!bellContainer) return;

    try {
        const response = await apiCall("/notifications");
        const notifications = response.data || [];
        const countEl = document.getElementById("notification-count");
        const listEl = document.getElementById("notifications-list");
        
        if (notifications.length > 0) {
            countEl.textContent = notifications.length;
            countEl.style.display = "inline-block";
            
            listEl.innerHTML = notifications.map(n => {
                let iconClass = "fa-info-circle";
                let iconColor = "var(--primary-color)";
                if (n.type === "compliance") {
                    iconClass = "fa-exclamation-triangle";
                    iconColor = "var(--error-color, #ef4444)";
                } else if (n.type === "badge") {
                    iconClass = "fa-medal";
                    iconColor = "#f59e0b";
                } else if (n.type === "challenge") {
                    iconClass = "fa-trophy";
                    iconColor = "#eab308";
                }
                
                return `
                    <div class="notification-item" onclick="markNotificationRead('${n.id}')" style="display: flex; gap: 10px; padding: 8px; border-radius: 6px; cursor: pointer; transition: background 0.2s; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <i class="fas ${iconClass}" style="color: ${iconColor}; font-size: 16px; margin-top: 2px;"></i>
                        <div style="flex: 1;">
                            <div style="font-size: 12px; color: var(--text-primary); font-weight: 500;">${n.message}</div>
                            <div style="font-size: 10px; color: var(--text-secondary); margin-top: 2px;">${new Date(n.created_at).toLocaleTimeString()}</div>
                        </div>
                    </div>
                `;
            }).join("");
        } else {
            countEl.style.display = "none";
            listEl.innerHTML = `<div style="text-align: center; color: var(--text-secondary); font-size: 12px; padding: 10px 0;">No new notifications</div>`;
        }
    } catch (err) {
        console.error("Failed to load notifications:", err);
    }
}

async function markNotificationRead(id) {
    try {
        await apiCall(`/notifications/${id}/read`, { method: "PUT" });
        updateNotifications();
    } catch (err) {
        console.error("Failed to mark notification as read:", err);
    }
}

async function clearAllNotifications() {
    try {
        const response = await apiCall("/notifications");
        const notifications = response.data || [];
        await Promise.all(notifications.map(n => apiCall(`/notifications/${n.id}/read`, { method: "PUT" })));
        updateNotifications();
    } catch (err) {
        console.error("Failed to clear notifications:", err);
    }
}

function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user_email");
    window.location.href = "login.html";
}

// Inject layouts on load
document.addEventListener("DOMContentLoaded", () => {
    // 1. Inject glassmorphic background glowing circles
    const glowContainer = document.createElement("div");
    glowContainer.className = "glow-bg-container";
    glowContainer.innerHTML = `
        <div class="bg-glow-circle bg-glow-circle-1"></div>
        <div class="bg-glow-circle bg-glow-circle-2"></div>
        <div class="bg-glow-circle bg-glow-circle-3"></div>
    `;
    document.body.prepend(glowContainer);

    // 2. Load GSAP library and trigger animations
    if (typeof gsap === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js';
        script.onload = () => {
            initGsapAnimations();
        };
        document.head.appendChild(script);
    } else {
        initGsapAnimations();
    }

    // 3. Configure Chart.js global defaults for White & Blue light theme
    if (typeof Chart !== 'undefined') {
        Chart.defaults.color = '#475569'; // Slate-600 (Text)
        Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.05)'; // Light border grid lines
        if (Chart.defaults.plugins && Chart.defaults.plugins.tooltip) {
            Chart.defaults.plugins.tooltip.backgroundColor = '#0f172a'; // Slate-900 tooltip bg
            Chart.defaults.plugins.tooltip.titleColor = '#ffffff';
            Chart.defaults.plugins.tooltip.bodyColor = '#ffffff';
        }
    }

    const token = localStorage.getItem("token");
    if (!token && !window.location.pathname.includes("login.html")) {
        window.location.href = "login.html";
        return;
    }
    
    if (!window.location.pathname.includes("login.html")) {
        applyRoleBasedAccess();
        syncUserRole();
        injectProfileModal();
    }
    
    const sidebar = document.getElementById("sidebar-container");
    if (sidebar) {
        sidebar.className = "sidebar";
        sidebar.innerHTML = getSidebarHTML();
    }
    
    const navbar = document.getElementById("navbar-container");
    if (navbar) {
        navbar.className = "header-nav";
        navbar.innerHTML = getNavbarHTML();
        
        const headerTitle = document.getElementById("page-header-title");
        if (headerTitle) {
            headerTitle.textContent = document.title || "EcoSphere AI";
        }
        
        // Notifications listeners
        const bell = document.getElementById("notification-bell");
        const dropdown = document.getElementById("notifications-dropdown");
        const clearBtn = document.getElementById("clear-notifications-btn");
        
        if (bell && dropdown) {
            bell.addEventListener("click", (e) => {
                e.stopPropagation();
                dropdown.style.display = dropdown.style.display === "none" ? "block" : "none";
            });
            
            document.addEventListener("click", () => {
                dropdown.style.display = "none";
            });
            
            dropdown.addEventListener("click", (e) => {
                e.stopPropagation();
            });
        }
        
        if (clearBtn) {
            clearBtn.addEventListener("click", clearAllNotifications);
        }
        
        // Initial load and periodic update
        updateNotifications();
        setInterval(updateNotifications, 10000); // refresh every 10 seconds
    }

    // 4. Check for Firebase auth domain fallback parameter to show explanation toast
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth_fallback') === 'true') {
        const newUrl = window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);
        setTimeout(() => {
            showToast("Firebase Auth domain restricted on this host. Switched automatically to offline/demo simulation mode.", "warning");
        }, 1200);
    }
});

// GSAP Animations Engine
function initGsapAnimations() {
    // 1. Sidebar slide-in and links staggered display
    if (document.querySelector(".sidebar")) {
        gsap.from(".sidebar", {
            opacity: 0,
            x: -80,
            duration: 1,
            ease: "power3.out"
        });
        gsap.from(".sidebar-item", {
            opacity: 0,
            x: -25,
            duration: 0.8,
            stagger: 0.05,
            delay: 0.25,
            ease: "power2.out"
        });
        // Interactive popping highlight for active tab
        gsap.from(".sidebar-item.active", {
            scale: 0.92,
            duration: 0.75,
            delay: 0.55,
            ease: "elastic.out(1.2, 0.6)"
        });
        gsap.from(".sidebar-footer", {
            opacity: 0,
            y: 30,
            duration: 0.8,
            delay: 0.7,
            ease: "power2.out"
        });
    }

    // 2. Navbar slide-down
    if (document.querySelector(".header-nav")) {
        gsap.from(".header-nav", {
            opacity: 0,
            y: -50,
            duration: 0.8,
            ease: "power3.out"
        });
        gsap.from(".header-nav > *", {
            opacity: 0,
            y: -15,
            duration: 0.6,
            stagger: 0.1,
            delay: 0.35,
            ease: "power2.out"
        });
    }

    // 3. Grid metric cards back animation
    if (document.querySelector(".stats-card")) {
        gsap.from(".stats-card", {
            opacity: 0,
            y: 45,
            scale: 0.95,
            duration: 0.9,
            stagger: 0.08,
            ease: "back.out(1.3)"
        });
    }

    // 4. Glass panels fade-up
    if (document.querySelector(".glass-panel")) {
        gsap.from(".glass-panel", {
            opacity: 0,
            y: 40,
            duration: 0.85,
            stagger: 0.12,
            delay: 0.15,
            ease: "power3.out"
        });
    }

    // 5. Table container and rows stagger
    if (document.querySelector(".table-responsive")) {
        gsap.from(".table-responsive", {
            opacity: 0,
            y: 30,
            duration: 0.8,
            delay: 0.25,
            ease: "power2.out"
        });
        gsap.from(".custom-table tbody tr", {
            opacity: 0,
            y: 12,
            duration: 0.5,
            stagger: 0.04,
            delay: 0.45,
            ease: "power2.out"
        });
    }

    // 6. Login card animations
    if (document.querySelector(".login-card")) {
        gsap.from(".login-card", {
            opacity: 0,
            y: 60,
            scale: 0.96,
            duration: 1.2,
            ease: "power4.out"
        });
        gsap.from(".login-logo > *", {
            opacity: 0,
            y: 20,
            duration: 0.8,
            stagger: 0.1,
            delay: 0.2,
            ease: "power2.out"
        });
    }

    // 7. Background glowing circles floating animation
    if (document.querySelector(".bg-glow-circle-1")) {
        gsap.to(".bg-glow-circle-1", {
            x: '15vw',
            y: '10vh',
            duration: 16,
            repeat: -1,
            yoyo: true,
            ease: "sine.inOut"
        });
    }
    if (document.querySelector(".bg-glow-circle-2")) {
        gsap.to(".bg-glow-circle-2", {
            x: '-12vw',
            y: '-18vh',
            duration: 20,
            repeat: -1,
            yoyo: true,
            ease: "sine.inOut"
        });
    }
    if (document.querySelector(".bg-glow-circle-3")) {
        gsap.to(".bg-glow-circle-3", {
            x: '-8vw',
            y: '8vh',
            duration: 14,
            repeat: -1,
            yoyo: true,
            ease: "sine.inOut"
        });
    }
}

// Global Profile Modal Implementation (Wireframe Feature: Profile Editing)
function injectProfileModal() {
    const profileModal = document.createElement("div");
    profileModal.id = "global-profile-modal";
    profileModal.className = "modal-overlay";
    profileModal.innerHTML = `
        <div class="modal-box" style="max-width: 420px; padding: 32px;">
            <div class="modal-title" style="margin-bottom: 24px; font-weight: 700; font-size: 20px; color: var(--text-primary);">Edit Your Employee Profile</div>
            <form id="global-profile-form">
                <input type="hidden" id="profile-emp-id">
                <div class="form-group" style="margin-bottom: 16px;">
                    <label for="profile-name" style="display: block; font-size: 13px; font-weight: 600; margin-bottom: 8px; color: var(--text-secondary);">Full Name</label>
                    <input type="text" id="profile-name" class="form-control" placeholder="Enter full name" required style="padding: 12px 16px;">
                </div>
                <div class="form-group" style="margin-bottom: 16px;">
                    <label for="profile-email" style="display: block; font-size: 13px; font-weight: 600; margin-bottom: 8px; color: var(--text-secondary);">Email Address</label>
                    <input type="email" id="profile-email" class="form-control" readonly style="background-color: var(--bg-color); cursor: not-allowed; padding: 12px 16px; border-color: var(--surface-border);">
                </div>
                <div class="form-group" style="margin-bottom: 24px;">
                    <label for="profile-dept" style="display: block; font-size: 13px; font-weight: 600; margin-bottom: 8px; color: var(--text-secondary);">Department</label>
                    <select id="profile-dept" class="form-control" required style="padding: 12px 16px;">
                        <option value="">Select department...</option>
                    </select>
                </div>
                <div class="form-buttons" style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px;">
                    <button type="button" class="btn-secondary" onclick="closeProfileModal()" style="padding: 10px 20px;">Cancel</button>
                    <button type="submit" class="btn-primary" style="padding: 10px 20px;">Save Changes</button>
                </div>
            </form>
        </div>
    `;
    document.body.appendChild(profileModal);

    // Bind click listener on profile menu
    const profileMenu = document.querySelector(".user-profile-menu");
    if (profileMenu) {
        profileMenu.style.cursor = "pointer";
        profileMenu.addEventListener("click", openProfileModal);
    }
}

function closeProfileModal() {
    document.getElementById("global-profile-modal").classList.remove("active");
}

async function openProfileModal() {
    const modal = document.getElementById("global-profile-modal");
    const userEmail = localStorage.getItem("user_email") || "admin@ecosphere.ai";
    
    document.getElementById("profile-email").value = userEmail;
    
    // Populate departments dropdown
    try {
        const deptRes = await apiCall("/departments?limit=100");
        const deptSelect = document.getElementById("profile-dept");
        deptSelect.innerHTML = '<option value="">Select department...</option>';
        if (deptRes && deptRes.success) {
            deptRes.data.items.forEach(d => {
                const opt = document.createElement("option");
                opt.value = d.id;
                opt.textContent = d.name;
                deptSelect.appendChild(opt);
            });
        }
    } catch (e) {
        console.warn("Failed to load departments for profile editing:", e);
    }

    // Try to load current employee details from backend
    try {
        const empRes = await apiCall(`/employees?search=${encodeURIComponent(userEmail)}`);
        if (empRes && empRes.success && empRes.data.items.length > 0) {
            const emp = empRes.data.items.find(e => e.email === userEmail) || empRes.data.items[0];
            document.getElementById("profile-emp-id").value = emp.id;
            document.getElementById("profile-name").value = emp.full_name;
            if (emp.department_id) {
                document.getElementById("profile-dept").value = emp.department_id;
            }
        } else {
            document.getElementById("profile-emp-id").value = "";
            document.getElementById("profile-name").value = "";
        }
    } catch (err) {
        console.warn("User profile not found in DB. Form will provision a new one.");
        document.getElementById("profile-emp-id").value = "";
        document.getElementById("profile-name").value = "";
    }

    modal.classList.add("active");
}

// Global handler for profile submission
document.addEventListener("submit", async (e) => {
    if (e.target && e.target.id === "global-profile-form") {
        e.preventDefault();
        const empId = document.getElementById("profile-emp-id").value;
        const name = document.getElementById("profile-name").value.trim();
        const email = document.getElementById("profile-email").value.trim();
        const deptId = document.getElementById("profile-dept").value;
        
        try {
            let res;
            if (empId) {
                res = await apiCall(`/employees/${empId}`, {
                    method: "PUT",
                    body: JSON.stringify({
                        full_name: name,
                        department_id: deptId
                    })
                });
            } else {
                let role_id = "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"; // Standard Employee Role ID
                res = await apiCall("/employees", {
                    method: "POST",
                    body: JSON.stringify({
                        full_name: name,
                        email: email,
                        department_id: deptId,
                        role_id: role_id
                    })
                });
            }

            if (res && res.success) {
                showToast("Profile updated successfully!");
                closeProfileModal();
                
                // Update profile avatar dynamically
                const userLetterEl = document.querySelector(".profile-avatar");
                const userNameEl = document.querySelector(".profile-info div");
                if (userLetterEl) userLetterEl.textContent = name.charAt(0).toUpperCase();
                if (userNameEl) userNameEl.textContent = name;
                
                // Reload on challenges or employees page
                if (window.location.pathname.includes("challenges.html") || window.location.pathname.includes("employees.html")) {
                    setTimeout(() => window.location.reload(), 800);
                }
            }
        } catch (err) {
            showToast(err.message || "Failed to update profile.", "error");
        }
    }
});
