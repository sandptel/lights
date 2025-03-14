#!/bin/bash

# Variables
SCRIPT_DIR=$(dirname "$0")            # Directory of the script
CONNECTION_FILE="$SCRIPT_DIR/connection.json"
CACHE_DIR="$HOME/.cache"
CACHE_CONNECTION_FILE="$CACHE_DIR/connection.json"
LOG_FILE="$SCRIPT_DIR/logs.txt"
CACHE_LOG_FILE="$CACHE_DIR/lights_daemon.log"

# Ensure ~/.cache exists
if [ ! -d "$CACHE_DIR" ]; then
    mkdir -p "$CACHE_DIR"
fi

# Start the daemon and log output
echo "Starting Smart Lights Daemon..."
echo "Logs are being written to $LOG_FILE and cached at $CACHE_LOG_FILE"

# Run the Python script and pipe output to the log file
python3 "$SCRIPT_DIR/lights.py" >> "$LOG_FILE" 2>&1 &

# Get the PID of the Python script
DAEMON_PID=$!

# Monitor the connection.json and logs.txt for changes
while kill -0 $DAEMON_PID 2>/dev/null; do
    # Check and sync connection.json
    if [ -f "$CONNECTION_FILE" ]; then
        cp "$CONNECTION_FILE" "$CACHE_CONNECTION_FILE"
    fi

    # Sync the logs to ~/.cache
    cp "$LOG_FILE" "$CACHE_LOG_FILE"
    echo $CACHE_LOG_FILE
    # Sleep before the next sync
    sleep 5
done

# Check exit status
if wait $DAEMON_PID; then
    echo "Smart Lights Daemon stopped successfully."
else
    echo "Smart Lights Daemon encountered an error."
fi

# Final sync of connection.json and logs
if [ -f "$CONNECTION_FILE" ]; then
    cp "$CONNECTION_FILE" "$CACHE_CONNECTION_FILE"
    echo $CACHE_CONNECTION_FILE
fi
cp "$LOG_FILE" "$CACHE_LOG_FILE"

echo "Final logs and connection state have been synced to ~/.cache."
