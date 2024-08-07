from fasthtml.common import fast_app, Html, Head, Title, Body, H1, P, Button, Script
from smartypants.answer import answer
from smartypants.pay import record_new_message, create_gift_offer, \
    check_message_limit, apply_gift
from db import get_db_connection
from twilio.twiml.messaging_response import MessagingResponse

app, rt = fast_app()

htmx = Script(src="https://unpkg.com/htmx.org@2.0.1",
              integrity="sha384-QWGpdj554B4ETpJJC9z+ZHJcA/i59TyjxEPXiiUgN2WmTyV5OEZWCD6gQhgkdpB/",
              crossorigin="anonymous")


@rt("/smartypants/sms")
def post(From: str, Body: str):
    resp = MessagingResponse()
    if check_message_limit(From):
        purchase_url = create_gift_offer(From)
        resp.message(f"Message limit exceeded. Please purchase more messages: {purchase_url}")
    else:
        completion = answer(From, Body)
        resp.message(completion)
        record_new_message(From, Body, completion)
    return str(resp)


@rt("/")
def get():
    return Html(
        Head(
            Title("Fernmyth - Nifty and Unprofitable Webservices")
        ),
        Body(
            H1("Welcome to Fernmyth!"),
            P("A collection of nifty and unprofitable webservices.")
        )
    )


@rt("/smartypants/apply_gift/{unique_id}")
def post(unique_id: str):
    result = apply_gift(unique_id)
    if result == "invalid":
        return "Unknown purchase offer"
    elif result == "expired":
        return "You have already been credited this gift"
    else:
        return "Purchase successful. You have been credited with 100 messages."


@rt("/smartypants/purchase/{unique_id}")
def get(unique_id: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT tel FROM purchase_offers WHERE unique_id = %s', [unique_id])
            result = cursor.fetchone()
            if not result:
                return "Invalid purchase link."
            else:
                tel, = result
    return Html(
        Head(
            Title("Purchase More Messages"),
            htmx
        ),
        Body(
            H1("Purchase More Messages"),
            P(f"Click the button below to apply the gift for {tel}."),
            P(
                Button("Apply Gift", hx_post=f"/smartypants/apply_gift/{unique_id}", hx_swap="outerHTML", hx_trigger="click")
            )
        )
    )
