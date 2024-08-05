from fasthtml.common import fast_app, serve
from smartypants.sms import load_past_messages, complete, record_new_message, generate_purchase_url
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
def foo(y:str, x:int):
    print(rt)
    return str(x) + str(y)

@app.get("/purchase/{unique_id}")
def purchase_more_messages(unique_id: str):
    # This is a placeholder implementation. In a real application, you would verify the unique_id.
    tel = "user's phone number"  # Retrieve the user's phone number associated with the unique_id
    with psycopg.connect("dbname=smartypants user=twilio") as conn:
        with conn.cursor() as cursor:
            cursor.execute('''INSERT INTO purchases (tel, purchase_date, purchase_type, message_count) VALUES
                (%(tel)s, current_timestamp, 'promotion', 100)''', {"tel": tel})
    return "Purchase successful. You have been credited with 100 messages."
    serve()
