import { useEffect, useState } from 'react';

export function ThemeToggle() {
  const [theme, setTheme] = useState(() => {
    // Check localStorage first for saved preference
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem('theme-preference');
      if (savedTheme === 'dark' || savedTheme === 'light') {
        return savedTheme;
      }
      // Fallback to system preference if no saved preference
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
    localStorage.setItem('theme-preference', theme);
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
