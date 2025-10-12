#!/bin/bash
# Local development script

echo "🚀 Starting CS2 Player Stats API locally..."
echo "📋 Installing dependencies..."
pip install -r requirements.txt

echo "🔄 Starting server..."
echo "🌐 API will be available at: http://localhost:8000"
echo "📚 API documentation at: http://localhost:8000/docs"
echo "❤️  Health check at: http://localhost:8000/health"
echo ""

python api_server.py