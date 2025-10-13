# 🎮 Puncentral CS2 Stats Dashboard

A modern, full-stack web application for tracking and visualizing Counter-Strike 2 player statistics.

![Dashboard Preview](https://img.shields.io/badge/React-18.3-61DAFB?logo=react)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript)
![Railway](https://img.shields.io/badge/Deployed%20on-Railway-0B0D0E?logo=railway)

## ✨ Features

### 📊 Dashboard
- **Player Leaderboard** with points-based ranking system
- **K/D Ratio Charts** with trend visualization
- **Map Win Rates** analysis
- **Last Match Summary** with detailed stats
- **Dark Theme** with custom Tailwind CSS styling
- **Player Avatars** and custom player colors
- **Authentication Gate** for secure access
- **Theme Toggle** for light/dark mode
- **Rate Limiting** with intelligent caching (50 req/min per endpoint)

### 🚀 Backend API
- **FastAPI** RESTful API with automatic documentation
- **SQLite Database** with Railway persistent volumes
- **API Token Authentication** with Bearer token support
- **Rate Limiting** (100 req/min per IP)
- **IP Geolocation** verification (Norwegian IPs only)
- **Smart Caching** for geolocation lookups
- **CORS Configuration** for cross-origin requests
- **Health Checks** for monitoring
- **Comprehensive Endpoints** for all stats

## 🏗️ Tech Stack

### Frontend
- **React 18.3** with TypeScript
- **Vite** for blazing-fast builds
- **Tailwind CSS** for styling
- **Recharts** for data visualization
- **Axios** for API requests

### Backend
- **FastAPI** (Python 3.11+)
- **SQLite** with persistent storage
- **Pandas** for data processing
- **SlowAPI** for rate limiting
- **Uvicorn** ASGI server

### Deployment
- **Railway** for hosting both services
- **Docker** multi-stage builds
- **GitHub Actions** ready (CI/CD)

## 📁 Project Structure

```
cs2/
├── backend/                 # FastAPI backend
│   ├── api_server.py       # Main API application
│   ├── requirements.txt    # Python dependencies
│   ├── railway.toml        # Railway config
│   └── player_stats.db     # SQLite database
│
├── dashboard/              # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   ├── types/          # TypeScript types
│   │   └── utils/          # Utility functions
│   ├── Dockerfile          # Production build
│   ├── package.json        # Node dependencies
│   └── vite.config.ts      # Vite configuration
│
├── DEPLOYMENT_GUIDE.md     # Full deployment guide
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- Python 3.11+
- npm or yarn

### Local Development

#### 1. Clone the repository
```bash
git clone git@github.com:Pirez/puncentral-stats-dashboard.git
cd puncentral-stats-dashboard
```

#### 2. Start the Backend
```bash
cd backend
pip3 install -r requirements.txt
python3 api_server.py
```
Backend runs on `http://localhost:8000`

#### 3. Start the Dashboard
```bash
cd dashboard
npm install
cp .env.example .env
# Edit .env and set VITE_API_URL=http://localhost:8000
npm run dev
```
Dashboard runs on `http://localhost:5173`

## 🌐 Railway Deployment

See the comprehensive [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for step-by-step instructions.

### Quick Deploy
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Deploy from GitHub: `Pirez/puncentral-stats-dashboard`
3. Deploy backend service (root: `backend`)
4. Deploy dashboard service (root: `dashboard`)
5. Set environment variables:
   - Dashboard: `VITE_API_URL=<backend-url>`
   - Backend: `ALLOWED_ORIGINS=<dashboard-url>`

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API docs |
| `/api/player-stats` | GET | All player statistics |
| `/api/kd-ratios` | GET | K/D ratios |
| `/api/kd-over-time` | GET | K/D trends over time |
| `/api/map-stats` | GET | Map statistics |
| `/api/map-win-rates` | GET | Map win rates |
| `/api/multi-kills` | GET | Multi-kill statistics |
| `/api/utility-damage` | GET | Utility damage stats |
| `/api/last-match` | GET | Most recent match data |

Full API documentation available at `/docs` endpoint.

## 🎨 Features in Detail

### Points-Based Leaderboard
Players earn points across multiple categories:
- K/D Ratio
- Headshot %
- Accuracy %
- Total Kills
- Total Deaths
- Multi-kills
- Utility Damage

**Scoring**: 5 points for 1st place, 4 for 2nd, down to 1 point for 5th

### Rate Limiting
- **Backend**: 100 requests/minute per IP
- **Frontend**: 50 requests/minute per endpoint
- **Caching**: 30-second client-side cache
- **Fallback**: Stale cache when rate limited

### Dark Theme
Custom dark theme with:
- Cyberpunk-inspired color palette
- Smooth transitions
- High contrast for readability
- Custom player colors for charts

### Authentication
Optional password protection with AuthGate component.

## 🔧 Configuration

### Environment Variables

#### Backend (`.env` or Railway Variables)
```bash
API_TOKEN=your-secure-token-here  # Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'
API_TOKEN_ENABLED=true  # Enable API token authentication
ALLOWED_ORIGINS=https://your-dashboard.railway.app,http://localhost:5173
GEOLOCATION_ENABLED=true  # Enable IP geolocation verification
PORT=8000  # Auto-set by Railway
```

#### Dashboard (`.env`)
```bash
VITE_API_URL=https://your-backend.railway.app
VITE_API_TOKEN=your-secure-token-here  # Must match backend API_TOKEN
VITE_AUTH_PASSWORD=your-password  # Optional
```

## 📊 Database Schema

SQLite database with tables:
- `player_stats` - Overall player statistics
- `map_stats` - Per-map statistics
- `kd_over_time` - K/D ratio trends
- `multi_kills` - Multi-kill events
- `utility_damage` - Utility damage tracking

## 🐛 Troubleshooting

### CORS Errors
```bash
# Set ALLOWED_ORIGINS in backend Railway variables
ALLOWED_ORIGINS=https://your-dashboard.railway.app
```

### Dashboard Can't Connect
1. Check backend health: `curl <backend-url>/health`
2. Verify `VITE_API_URL` is set correctly
3. Rebuild dashboard after changing env vars

### Build Failures
- Check Railway logs: `railway logs`
- Ensure all dependencies are in `package.json`/`requirements.txt`
- Verify root directory is set correctly in Railway

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for more troubleshooting.

## 📈 Performance

- **Build Time**: ~2-3 minutes on Railway
- **Bundle Size**: ~500KB (gzipped)
- **First Load**: <2s
- **Rate Limiting**: Prevents API abuse
- **Client-Side Caching**: Reduces backend load

## 🔐 Security

- ✅ API token authentication with Bearer tokens
- ✅ Timing attack protection (constant-time comparison)
- ✅ Rate limiting on frontend and backend
- ✅ IP geolocation verification (Norwegian IPs only)
- ✅ Smart caching to prevent API abuse
- ✅ CORS configuration
- ✅ Environment variable protection
- ✅ Optional authentication
- ✅ HTTPS on Railway (automatic)
- ✅ No sensitive data in repository

## 📚 Documentation

- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Full deployment instructions
- [backend/API_TOKEN_AUTH_README.md](./backend/API_TOKEN_AUTH_README.md) - API token authentication
- [backend/IP_GEOLOCATION_README.md](./backend/IP_GEOLOCATION_README.md) - IP geolocation feature
- [backend/DEPLOYMENT.md](./backend/DEPLOYMENT.md) - Backend-specific deployment
- [dashboard/RAILWAY_DEPLOYMENT.md](./dashboard/RAILWAY_DEPLOYMENT.md) - Dashboard deployment
- [backend/PERSISTENT_STORAGE.md](./backend/PERSISTENT_STORAGE.md) - Database persistence

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is for personal use. Contact the author for licensing inquiries.

## 👥 Authors

- **Johan** - Initial work

## 🙏 Acknowledgments

- Built with [Claude Code](https://claude.com/claude-code)
- Deployed on [Railway](https://railway.app)
- Icons from [Lucide Icons](https://lucide.dev)

## 📞 Support

For issues or questions:
- Check the [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- Review [troubleshooting](#-troubleshooting) section
- Open a GitHub issue

---

**Live Demo**: [Coming Soon]

**Repository**: https://github.com/Pirez/puncentral-stats-dashboard

Made with ❤️ for the Puncentral community
