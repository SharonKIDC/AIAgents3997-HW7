#!/bin/bash
# Agent League System - Complete Simulation
# This script demonstrates the full league workflow

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
LEAGUE_MANAGER_PORT=8000
REFEREE1_PORT=8001
REFEREE2_PORT=8002
PLAYER_START_PORT=9001

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🛑 Cleaning up processes...${NC}"
    pkill -f "src.league_manager.main" 2>/dev/null || true
    pkill -f "src.referee.main" 2>/dev/null || true
    pkill -f "src.player.main" 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}✓ Processes stopped${NC}"

    # Reset league state
    echo -e "\n${YELLOW}🧹 Resetting league state...${NC}"
    ./reset_league.sh
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Agent League System - Live Simulation       ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo ""

# Step 1: Start League Manager
echo -e "${GREEN}[1/5] Starting League Manager on port ${LEAGUE_MANAGER_PORT}...${NC}"
python -m src.league_manager.main --port ${LEAGUE_MANAGER_PORT} > ./logs/league_manager_sim.log 2>&1 &
LEAGUE_PID=$!
sleep 2

# Check if League Manager started
if ! curl -s http://localhost:${LEAGUE_MANAGER_PORT}/health > /dev/null 2>&1; then
    echo -e "${RED}✗ League Manager failed to start${NC}"
    exit 1
fi
echo -e "${GREEN}✓ League Manager running (PID: ${LEAGUE_PID})${NC}"

# Step 2: Start Referees
echo -e "\n${GREEN}[2/5] Starting Referees...${NC}"

python -m src.referee.main referee1 --port ${REFEREE1_PORT} --league-manager-url http://localhost:${LEAGUE_MANAGER_PORT}/mcp > ./logs/referee1_sim.log 2>&1 &
REF1_PID=$!
sleep 1

python -m src.referee.main referee2 --port ${REFEREE2_PORT} --league-manager-url http://localhost:${LEAGUE_MANAGER_PORT}/mcp > ./logs/referee2_sim.log 2>&1 &
REF2_PID=$!
sleep 1

echo -e "${GREEN}✓ Referee 1 running (PID: ${REF1_PID})${NC}"
echo -e "${GREEN}✓ Referee 2 running (PID: ${REF2_PID})${NC}"

# Step 3: Start Players
echo -e "\n${GREEN}[3/5] Starting Players...${NC}"

# Define players: name, strategy
declare -a PLAYERS=(
    "alice:smart"
    "bob:smart"
    "charlie:random"
    "dave:random"
    "eve:smart"
    "frank:random"
    "grace:smart"
    "hank:random"
    "iris:smart"
    "jack:random"
    "kate:smart"
    "leo:random"
    "maya:smart"
    "nick:random"
)

PLAYER_PIDS=()
PORT=${PLAYER_START_PORT}

for player_info in "${PLAYERS[@]}"; do
    PLAYER_NAME=$(echo $player_info | cut -d':' -f1)
    STRATEGY=$(echo $player_info | cut -d':' -f2)

    python -m src.player.main ${PLAYER_NAME} --port ${PORT} --league-manager-url http://localhost:${LEAGUE_MANAGER_PORT}/mcp --strategy ${STRATEGY} > ./logs/${PLAYER_NAME}_sim.log 2>&1 &
    PID=$!
    PLAYER_PIDS+=($PID)
    echo -e "${GREEN}✓ ${PLAYER_NAME^} running (${STRATEGY} strategy, PID: ${PID})${NC}"

    PORT=$((PORT + 1))
    sleep 0.5
done

# Step 4: Check League Status
echo -e "\n${GREEN}[4/5] Checking League Status...${NC}"
sleep 2

