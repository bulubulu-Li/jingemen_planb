#!/bin/bash

# 用ps和grep命令找到RPC/tserver.py的进程ID
pid=$(ps -ef | grep "HTTP/main_server.py" | grep -v grep | awk '{print $2}')

# 如果找到了进程ID，就用kill命令杀掉它
if [ -n "$pid" ]; then
  kill -9 $pid
  echo "已经杀掉了HTTP/main_server.py的进程"
else
  echo "没有找到HTTP/main_server.py的进程"
fi

pid=$(ps -ef | grep "/qabot/bin/python" | grep -v grep | awk '{print $2}')

# 如果找到了进程ID，就用kill命令杀掉它
if [ -n "$pid" ]; then
  kill -9 $pid
  echo "已经杀掉了/qabot/bin/python子进程"
else
  echo "没有找到/qabot/bin/python子进程"
fi

# 先清空server.log文件
echo "" > serverHttp.log
# Start the server in the background and redirect logs to a file
nohup python HTTP/main_server.py >> serverHttp.log 2>&1 &

# Print a message indicating that the server has started
echo "HTTP Server started. Logs are being written to serverHttp.log."