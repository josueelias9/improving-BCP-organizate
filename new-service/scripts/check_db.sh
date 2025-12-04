#!/usr/bin/env bash

set -e

echo "🔍 Checking BCP PDF Extractor database status..."

# Check database connection and data
python app/check_db.py

echo ""
echo "📊 Database statistics via API..."
curl -s http://localhost:8001/api/database/status | jq '.' || echo "⚠️ API not running or jq not installed"

echo ""
echo "✅ Database check completed!"