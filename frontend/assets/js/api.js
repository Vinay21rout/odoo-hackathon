const API_BASE_URL = localStorage.getItem("api_base_url") || "http://localhost:8000/api/v1";

if (typeof window.apiCall === 'undefined') {
    window.apiCall = async function(endpoint, options = {}) {
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
    };
}
