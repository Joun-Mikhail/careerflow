/**
 * Capacitor / WebView storage adapter.
 *
 * Capacitor wraps the SPA inside a WebView whose `localStorage` is persisted
 * across launches by both the iOS WKWebView and the Android WebView, so the
 * existing token store works as-is. This module exists as a single seam in
 * case we ever need to switch to `@capacitor/preferences` (a native key/value
 * store) on devices where WebView storage is volatile.
 *
 * On the web, `isNative()` returns `false` and the file is effectively inert.
 */

interface CapacitorWindow extends Window {
  Capacitor?: { isNativePlatform?: () => boolean; getPlatform?: () => string };
}

export function isNative(): boolean {
  if (typeof window === 'undefined') return false;
  const cap = (window as CapacitorWindow).Capacitor;
  return typeof cap?.isNativePlatform === 'function' && cap.isNativePlatform();
}

export function platform(): 'web' | 'ios' | 'android' {
  if (typeof window === 'undefined') return 'web';
  const cap = (window as CapacitorWindow).Capacitor;
  const value = cap?.getPlatform?.() ?? 'web';
  return value === 'ios' || value === 'android' ? value : 'web';
}
