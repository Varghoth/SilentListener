#!/bin/bash

# Ждем, пока VNC полностью запустится
for i in {1..10}; do
    if pgrep Xtightvnc > /dev/null; then
        echo "VNC is running, starting DCA..."
        python3 /app/DCA/agent.py
        exit
    fi
    echo "Waiting for VNC to start..."
    sleep 2
done

echo "VNC did not start in time. Exiting."
exit 1
