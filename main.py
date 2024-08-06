from fasthtml.common import fast_app, serve, Html, Head, Title, Body, H1, P
from smartypants.answer import answer
from smartypants.pay import record_new_message, create_gift_offer, check_message_limit, apply_gift
from db import get_db_connection
from twilio.twiml.messaging_response import MessagingResponse

app, rt = fast_app()

@app.post("/smartypants/sms")
def answer_text_message(From:str, Body:str):
    resp = MessagingResponse()
    if check_message_limit(From):
        purchase_url = create_gift_offer(From)
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

@app.post("/smartypants/apply_gift/{unique_id}")
def apply_gift_route(unique_id: str):
    apply_gift(unique_id)
    return "Purchase successful. You have been credited with 100 messages."

@app.get("/smartypants/purchase/{unique_id}")
def see_purchase_offers(unique_id: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT tel FROM purchase_offers WHERE unique_id = %s', [unique_id])
            result = cursor.fetchone()
            if not result:
                return "Invalid purchase link."
    return Html(
        Head(
            Title("Purchase More Messages")
        ),
        Body(
            H1("Purchase More Messages"),
            P(f"Click the button below to apply the gift for {tel}."),
            P(
                f'<button hx-post="/smartypants/apply_gift/{unique_id}" hx-swap="outerHTML">Apply Gift</button>'
            )
        )
    )
