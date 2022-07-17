#!/usr/bin/env bash

# wait for postgress to start
until /usr/bin/env python pg_ping.py 2>&1 >/dev/null; do
	echo 'wait for postgres to start...'
	sleep 5
done

if [ ! -f "resetdb.txt" ]; then
    otree resetdb --noinput && echo "resetdb=TRUE" > resetdb.txt
fi

otree prodserver