STATUS=$(curl -s http://localhost:${LEAGUE_MANAGER_PORT}/status)
echo -e "${BLUE}League Status:${NC}"
echo "$STATUS" | python3 -m json.tool 2>/dev/null || echo "$STATUS"

# Step 5: Display Current State
echo -e "\n${GREEN}[5/5] Current League State${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

# Parse status
LEAGUE_STATUS=$(echo "$STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")
REFEREE_COUNT=$(echo "$STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('referees', 0))" 2>/dev/null || echo "0")
PLAYER_COUNT=$(echo "$STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('players', 0))" 2>/dev/null || echo "0")

echo -e "Status:    ${YELLOW}${LEAGUE_STATUS}${NC}"
echo -e "Referees:  ${GREEN}${REFEREE_COUNT}${NC}"
echo -e "Players:   ${GREEN}${PLAYER_COUNT}${NC}"

echo -e "\n${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Simulation Setup Complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

echo -e "\n${YELLOW}📊 League is now in ${LEAGUE_STATUS} state${NC}"

# Step 6: Start the League
if [ "$LEAGUE_STATUS" = "REGISTRATION" ]; then
    echo -e "\n${GREEN}[6/6] Starting the League...${NC}"
    sleep 2

    START_RESPONSE=$(curl -s -X POST http://localhost:${LEAGUE_MANAGER_PORT}/mcp \
      -H "Content-Type: application/json" \
      -d '{
        "jsonrpc": "2.0",
        "method": "league.handle",
        "params": {
          "envelope": {
            "protocol": "league.v2",
            "message_type": "ADMIN_START_LEAGUE_REQUEST",
            "sender": "admin",
            "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
            "conversation_id": "'$(uuidgen)'"
          },
          "payload": {}
        },
        "id": "start-1"
      }')

    echo -e "${BLUE}Start League Response:${NC}"
    echo "$START_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$START_RESPONSE"

    # Check if successful
    if echo "$START_RESPONSE" | grep -q '"league_status": "ACTIVE"'; then
        echo -e "${GREEN}✓ League started successfully!${NC}"
        LEAGUE_STATUS="ACTIVE"
    else
        echo -e "${YELLOW}⚠️  League start may have failed. Check response above.${NC}"
    fi
fi

echo -e "\n${BLUE}Available Commands:${NC}"
echo -e "  • Check status:    ${GREEN}curl http://localhost:${LEAGUE_MANAGER_PORT}/status${NC}"
echo -e "  • View health:     ${GREEN}curl http://localhost:${LEAGUE_MANAGER_PORT}/health${NC}"
echo -e "  • View audit log:  ${GREEN}tail -f ./logs/audit.jsonl${NC}"
echo -e "  • View database:   ${GREEN}sqlite3 ./data/league.db${NC}"

echo -e "\n${BLUE}Process IDs:${NC}"
echo -e "  League Manager: ${LEAGUE_PID}"
echo -e "  Referees:       ${REF1_PID}, ${REF2_PID}"
echo -e "  Players (${#PLAYER_PIDS[@]}):    ${PLAYER_PIDS[*]}"

echo -e "\n${YELLOW}Press Ctrl+C to stop all processes and cleanup${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}\n"

# Monitor league progress
LAST_STATUS=""
MONITOR_INTERVAL=5
PREV_COMPLETED=0

echo -e "${BLUE}📊 Monitoring league progress (updates every ${MONITOR_INTERVAL}s)...${NC}\n"

while true; do
    sleep ${MONITOR_INTERVAL}

    # Check if League Manager is still running
    if ! kill -0 ${LEAGUE_PID} 2>/dev/null; then
        echo -e "${RED}✗ League Manager stopped unexpectedly${NC}"
        exit 1
    fi

    # Check league status
    CURRENT_STATUS=$(curl -s http://localhost:${LEAGUE_MANAGER_PORT}/status 2>/dev/null)
    if [ -n "$CURRENT_STATUS" ]; then
        LEAGUE_STATE=$(echo "$CURRENT_STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")

        # Check match progress from database
        if [ -f "./data/league.db" ]; then
            MATCH_INFO=$(python3 << 'PYEOF'
import sqlite3
try:
    conn = sqlite3.connect('./data/league.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM matches")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM matches WHERE status = 'COMPLETED'")
    completed = cursor.fetchone()[0]
    conn.close()
    print(f"{total}|{completed}")
except:
    print("0|0")
PYEOF
)
            TOTAL_MATCHES=$(echo "$MATCH_INFO" | cut -d'|' -f1)
            COMPLETED_MATCHES=$(echo "$MATCH_INFO" | cut -d'|' -f2)

            # Show match progress when matches complete
            if [ "$COMPLETED_MATCHES" -gt "$PREV_COMPLETED" ]; then
                TIMESTAMP=$(date '+%H:%M:%S')
                echo -e "${TIMESTAMP} ${BLUE}📊 Match Progress: ${COMPLETED_MATCHES}/${TOTAL_MATCHES} completed${NC}"
                PREV_COMPLETED=$COMPLETED_MATCHES
            fi
        fi

        # Print status changes
        if [ "$LEAGUE_STATE" != "$LAST_STATUS" ]; then
            TIMESTAMP=$(date '+%H:%M:%S')
            case "$LEAGUE_STATE" in
                "REGISTRATION")
                    echo -e "${TIMESTAMP} ${YELLOW}⏳ League Status: REGISTRATION${NC}"
                    ;;
                "SCHEDULING")
                    echo -e "${TIMESTAMP} ${BLUE}📅 League Status: SCHEDULING${NC}"
                    ;;
                "ACTIVE")
                    echo -e "${TIMESTAMP} ${GREEN}▶️  League Status: ACTIVE - Starting matches${NC}"
                    if [ -n "$TOTAL_MATCHES" ] && [ "$TOTAL_MATCHES" -gt 0 ]; then
                        echo -e "${TIMESTAMP} ${BLUE}📋 Total matches scheduled: ${TOTAL_MATCHES}${NC}"
                    fi
                    ;;
                "COMPLETED")
                    echo -e "${TIMESTAMP} ${GREEN}✅ League Status: COMPLETED${NC}"

                    # Show final results
                    if [ -f "./data/league.db" ]; then
                        echo -e "\n${BLUE}═══════════════════════════════════════════${NC}"
                        echo -e "${GREEN}Final Results:${NC}"
                        echo -e "${BLUE}═══════════════════════════════════════════${NC}"
                        python3 << 'PYEOF'
