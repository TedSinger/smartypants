import uuid
from db import get_db_connection
from twilio.twiml.messaging_response import MessagingResponse

def apply_gift(unique_id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''INSERT INTO purchases (tel, purchase_date, purchase_type, message_count) VALUES
                (%(tel)s, current_timestamp, 'promotion', 100)''', {"tel": tel})

def create_gift_offer(tel):
    unique_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''INSERT INTO purchase_offers (unique_id, tel) VALUES (%s, %s)''', (unique_id, tel))
    return f"https://smartypants.onrender.com/smartypants/purchase/{unique_id}"

def check_message_limit(tel):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM messages WHERE tel = %s', [tel])
            message_count = cursor.fetchone()[0]
            cursor.execute('SELECT COALESCE(SUM(message_count), 0) FROM purchases WHERE tel = %s', [tel])
            purchase_count = cursor.fetchone()[0]
            if message_count > purchase_count + 50:
                return True
    return False

def record_new_message(tel, body, completion):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''insert into messages (tel, is_user, sent, body) values
                (%(tel)s, true, current_timestamp, %(body)s),
                (%(tel)s, false, current_timestamp + interval '1 second', %(completion)s)''', {"tel":tel, "body":body, "completion":completion})
