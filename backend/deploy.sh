#!/bin/bash
# Railway deployment script

echo "🚂 CS2 Player Stats API - Railway Deployment"
echo "============================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI is not installed."
    echo "📦 Install it with: npm install -g @railway/cli"
    echo "🔗 Or visit: https://docs.railway.app/develop/cli"
    exit 1
fi

echo "✅ Railway CLI found"
echo ""

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please log in to Railway first:"
    echo "   railway login"
    exit 1
fi

echo "✅ Logged in to Railway"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"
echo "📁 Current directory: $(pwd)"
echo ""

# Initialize if not already initialized
if [ ! -f "railway.json" ]; then
    echo "🎯 Initializing Railway project..."
    railway init
    echo ""
fi

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "🔗 Get your domain with: railway domain"
echo "📊 View logs with: railway logs"
echo "⚙️  Manage project at: https://railway.app/dashboard"
echo ""
echo "📚 Your API documentation will be available at:"
echo "   https://your-domain.railway.app/docs"
echo ""
echo "❤️  Health check endpoint:"
echo "   https://your-domain.railway.app/health"