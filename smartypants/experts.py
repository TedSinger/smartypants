from pydantic import BaseModel
import enum
from smartypants.base import LLMContext, client, complete
import json
from collections import namedtuple
from textwrap import dedent

class GenericExpert:
    name = "general"
    summary = "Anything not suited to one of the more specialized experts"
    def complete(self, ctx):
        return complete(ctx)

class MathExpert:
    name = "math"
    summary = "Mathematics, from grade school arithmetic through algebraic topology"

class ReligionExpert:
    name = "religion"
    summary = "Holy texts, morality, and myth"

class SmartypantsExpert(GenericExpert):
    name = "smartypants"
    summary = "The SMS service through which the user is interacting with you. Its pricing, policies, and functionality"
    def complete(self, ctx):
        c = LLMContext()
        c.system(dedent("""
            You are 'SmartyPants', an SMS AI. You are designed to be as helpful as possible - accurate and direct, without false confidence or false humility.
            
            You are produced by a solo hobby developer. You are currently free to use, but expected to cost 1 cent per message.

            This service is amateurish, so any messages could be read by the developer, various online service, or anyone who bothers to hack into the service database.
            """))
        c.messages.extend(ctx.messages)
        return complete(c)
        

EXPERTS = {e.name: e for e in [
    GenericExpert(),
    MathExpert(),
    ReligionExpert(),
    SmartypantsExpert()
]}

_EXPERTS_ENUM = enum.Enum('Experts', {e: e for e in sorted(EXPERTS.keys())})


class ExpertSchema(BaseModel):
    expert: _EXPERTS_ENUM

_QUESTION = "Which expert is best suited to answer the user? Choose from:\n" + \
    '\n'.join([f" - {e.name}: {e.summary}" for e in EXPERTS.values()])

def get_expert(ctx) -> GenericExpert:
    ctx = ctx.copy()
    ctx.system(_QUESTION)
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=ctx.messages,
        response_format=ExpertSchema
    )
    name = json.loads(completion.choices[0].message.content)['expert']
    return EXPERTS[name]

