#!/bin/bash

gosu postgres /usr/lib/postgresql/10/bin/initdb -D /var/lib/postgresql/data > /dev/null;
clear
gosu postgres /usr/lib/postgresql/10/bin/pg_ctl -D /var/lib/postgresql/data/ -l /var/lib/postgresql/data/logfile start;
gosu postgres psql -U postgres -c "CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD' CREATEDB" > /dev/null;
gosu postgres createdb -U $POSTGRES_USER $POSTGRES_DB;
gosu postgres createdb -U $POSTGRES_USER $POSTGRES_USER;
gosu postgres createdb -U $POSTGRES_USER nipo;
echo
echo
echo "
Welcome to Challenge L1A- a part of the nipo tutorial challenge series. For tips, tricks, questions or feedback, reach out to the developer mcflyhalf on his website nyangaga.com or mcflyhalf@live.com. After you get the solution, please do not publish it as it then deprives everyone else of the chance to arrive at it themselves. Enjoy!!!"

echo
echo
echo

exec /bin/bash
