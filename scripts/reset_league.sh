#!/bin/bash
# Reset League - Clear all state and start fresh

# Change to project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

echo "🧹 Resetting Agent League System..."

# Stop any running instances (optional)
pkill -f "src.league_manager.main"
pkill -f "src.referee.main"
pkill -f "src.player.main"

# Delete database
if [ -f "./data/league.db" ]; then
    rm -f ./data/league.db ./data/league.db-wal ./data/league.db-shm
    echo "✓ Deleted database files"
else
    echo "ℹ No database found (already clean)"
fi

# Clear logs (optional - comment out if you want to keep logs)
if [ -f "./logs/audit.jsonl" ]; then
    rm -f ./logs/audit.jsonl
    echo "✓ Cleared audit log"
fi

if [ -f "./logs/league_manager.log" ]; then
    rm -f ./logs/league_manager.log
    echo "✓ Cleared application log"
fi

# Clear simulation logs
if ls ./logs/*_sim.log 1> /dev/null 2>&1; then
    rm -f ./logs/*_sim.log
    echo "✓ Cleared simulation logs"
fi

echo ""
echo "✅ League reset complete!"
echo "You can now start the League Manager with:"
echo "   python -m src.league_manager.main --port 8000"
