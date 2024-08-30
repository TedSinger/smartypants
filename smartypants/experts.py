from pydantic import BaseModel
import enum
from smartypants.base import LLMContext, client
import json


class _EXPERTS_ENUM(enum.Enum):
    general: str = "general"
    math: str = "math"
    religion: str = "religion"
    smartypants: str = "smartypants"

EXPERTS = {
    _EXPERTS_ENUM.general: "Anything not suited to one of the more specialized experts",
    _EXPERTS_ENUM.math: "Mathematics, from grade school arithmetic through algebraic topology",
    _EXPERTS_ENUM.religion: "Holy texts, morality, and myth",
    _EXPERTS_ENUM.smartypants: "The SMS service through which the user is interacting with you. Its pricing, policies, and functionality"
}

class ExpertSchema(BaseModel):
    expert: _EXPERTS_ENUM

_QUESTION = "Which expert is best suited to answer the user? Choose from:\n" + \
    '\n'.join([f" - {k.name}: {v}" for k, v in EXPERTS.items()])

def get_expert(ctx):
    ctx = ctx.copy()
    ctx.system(_QUESTION)
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=ctx.messages,
        response_format=ExpertSchema
    )
    return json.loads(completion.choices[0].message.content)['expert']

EXTRA_CONTEXT_FOR_EXPERTS = {
    "smartypants": """
    You are 'SmartyPants', an SMS AI. You are designed to be as helpful as possible - accurate and direct, without false confidence or false humility.
    
    You are produced by a solo hobby developer. You are currently free to use, but expected to cost 1 cent per message.

    This service is amateurish, so any messages could be read by the developer, various online service, or anyone who bothers to hack into the service database.
    """
}