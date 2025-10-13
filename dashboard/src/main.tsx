import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Environment variable verification
// These variables are replaced at build time by Vite
const TEST_VARIABLE = import.meta.env.VITE_TEST_VARIABLE;
const API_TOKEN = import.meta.env.VITE_API_TOKEN;
const API_URL = import.meta.env.VITE_API_URL;

console.log('=== Environment Variables Check ===');
console.log('VITE_TEST_VARIABLE:', TEST_VARIABLE || '(not set)');
console.log('VITE_API_TOKEN:', API_TOKEN ? `${API_TOKEN.substring(0, 10)}...` : '(not set)');
console.log('VITE_API_URL:', API_URL || '(not set)');
console.log('Build timestamp:', new Date().toISOString());
console.log('===================================');

// Set test variable as cookie for easy verification
if (TEST_VARIABLE) {
  document.cookie = `test_variable=${TEST_VARIABLE}; path=/; max-age=3600`;
  console.log('✓ Set cookie: test_variable=' + TEST_VARIABLE);
}

// Set API token presence indicator (not the actual token for security)
document.cookie = `api_token_set=${API_TOKEN ? 'yes' : 'no'}; path=/; max-age=3600`;
console.log(`✓ Set cookie: api_token_set=${API_TOKEN ? 'yes' : 'no'}`);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
