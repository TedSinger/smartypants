
from openai import OpenAI
client = OpenAI()

class LLMContext:
    def __init__(self):
        self.messages = []

    def system(self, content):
        self.messages.append({"role": "system", "content": content})

    def user(self, content):
        self.messages.append({"role": "user", "content": content})

    def assistant(self, content):
        self.messages.append({"role": "assistant", "content": content})

    def copy(self):
        ret = LLMContext()
        ret.messages = list(self.messages)
        return ret

def complete(ctx):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=ctx.messages
    )
    return completion.choices[0].message.content