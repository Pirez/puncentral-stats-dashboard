import { useEffect, useState } from 'react';

type Theme = 'dark' | 'light';

const getStoredTheme = (): Theme | null => {
  try {
    const stored = localStorage.getItem('theme-preference');
    if (stored === 'dark' || stored === 'light') return stored;
  } catch (error) {
    console.warn('Failed to read theme from localStorage:', error);
  }
  return null;
};

const saveTheme = (theme: Theme): void => {
  try {
    localStorage.setItem('theme-preference', theme);
  } catch (error) {
    console.warn('Failed to save theme to localStorage:', error);
  }
};

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(() => {
    // Check localStorage first
    if (typeof window !== 'undefined') {
      const savedTheme = getStoredTheme();
      if (savedTheme) {
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
  }, [theme]);

  const handleToggle = () => {
    const newTheme: Theme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    saveTheme(newTheme);
  };

  return (
    <button
      className="px-3 py-1 rounded border border-border bg-card text-foreground hover:bg-muted transition"
      onClick={handleToggle}
      aria-label="Toggle dark/light mode"
      style={{ float: 'right' }}
    >
      {theme === 'dark' ? '🌙 Dark' : '☀️ Light'}
    </button>
  );
}
