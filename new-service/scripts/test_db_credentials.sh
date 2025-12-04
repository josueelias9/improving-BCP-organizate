#!/usr/bin/env bash

echo "🔍 Testing PostgreSQL connection with different credentials..."

# Common credential combinations to test
declare -a CREDENTIALS=(
    "postgres:postgres"
    "postgres:password"
    "postgres:"
    "root:root"
    "admin:admin"
    "postgres:postgres123"
    "postgres:secret"
)

for cred in "${CREDENTIALS[@]}"; do
    IFS=':' read -r user pass <<< "$cred"
    echo "Testing user='$user' password='$pass'"
    
    if [ -z "$pass" ]; then
        # Test with no password
        PGPASSWORD="" psql -h postgres -p 5432 -U "$user" -d postgres -c "SELECT 1;" 2>/dev/null
    else
        # Test with password
        PGPASSWORD="$pass" psql -h postgres -p 5432 -U "$user" -d postgres -c "SELECT 1;" 2>/dev/null
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ SUCCESS: user='$user' password='$pass'"
        echo ""
        echo "Update your .env file with:"
        echo "POSTGRES_USER=$user"
        echo "POSTGRES_PASSWORD=$pass"
        exit 0
    else
        echo "❌ Failed: user='$user' password='$pass'"
    fi
    echo ""
done

echo "❌ None of the common credentials worked."
echo "You may need to check the PostgreSQL container configuration."