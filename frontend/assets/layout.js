const API_BASE_URL = localStorage.getItem("api_base_url") || "http://localhost:8000/api/v1";

// Helper to make API calls
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem("token");
    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
    };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers,
        });
        const json = await response.json();
        if (!response.ok) {
            throw new Error(json.message || "An error occurred");
        }
        return json;
    } catch (err) {
        console.error("API Call Error:", err);
        throw err;
    }
}

// Show Alert Toasts
function showToast(message, type = "success") {
    const container = document.getElementById("toast-container") || createToastContainer();
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    let icon = "fa-check-circle";
    let color = "#10b981";
    if (type === "error") {
        icon = "fa-exclamation-circle";
        color = "#ef4444";
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

// Shared layouts injection
function getSidebarHTML() {
    const activeClass = (path) => window.location.pathname.includes(path) ? "active" : "";
    return `
        <div class="sidebar-header">
            <div class="logo-text">
                <i class="fas fa-globe-americas"></i> EcoSphere AI
            </div>
        </div>
        <ul class="sidebar-menu">
            <li class="sidebar-item ${activeClass('dashboard.html')}">
                <a href="dashboard.html"><i class="fas fa-chart-line"></i> Dashboard</a>
            </li>
            <li class="sidebar-item ${activeClass('departments.html')}">
                <a href="departments.html"><i class="fas fa-sitemap"></i> Departments</a>
            </li>
            <li class="sidebar-item ${activeClass('employees.html')}">
                <a href="employees.html"><i class="fas fa-users"></i> Employees</a>
            </li>
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
            <li class="sidebar-item ${activeClass('settings.html')}">
                <a href="settings.html"><i class="fas fa-cog"></i> Settings</a>
            </li>
        </ul>
        <div class="sidebar-footer">
            <button class="logout-btn" onclick="handleLogout()">
                <i class="fas fa-sign-out-alt"></i> Logout
            </button>
        </div>
    `;
}

function getNavbarHTML() {
    const userEmail = localStorage.getItem("user_email") || "User";
    const userLetter = userEmail.charAt(0).toUpperCase();
    return `
        <div class="header-title" id="page-header-title"></div>
        <div class="user-profile-menu">
            <div class="profile-info" style="text-align: right;">
                <div style="font-weight: 600; font-size: 14px;">${userEmail}</div>
                <div style="font-size: 12px; color: var(--text-secondary);">Organization Employee</div>
            </div>
            <div class="profile-avatar">${userLetter}</div>
        </div>
    `;
}

function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user_email");
    window.location.href = "login.html";
}

// Inject layouts on load
document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    if (!token && !window.location.pathname.includes("login.html")) {
        window.location.href = "login.html";
        return;
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
    }
});
