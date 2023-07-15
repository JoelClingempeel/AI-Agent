import openai
import os

openai.organization = os.environ["ORG_ID"]
openai.api_key = os.environ["API_KEY"]

def ask_chatgpt(message, temperature=0):
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "user", "content": message}
      ],
      temperature=temperature
    )
    return completion.choices[0].message.content