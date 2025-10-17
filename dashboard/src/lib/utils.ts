import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Converts a UTC timestamp string to a local Date object.
 * Ensures the timestamp is treated as UTC even if it doesn't have a timezone indicator.
 * @param utcTimestamp - UTC timestamp string (e.g., "2024-01-15 10:30:00" or "2024-01-15T10:30:00Z")
 * @returns Date object in local timezone
 */
export function utcToLocal(utcTimestamp: string): Date {
  // If the timestamp already has a 'Z' or timezone offset, use it directly
  if (utcTimestamp.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(utcTimestamp)) {
    return new Date(utcTimestamp);
  }

  // Otherwise, append 'Z' to treat it as UTC
  // Handle both space and 'T' separators
  const normalizedTimestamp = utcTimestamp.replace(' ', 'T');
  return new Date(normalizedTimestamp + 'Z');
}

/**
 * Formats a UTC timestamp as a localized date and time string
 * @param utcTimestamp - UTC timestamp string
 * @returns Formatted local date and time string
 */
export function formatLocalDateTime(utcTimestamp: string): string {
  return utcToLocal(utcTimestamp).toLocaleString();
}

/**
 * Formats a UTC timestamp as a localized date string
 * @param utcTimestamp - UTC timestamp string
 * @returns Formatted local date string
 */
export function formatLocalDate(utcTimestamp: string): string {
  return utcToLocal(utcTimestamp).toLocaleDateString();
}

/**
 * Formats a UTC timestamp as a localized time string
 * @param utcTimestamp - UTC timestamp string
 * @param options - Intl.DateTimeFormatOptions for time formatting
 * @returns Formatted local time string
 */
export function formatLocalTime(utcTimestamp: string, options?: Intl.DateTimeFormatOptions): string {
  return utcToLocal(utcTimestamp).toLocaleTimeString([], options);
}
