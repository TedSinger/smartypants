from fasthtml.common import fast_app, Html, Head, Title, Body, H1, P, Button, Script
from smartypants.answer import answer
from smartypants.pay import record_new_message, create_gift_offer, \
    check_message_limit, apply_gift
from db import get_db_connection, q, get_pool
from twilio.twiml.messaging_response import MessagingResponse

app, rt = fast_app()


@app.on_event("shutdown")
async def shutdown():
    get_pool().close()


htmx = Script(src="https://unpkg.com/htmx.org@2.0.1",
              integrity="sha384-QWGpdj554B4ETpJJC9z+ZHJcA/i59TyjxEPXiiUgN2WmTyV5OEZWCD6gQhgkdpB/",
              crossorigin="anonymous")


@rt("/smartypants/sms", methods=["GET", "POST"])
def post(From: str, Body: str):
    resp = MessagingResponse()
    if check_message_limit(From):
        purchase_url = create_gift_offer(From)
        resp.message(f"This service costs money to run. Can you help chip in? {purchase_url}")
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
    try:
        apply_gift(unique_id)
        return "Purchase successful. You have been credited with 100 messages."
    except ValueError as e:
        return str(e)


@rt("/smartypants/purchase/{unique_id}")
def get(unique_id: str):
    with get_db_connection() as conn, conn.cursor() as cursor:
        result = q(cursor, 'SELECT tel FROM purchase_offers WHERE unique_id = %s', unique_id)
        if not result:
            return "Invalid purchase link."
    return Html(
        Head(
            Title("Purchase More Messages"),
            htmx
        ),
        Body(
            H1("Purchase More Messages"),
            P(f"I don't know how to accept money yet. So click the button for more free messages for {result[0].tel}."),
            P(
                Button("Apply Gift",
                       hx_post=f"/smartypants/apply_gift/{unique_id}",
                       hx_swap="outerHTML",
                       hx_trigger="click")
            )
        )
    )