import sqlite3
conn = sqlite3.connect('./data/league.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM matches WHERE status = 'COMPLETED'")
completed = cursor.fetchone()[0]
print(f"✅ Matches completed: {completed}")

cursor.execute("""
    SELECT pr.rank, pr.player_id, pr.points, pr.wins, pr.draws, pr.losses
    FROM player_rankings pr
    JOIN standings_snapshots ss ON pr.snapshot_id = ss.snapshot_id
    ORDER BY ss.computed_at DESC, pr.rank
    LIMIT 4
""")

print("\n🏆 Final Standings:")
print("-" * 43)
print(f"{'Rank':<6} {'Player':<10} {'Points':<8} {'Record':<15}")
print("-" * 43)
for row in cursor.fetchall():
    rank, player, points, wins, draws, losses = row
    record = f"{wins}W-{draws}D-{losses}L"
    print(f"{rank:<6} {player:<10} {points:<8} {record:<15}")

conn.close()
PYEOF
                        echo -e "${BLUE}═══════════════════════════════════════════${NC}"
                    fi

                    echo -e "\n${GREEN}✅ Simulation completed successfully!${NC}"
                    echo -e "\n${YELLOW}Press Enter to cleanup and exit, or Ctrl+C to exit now...${NC}"
                    read
                    exit 0
                    ;;
            esac
            LAST_STATUS="$LEAGUE_STATE"
        fi
    fi
done
