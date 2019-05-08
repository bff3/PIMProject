#1/bin/bash
exec /opt/vc/bin/raspivid -t 0 -w 1280 -h 720 -fps 24 -n -ih -rot 0 -b 1000000 -o - | ncat -lvk4 192.168.4.1 5001
