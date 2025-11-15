/**
 * JWT utility functions
 */

export function decodeJWT(token) {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    const decoded = JSON.parse(atob(parts[1]));
    return decoded;
  } catch (e) {
    console.error('Failed to decode JWT:', e);
    return null;
  }
}

export function getTokenRole(token) {
  const decoded = decodeJWT(token);
  return decoded?.role || 'staff';
}
