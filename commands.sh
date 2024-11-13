#!/bin/bash

save_db_schema() {
    pg_dump -s $PG_URL -x  --no-comments | egrep -v '^(--.*)?$' > schema_dump.sql
}

run () {
    uvicorn --host 0.0.0.0 smartypants.main:app
}

send_mock_sms() {
    local message="$*"
    curl -X POST "http://localhost:8000/smartypants/sms" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "From=+1234567890" \
        --data-urlencode "Body=${message}"
}


$@
