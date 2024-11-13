#!/bin/bash

save_db_schema() {
    pg_dump -s $PG_URL -x  --no-comments | egrep -v '^(--.*)?$' > schema_dump.sql
}

run () {
    uvicorn --host 0.0.0.0 main:app
}

send_mock_sms() {
    local message=$1
    curl -X POST "http://localhost:8000/sms" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "From=+1234567890&Body=${message}"
}


$@
