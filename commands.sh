#!/bin/bash

save_db_schema() {
    pg_dump -s $PG_URL -x  --no-comments | egrep -v '^(--.*)?$' > schema_dump.sql
}

run () {
    uvicorn --host 0.0.0.0 main:app
}

$@
