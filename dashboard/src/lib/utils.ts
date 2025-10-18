import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Converts a UTC timestamp string to a Date object in the browser's local timezone
 * @param utcTimestamp - ISO 8601 timestamp string (with or without 'Z' suffix)
 * @returns Date object representing the timestamp in browser's timezone
 */
export function utcToLocal(utcTimestamp: string): Date {
  // If the timestamp doesn't have a timezone indicator, treat it as UTC
  if (!utcTimestamp.includes('Z') && !utcTimestamp.includes('+') && !utcTimestamp.includes('-', 10)) {
    // Normalize the format and append 'Z' to mark as UTC
    const normalized = utcTimestamp.replace(' ', 'T');
    return new Date(normalized + 'Z');
  }
  return new Date(utcTimestamp);
}

/**
 * Formats a UTC timestamp as a localized date and time string in browser's timezone
 * @param utcTimestamp - ISO 8601 timestamp string
 * @returns Formatted date and time string (e.g., "12/31/2024, 3:45 PM")
 */
export function formatLocalDateTime(utcTimestamp: string): string {
  const date = utcToLocal(utcTimestamp);
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  });
}

/**
 * Formats a UTC timestamp as a localized date string in browser's timezone
 * @param utcTimestamp - ISO 8601 timestamp string
 * @returns Formatted date string (e.g., "12/31/2024")
 */
export function formatLocalDate(utcTimestamp: string): string {
  const date = utcToLocal(utcTimestamp);
  return date.toLocaleDateString();
}

/**
 * Formats a UTC timestamp as a localized time string in browser's timezone
 * @param utcTimestamp - ISO 8601 timestamp string
 * @param options - Intl.DateTimeFormatOptions for time formatting
 * @returns Formatted time string (e.g., "3:45 PM")
 */
export function formatLocalTime(utcTimestamp: string, options?: Intl.DateTimeFormatOptions): string {
  const date = utcToLocal(utcTimestamp);
  return date.toLocaleTimeString(undefined, options);
}

/**
 * Formats a UTC timestamp for display in charts - short date and time
 * @param utcTimestamp - ISO 8601 timestamp string
 * @returns Formatted string suitable for chart labels (e.g., "12/31/24 3:45 PM")
 */
export function formatChartDateTime(utcTimestamp: string): string {
  const date = utcToLocal(utcTimestamp);
  const dateStr = date.toLocaleDateString(undefined, {
    month: 'numeric',
    day: 'numeric',
    year: '2-digit'
  });
  const timeStr = date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  });
  return `${dateStr} ${timeStr}`;
}
