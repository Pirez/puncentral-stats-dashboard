// Frontend rate limiting and caching utility

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

interface RateLimitEntry {
  count: number;
  resetTime: number;
}

class RateLimiter {
  private cache: Map<string, CacheEntry<any>> = new Map();
  private rateLimits: Map<string, RateLimitEntry> = new Map();
  private readonly cacheDuration: number = 30000; // 30 seconds cache
  private readonly maxRequestsPerMinute: number = 50;
  private readonly rateLimitWindow: number = 60000; // 1 minute

  /**
   * Check if a request should be allowed based on rate limiting
   */
  private isRateLimited(endpoint: string): boolean {
    const now = Date.now();
    const limit = this.rateLimits.get(endpoint);

    if (!limit || now > limit.resetTime) {
      // Reset or initialize rate limit
      this.rateLimits.set(endpoint, {
        count: 1,
        resetTime: now + this.rateLimitWindow,
      });
      return false;
    }

    if (limit.count >= this.maxRequestsPerMinute) {
      console.warn(`Rate limit exceeded for ${endpoint}. Try again in ${Math.ceil((limit.resetTime - now) / 1000)}s`);
      return true;
    }

    limit.count++;
    return false;
  }

  /**
   * Get cached data if available and not expired
   */
  private getCachedData<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    const now = Date.now();
    if (now - cached.timestamp > this.cacheDuration) {
      this.cache.delete(key);
      return null;
    }

    console.log(`Using cached data for ${key}`);
    return cached.data as T;
  }

  /**
   * Cache data for future use
   */
  private setCachedData<T>(key: string, data: T): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  /**
   * Execute a request with rate limiting and caching
   */
  async execute<T>(
    key: string,
    requestFn: () => Promise<T>,
    options: {
      skipCache?: boolean;
      cacheDuration?: number;
    } = {}
  ): Promise<T> {
    // Check cache first (unless skipCache is true)
    if (!options.skipCache) {
      const cached = this.getCachedData<T>(key);
      if (cached !== null) {
        return cached;
      }
    }

    // Check rate limit
    if (this.isRateLimited(key)) {
      // Return cached data even if expired, rather than making request
      const cached = this.cache.get(key);
      if (cached) {
        console.warn(`Rate limited - returning stale cache for ${key}`);
        return cached.data as T;
      }
      throw new Error(`Rate limit exceeded for ${key}. Please try again later.`);
    }

    // Execute request
    try {
      const data = await requestFn();
      this.setCachedData(key, data);
      return data;
    } catch (error) {
      // If request fails, try returning cached data
      const cached = this.cache.get(key);
      if (cached) {
        console.warn(`Request failed - returning stale cache for ${key}`);
        return cached.data as T;
      }
      throw error;
    }
  }

  /**
   * Clear cache for a specific key or all keys
   */
  clearCache(key?: string): void {
    if (key) {
      this.cache.delete(key);
    } else {
      this.cache.clear();
    }
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    };
  }
}

// Export singleton instance
export const rateLimiter = new RateLimiter();
