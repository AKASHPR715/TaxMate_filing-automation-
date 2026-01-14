/**
 * User ID & Authentication Management for TaxMate
 */

const TOKEN_KEY = 'taxmate_auth_token';
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface UserData {
    username: string;
    email: string;
    fullname: string;
    phone_num: string;
    pan: string;
    password: string;
}

/**
 * Get the JWT token from storage
 */
export function getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(TOKEN_KEY);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
    return !!getToken();
}

/**
 * Get User ID (extract from token or fallback)
 * Note: The backend uses the token to identify the user, so this might be less critical for ID,
 * but useful for display if we decode the token.
 */
export function getUserId(): string {
    const token = getToken();
    if (!token) return 'anonymous';

    // Simple decode (production should be more robust)
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.id || payload.sub || 'authenticated_user';
    } catch (e) {
        return 'invalid_token';
    }
}

/**
 * Get headers with Authorization Bearer token for API calls
 */
export function getApiHeaders(contentType?: string): HeadersInit {
    const headers: any = {};

    if (contentType) {
        headers['Content-Type'] = contentType;
    }

    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // Checking if we still need X-User-Id. Some endpoints might rely on it if they haven't been fully migrated to generic Auth dependency.
    // Ideally, the backend extracts user from Token.
    // Adding it just in case legacy logic persists, but Authorization header is key.
    headers['X-User-Id'] = getUserId();

    return headers;
}

/**
 * Login
 */
export async function login(identifier: string, password: string): Promise<void> {
    const res = await fetch(`${BACKEND_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier, password }),
    });

    if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Login failed');
    }

    const data = await res.json();
    localStorage.setItem(TOKEN_KEY, data.access_token);
}

/**
 * Sign Up
 */
export async function signup(userData: UserData): Promise<void> {
    const res = await fetch(`${BACKEND_URL}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
    });

    if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Signup failed');
    }

    const data = await res.json();
    // Assuming signup returns token directly as per backend code
    localStorage.setItem(TOKEN_KEY, data.access_token);
}

/**
 * Logout
 */
export function logout(): void {
    if (typeof window !== 'undefined') {
        localStorage.removeItem(TOKEN_KEY);
        // Optional: Call backend logout API to blacklist token
        window.location.reload();
    }
}
