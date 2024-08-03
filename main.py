from fasthtml.common import fast_app, serve
from smartypants.sms import load_past_messages, complete, record_new_message
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

if __name__ == '__main__':
    serve()
