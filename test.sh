python3 src/server.py --source 127.0.0.1:5406 --target 127.0.0.1:5404 --verbose &
server_pid=$!
sleep 1
python3 src/proxy.py --source 127.0.0.1:5405 --target 127.0.0.1:5406 --delay 0.1 0.5 --loss 0.1 --verbose &
proxy_pid=$!
sleep 1

trap "kill $server_pid; kill $proxy_pid" INT

python3 src/client.py --source 127.0.0.1:5404 --target 127.0.0.1:5405 --verbose

kill $server_pid
kill $proxy_pid

