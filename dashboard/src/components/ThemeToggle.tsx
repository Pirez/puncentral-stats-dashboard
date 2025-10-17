import { useEffect, useState } from 'react';

const THEME_STORAGE_KEY = 'theme-preference';

export function ThemeToggle() {
  const [theme, setTheme] = useState(() => {
    // Check localStorage first for saved preference
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
      if (savedTheme === 'dark' || savedTheme === 'light') {
        return savedTheme;
      }
      // Fall back to system preference
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
      }
    }
    return 'light';
  });

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    // Save theme preference to localStorage
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  return (
    <button
      className="px-3 py-1 rounded border border-border bg-card text-foreground hover:bg-muted transition"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      aria-label="Toggle dark/light mode"
      style={{ float: 'right' }}
    >
      {theme === 'dark' ? '🌙 Dark' : '☀️ Light'}
    </button>
  );
}
