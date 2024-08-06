from fasthtml.common import fast_app, serve, Html, Head, Title, Body, H1, P
from smartypants.answer import answer
from smartypants.pay import record_new_message, generate_purchase_url, check_message_limit, apply_gift
from db import get_db_connection
from twilio.twiml.messaging_response import MessagingResponse

app, rt = fast_app()

@app.post("/smartypants/sms")
def answer_text_message(From:str, Body:str):
    resp = MessagingResponse()
    if check_message_limit(From):
        purchase_url = generate_purchase_url(From)
        resp.message(f"Message limit exceeded. Please purchase more messages: {purchase_url}")
    else:
        completion = answer(From, Body)
        resp.message(completion)
        record_new_message(From, Body, completion)
    return str(resp)

@app.get("/")
def homepage():
    return Html(
        Head(
            Title("Fernmyth - Nifty and Unprofitable Webservices")
        ),
        Body(
            H1("Welcome to Fernmyth!"),
            P("A collection of nifty and unprofitable webservices.")
        )
    )

@app.post("/apply_gift/{tel}")
def apply_gift_route(tel: str):
    apply_gift(tel)
    return "Purchase successful. You have been credited with 100 messages."
def purchase_more_messages(unique_id: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT tel FROM purchase_offers WHERE unique_id = %s', [unique_id])
            result = cursor.fetchone()
            if result:
                tel = result[0]
            else:
                return "Invalid purchase link."
    return Html(
        Head(
            Title("Purchase More Messages")
        ),
        Body(
            H1("Purchase More Messages"),
            P(f"Click the button below to apply the gift for {tel}."),
            P(
                f'<button hx-post="/apply_gift/{tel}" hx-swap="outerHTML">Apply Gift</button>'
            )
        )
    )
