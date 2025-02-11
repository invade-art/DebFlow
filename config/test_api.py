from openai import OpenAI
client = OpenAI(api_key="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")

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "hi"
        }
    ]
)

print(completion.choices[0].message)