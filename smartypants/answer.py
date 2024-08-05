import os
from openai import OpenAI
from db import get_db_connection

client = OpenAI()
PROMPT = """You are answering in SMS. Be brief, direct, precise. Prefer short words and active voice. Prefer scientifically
grounded answers, keeping in mind (but not pontificating on) the epistemic limitations of fields such as nutrition, sociology,
economics. If you must disclaim, do so only once, at the start, with a brief statement such as 'I am NOT a lawyer. Here is my
guess:' or 'People disagree. Here are the main viewpoints:'. Do not waffle, hedge, or add vague qualifiers. Do acknowledge
specific tradeoffs and common complications, but do not defer to generic platitudes like 'Be careful' or 'Do your own research'."""

def load_past_messages(tel, body):
    messages = [{"role": "system", "content": PROMPT}]
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('select is_user, body from messages where tel = %s order by sent asc', [tel])
            rows = cursor.fetchall()
            for row in rows:
                messages.append({"role": "user" if row[0] else "assistant", "content": row[1]})
    messages.append({"role": "user", "content": body})
    return messages

def complete(messages):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    return completion.choices[0].message.content
