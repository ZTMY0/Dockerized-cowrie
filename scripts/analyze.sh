#!/bin/bash

echo "🔍 Scanning Docker for Cowrie..."

# 1. Find the container ID (looks for any image name containing 'cowrie')
CONTAINER_ID=$(docker ps | grep -i cowrie | awk '{print $1}' | head -n 1)

if [ -z "$CONTAINER_ID" ]; then
    echo "❌ ERROR: No running Docker container found with 'cowrie' in the name."
    echo "   Run 'docker ps' to check if it's actually running."
    exit 1
fi

echo "✅ Found Cowrie Container: $CONTAINER_ID"

# 2. Define common paths where Cowrie hides logs
LOG_PATHS=(
    "/cowrie/cowrie-git/var/log/cowrie/cowrie.json"
    "/srv/cowrie/var/log/cowrie/cowrie.json"
    "/var/log/cowrie/cowrie.json"
    "/home/cowrie/cowrie-git/var/log/cowrie/cowrie.json"
)

FOUND=0

# 3. Loop through paths to find the JSON file
for PATH_CHECK in "${LOG_PATHS[@]}"; do
    if docker exec "$CONTAINER_ID" [ -f "$PATH_CHECK" ]; then
        echo "🎉 SUCCESS! Found cowrie.json at: $PATH_CHECK"
        echo "   File Size: $(docker exec "$CONTAINER_ID" du -h "$PATH_CHECK" | awk '{print $1}')"
        echo ""
        echo "--- DATA PREVIEW (First 1 Line) ---"
        docker exec "$CONTAINER_ID" head -n 1 "$PATH_CHECK"
        echo ""
        echo "-----------------------------------"
        FOUND=1
        
        # Save the path for the user
        echo "To copy this file to your current folder, run:"
        echo "docker cp $CONTAINER_ID:$PATH_CHECK ./cowrie.json"
        break
    fi
done

# 4. If JSON failed, check for standard .log file
if [ $FOUND -eq 0 ]; then
    echo "⚠️  Could not find 'cowrie.json'. Checking for 'cowrie.log' (text format)..."
    if docker exec "$CONTAINER_ID" [ -f "/cowrie/cowrie-git/var/log/cowrie/cowrie.log" ]; then
        echo "⚠️  Found 'cowrie.log' (Standard Text Log)." 
        echo "   This means JSON logging is disabled in cowrie.cfg."
    else
        echo "❌ No logs found. Your volume mapping might be hiding them, or logging is broken."
    fi
fi
