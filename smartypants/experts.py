from pydantic import BaseModel
import enum
from smartypants.base import LLMContext, client
import json


Experts = [
    ("general", "Anything not suited to one of the more specialized experts"),
    ("math", "Mathematics, from grade school arithmetic through algebraic topology"),
    ("religion", "Holy texts, morality, and myth"),
    ("smartypants", "The SMS service through which the user is interacting with you. Its pricing, policies, and functionality")
]

class _EXPERTS_ENUM(enum.Enum):
    @classmethod
    def from_list(cls, experts_list):
        return cls('Experts', {name: name for name, _ in experts_list})

_EXPERTS_ENUM = _EXPERTS_ENUM.from_list(Experts)

EXPERTS = {getattr(_EXPERTS_ENUM, name): description for name, description in Experts}

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
