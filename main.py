from fasthtml.common import fast_app, serve, Html, Head, Title, Body, H1, P
from smartypants.answer import load_past_messages, complete
from smartypants.pay import record_new_message, generate_purchase_url
from db import get_db_connection
from twilio.twiml.messaging_response import MessagingResponse

app, rt = fast_app()

@app.post("/smartypants/sms")
def answer_text_message(From:str, Body:str):
    messages = load_past_messages(From, Body)
    completion = complete(messages)
    record_new_message(From, Body, completion)
    resp = MessagingResponse()
    resp.message(completion)
    return str(resp)

@app.get("/")
def homepage():
    return str(Html(
        Head(
            Title("Fernmyth - Nifty and Unprofitable Webservices")
        ),
        Body(
            H1("Welcome to Fernmyth!"),
            P("A collection of nifty and unprofitable webservices.")
        )
    ))

@app.get("/purchase/{unique_id}")
def purchase_more_messages(unique_id: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT tel FROM purchase_offers WHERE unique_id = %s', [unique_id])
            result = cursor.fetchone()
            if result:
                tel = result[0]
            else:
                return "Invalid purchase link."
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''INSERT INTO purchases (tel, purchase_date, purchase_type, message_count) VALUES
                (%(tel)s, current_timestamp, 'promotion', 100)''', {"tel": tel})
    return "Purchase successful. You have been credited with 100 messages."
