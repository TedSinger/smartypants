from smartypants.base import LLMContext, complete
from db import get_db_connection, q

PROMPT = """You are answering in SMS. Be brief, direct, precise. Prefer short words and active voice. Prefer scientifically
grounded answers, keeping in mind (but not pontificating on) the epistemic limitations of fields such as nutrition, sociology,
economics. If you must disclaim, do so only once, at the start, with a brief statement such as 'I am NOT a lawyer. Here is my
guess:' or 'People disagree. Here are the main viewpoints:'. Do not waffle, hedge, or add vague qualifiers. Do acknowledge
specific tradeoffs and common complications, but do not defer to generic platitudes like 'Be careful' or 'Do your own research'."""


def load_past_messages(tel, body):
    ctx = LLMContext()
    with get_db_connection() as conn, conn.cursor() as cursor:
        rows = q(cursor, 'select end_message_sent, body from summaries where tel = %s order by end_message_sent asc', tel)
        if rows:
            ctx.system("The following are summaries of what you have learned about your counterpart over your conversation")
        summary_end = '1970-01-01'
        for row in rows:
            ctx.system(row.body)
            summary_end = row.end_message_sent
        rows = q(cursor, 'select is_user, body from messages where tel = %s and sent > %s order by sent asc', tel, summary_end)
        ctx.system(PROMPT)
        for row in rows:
            if row.is_user:
                ctx.user(row.body)
            else:
                ctx.assistant(row.body)
    ctx.user(body)
    return ctx




def answer(From, Body):
    messages = load_past_messages(From, Body)
    return complete(messages)


def summarize(tel):
    # FIXME: store a background json object. {factoid: (severity, confidence)}
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
    resp = complete(ctx)
    print(resp)
    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute('insert into summaries (body, end_message_sent) values (%s, %s)', (resp, message_end))
