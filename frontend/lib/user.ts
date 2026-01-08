/**
 * User ID Management for TaxMate
 * Simple localStorage-based user ID for demo purposes
 */

const USER_ID_KEY = 'taxmate_user_id';

/**
 * Get or generate a user ID
 * In production, this would come from authentication
 */
export function getUserId(): string {
    if (typeof window === 'undefined') return 'ssr_user';

    let userId = localStorage.getItem(USER_ID_KEY);

    if (!userId) {
        // Generate a simple user ID
        userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem(USER_ID_KEY, userId);
        console.log(`Generated new user ID: ${userId}`);
    }

    return userId;
}

/**
 * Clear user ID (for testing different users)
 */
export function clearUserId(): void {
    if (typeof window !== 'undefined') {
        localStorage.removeItem(USER_ID_KEY);
    }
}

/**
 * Get headers with X-User-Id for API calls
 */
export function getApiHeaders(contentType?: string): HeadersInit {
    const headers: HeadersInit = {
        'X-User-Id': getUserId(),
    };

    if (contentType) {
        headers['Content-Type'] = contentType;
    }

    return headers;
}
