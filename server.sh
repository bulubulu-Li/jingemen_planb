#!/bin/bash

# Start the server in the background and redirect logs to a file
nohup python RPC/tserver.py > server.log 2>&1 &

# Print a message indicating that the server has started
echo "Server started. Logs are being written to server.log."