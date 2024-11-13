import uuid
from smartypants.db import get_db_connection, q_one


def apply_gift(unique_id, disappointment, feedback):
    with get_db_connection() as conn, conn.cursor() as cursor:
        offer = q_one(cursor, 'SELECT tel, is_used FROM purchase_offers WHERE unique_id = %s', unique_id)
        if offer.is_used:
            raise ValueError("This offer has already been used")
        cursor.execute('''INSERT INTO purchases (tel, purchase_date, purchase_type, message_count) VALUES
            (%(tel)s, current_timestamp, 'promotion', 100)''', {"tel": offer.tel})
        cursor.execute('UPDATE purchase_offers SET is_used = TRUE WHERE unique_id = %s', [unique_id])
        cursor.execute('''INSERT INTO survey_responses (tel, disappointment, feedback) VALUES
            (%(tel)s, %(disappointment)s, %(feedback)s)''', 
            {"tel": offer.tel, "disappointment": disappointment, "feedback": feedback})


def create_gift_offer(tel):
    unique_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''INSERT INTO purchase_offers (unique_id, tel) VALUES (%s, %s)''', (unique_id, tel))
    return f"https://smartypants.onrender.com/smartypants/purchase/{unique_id}"


def check_message_limit(tel):
    with get_db_connection() as conn, conn.cursor() as cursor:
        message_count = q_one(cursor, 'SELECT COUNT(*) as c FROM messages WHERE tel = %s', tel).c
        purchase_count = q_one(cursor, 'SELECT COALESCE(SUM(message_count), 0) as c FROM purchases WHERE tel = %s', tel).c
        if message_count > purchase_count + 50:
            return True
    return False


def record_new_message(tel, body, completion):
    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute('''insert into messages (tel, is_user, sent, body) values
            (%(tel)s, true, current_timestamp, %(body)s),
            (%(tel)s, false, current_timestamp + interval '1 second', %(completion)s)''', {"tel":tel, "body":body, "completion":completion})
