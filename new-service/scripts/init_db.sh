#!/usr/bin/env bash

set -e
set -x

echo "🚀 Starting BCP PDF Extractor initialization..."

# Let the DB start
echo "⏳ Waiting for database to be ready..."
python app/backend_pre_start.py

# Create database tables
echo "📋 Creating database tables..."
python -c "
import sys
sys.path.insert(0, 'app')
from src.infrastructure.database.db import create_db_and_tables
create_db_and_tables()
print('✅ Database tables created successfully')
"

# Create initial data in DB
echo "📊 Creating initial data in database..."
python app/init_data.py

echo "✅ BCP PDF Extractor initialization completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "   1. Start the API server: uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"
echo "   2. Check API docs at: http://localhost:8001/docs"
echo "   3. Check database status: GET /api/database/status"
echo ""