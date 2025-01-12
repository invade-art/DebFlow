import openai
from metagpt.ext.aflow.Debate.Debate_prompt import (
    optimizer_workflow_prompt,
    genera_output_prompt,
    neg_prompt,
    Debate_prompt,
    moderator_prompt_meta,
    moderator_prompt,
)
import os
from openai import OpenAI
import json

key = "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"
prompt = "Now please output your answer in json format, with the format as follows:  {\"preference\": \"Yes or No\", \"Supported Side\": \"Affirmative or Negative\", \"Reason\": \"\"}. Please strictly output in JSON format, do not output irrelevant content"
# response = openai.ChatCompletion.create(
#                     model="gpt-4o-mini",
#                     messages=prompt,
#                     temperature=0,
#                     api_key=key,
#             )
# gen = response['choices'][0]['message']['content']
# print(gen)


client = OpenAI(
    api_key=key,  # This is the default and can be omitted
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role":"system",
            "content":"hello",
        },
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model="gpt-4o",
)
# 假设 chat_completion 是一个 ChatCompletion 对象
gen = chat_completion.choices[0].message.content

print(gen)
print(type(gen))
t = eval(gen)
print(type(t))
print(t["preference"])
print(type(t["preference"]))