from smartypants.base import LLMContext, complete
from db import get_db_connection, q
import json
from smartypants.summaries import get_summary


PROMPT = """You are answering in SMS. Be brief, direct, precise. Prefer short words and active voice. Prefer scientifically
grounded answers, keeping in mind (but not pontificating on) the epistemic limitations of fields such as nutrition, sociology,
economics. If you must disclaim, do so only once, at the start, with a brief statement such as 'I am NOT a lawyer. Here is my
guess:' or 'People disagree. Here are the main viewpoints:'. Do not waffle, hedge, or add vague qualifiers. Do acknowledge
specific tradeoffs and common complications, but do not defer to generic platitudes like 'Be careful' or 'Do your own research'."""


def load_past_messages(tel, body) -> LLMContext:
    ctx = LLMContext()
    summary, summary_end = get_summary(tel)
    if summary:
        ctx.system("The following are your previous estimates of your counterpart's knowledge of various topics:")
        ctx.system(summary)
    
    with get_db_connection() as conn, conn.cursor() as cursor:
        rows = q(cursor, 'select is_user, body from messages where tel = %s and sent > %s order by sent asc', tel, summary_end)
        ctx.system(PROMPT)
        for row in rows[-50:]:
            if row.is_user:
                ctx.user(row.body)
            else:
                ctx.assistant(row.body)
    ctx.user(body)
    return ctx


def answer(From, Body):
    messages = load_past_messages(From, Body)
    return complete(messages)
