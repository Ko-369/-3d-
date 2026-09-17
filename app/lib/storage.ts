/**
 * Tiny localStorage helpers. The lab is a client-side learning app with no
 * account system wired up yet, so favourites, notes and progress live in the
 * browser. Every read/write is guarded so SSR and private-mode browsing never
 * throw — a missing `window` or a quota error just degrades to in-memory state.
 */

const PREFIX = "calab:";

export function readJSON<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(PREFIX + key);
    return raw === null ? fallback : (JSON.parse(raw) as T);
  } catch {
    return fallback;
  }
}

export function writeJSON<T>(key: string, value: T): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(PREFIX + key, JSON.stringify(value));
  } catch {
    /* quota / private-mode — ignore, the state simply won't persist */
  }
}

export function removeKey(key: string): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(PREFIX + key);
  } catch {
    /* ignore */
  }
}

export const STORAGE_KEYS = {
  favorites: "favorites",
  notes: "notes",
} as const;
