from smartypants.base import LLMContext, complete, client
from db import get_db_connection, q
from pydantic import BaseModel
from typing import List, Tuple
import enum
import json

class Depth(enum.Enum):
    unaware = "unaware"
    ignorant = "ignorant"
    curious = "curious"
    informed = "informed"
    dabbler = "dabbler"
    hobbyist = "hobbyist"
    practioner = "practitioner"

class BackgroundInference(BaseModel):
    domain: str
    depth: Depth
    confidence: float

class UserBackground(BaseModel):
    inferences: List[BackgroundInference]

def get_background(ctx) -> UserBackground:
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=ctx.messages,
        response_format=UserBackground
    )
    return json.loads(completion.choices[0].message.content)['inferences']


def summarize(tel):
    ctx = LLMContext()
    ctx.system("Read over the following log of your prior conversation with your counterpart. Make a mental note of things you learn about them, so that you can target your future answers at a more appropriate pedagogical level")
    with get_db_connection() as conn, conn.cursor() as cursor:
        rows = q(cursor, 'select end_message_sent, body from summaries where tel = %s order by end_message_sent asc', tel)[:-5]
        if rows:
            ctx.system("The following are summaries of what you have learned about your counterpart over your conversation")
        summary_end = '1970-01-01'
        for row in rows:
            ctx.system(row.body)
            summary_end = row.end_message_sent
        rows = q(cursor, 'select body, sent from messages where tel = %s and sent > %s and is_user order by sent asc', tel, summary_end)
        ctx.system("The following messages are not included in the past summaries")
        for row in rows:
            ctx.user(row.body)
            message_end = row.sent
        ctx.system("Update any changed confidence in the previous summaries. Also output any new background factoids")
    resp = get_background(ctx)

    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute('insert into summaries (body, tel, end_message_sent) values (%s, %s, %s)', (json.dumps(resp), tel, message_end))
