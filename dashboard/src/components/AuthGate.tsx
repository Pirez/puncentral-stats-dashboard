import React, { useState, useEffect } from 'react';

const COOKIE_NAME = 'cookiepuns';
const COUNTRY_COOKIE_NAME = 'country_check';
const COOKIE_MAX_AGE = 60 * 60 * 24 * 365; // 365 days in seconds
const COUNTRY_CACHE_MAX_AGE = 60 * 60 * 24; // 24 hours in seconds

function setCookie(name: string, value: string, maxAge: number) {
  document.cookie = `${name}=${value}; max-age=${maxAge}; path=/`;
}

function getCookie(name: string) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
}

export function AuthGate({ children }: { children: React.ReactNode }) {
  const [authed, setAuthed] = useState(() => getCookie(COOKIE_NAME) === '1');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [checkingCountry, setCheckingCountry] = useState(true);
  const [countryAllowed, setCountryAllowed] = useState(false);

  useEffect(() => {
    // Skip country check in development mode
    if (import.meta.env.DEV) {
      setCheckingCountry(false);
      setCountryAllowed(true);
      return;
    }

    // Only check if not already authed
    if (!authed) {
      // Check if we have a cached country result
      const cachedCountryResult = getCookie(COUNTRY_COOKIE_NAME);
      
      if (cachedCountryResult) {
        // Use cached result
        setCountryAllowed(cachedCountryResult === 'allowed');
        setCheckingCountry(false);
      } else {
        // Make API call with retry logic
        const checkCountry = async (retryCount = 0) => {
          try {
            const response = await fetch('https://ipapi.co/json/');
            
            if (response.status === 429) {
              // Rate limited, wait and retry
              if (retryCount < 2) {
                const delay = Math.pow(2, retryCount) * 1000; // Exponential backoff
                setTimeout(() => checkCountry(retryCount + 1), delay);
                return;
              } else {
                // Max retries exceeded, assume allowed for development
                console.warn('Country check rate limited, assuming allowed');
                setCountryAllowed(true);
                setCookie(COUNTRY_COOKIE_NAME, 'allowed', COUNTRY_CACHE_MAX_AGE);
                setCheckingCountry(false);
                return;
              }
            }
            
            const data = await response.json();
            const isAllowed = data && data.country_code === 'NO';
            
            setCountryAllowed(isAllowed);
            setCookie(COUNTRY_COOKIE_NAME, isAllowed ? 'allowed' : 'denied', COUNTRY_CACHE_MAX_AGE);
          } catch (error) {
            console.warn('Country check failed:', error);
            // On error, assume allowed for development
            setCountryAllowed(true);
            setCookie(COUNTRY_COOKIE_NAME, 'allowed', COUNTRY_CACHE_MAX_AGE);
          } finally {
            setCheckingCountry(false);
          }
        };
        
        checkCountry();
      }
    } else {
      setCheckingCountry(false);
      setCountryAllowed(true);
    }
  }, [authed]);

  function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (username === 'test' && password === 'test') {
      setCookie(COOKIE_NAME, '1', COOKIE_MAX_AGE);
      setAuthed(true);
      setError('');
    } else {
      setError('Invalid username or password');
    }
  }

  if (checkingCountry) {
    return (
      <div style={{ minHeight: '100vh', background: '#0f172a', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ border: '4px solid #3b82f6', borderTop: '4px solid transparent', borderRadius: '50%', width: '48px', height: '48px', animation: 'spin 1s linear infinite', margin: '0 auto 16px' }}></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!countryAllowed) {
    return (
      <div style={{ minHeight: '100vh', background: '#0f172a', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center', background: '#1e293b', padding: 32, borderRadius: 8, minWidth: 320, boxShadow: '0 2px 16px #0008' }}>
          <h2 style={{ marginBottom: 16, fontSize: 24 }}><span role="img" aria-label="ban">🚫</span></h2>
          <p>Error code: 403 </p>
        </div>
      </div>
    );
  }

  if (authed) return <>{children}</>;

  return (
    <div style={{ minHeight: '100vh', background: '#0f172a', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <form onSubmit={handleLogin} style={{ background: '#1e293b', padding: 32, borderRadius: 8, minWidth: 320, boxShadow: '0 2px 16px #0008' }}>
        <h2 style={{ marginBottom: 16, fontSize: 24 }}>Login</h2>
        <div style={{ marginBottom: 12 }}>
          <label>Username</label>
          <input value={username} onChange={e => setUsername(e.target.value)} style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #334155', marginTop: 4, background: '#0f172a', color: 'white' }} />
        </div>
        <div style={{ marginBottom: 12 }}>
          <label>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #334155', marginTop: 4, background: '#0f172a', color: 'white' }} />
        </div>
        {error && <div style={{ color: '#ef4444', marginBottom: 12 }}>{error}</div>}
        <button type="submit" style={{ width: '100%', padding: 10, background: '#3b82f6', color: 'white', border: 'none', borderRadius: 4, fontWeight: 600, fontSize: 16 }}>Login</button>
      </form>
    </div>
  );
}
