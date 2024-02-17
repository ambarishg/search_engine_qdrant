import openai
from config import *

openai.api_type = "azure"
openai.api_key = KEY
openai.api_base = ENDPOINT
openai.location = LOCATION
deployment_id_gpt4=DEPLOYMENT_ID

import openai
from openai import AzureOpenAI

client = AzureOpenAI(
  azure_endpoint = ENDPOINT, 
  api_key=KEY,  
  api_version="2023-05-15"
)

def create_prompt(context,query):
    header = "You are a helpful assistant"
    return header + context + "\n\n" + query + "\n"


def generate_answer(conversation):
    response = client.chat.completions.create(
    model=deployment_id_gpt4,
    messages=conversation,
    temperature=0,
    max_tokens=1000,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop = [' END']
    )
    return (response.choices[0].message.content).strip()

def generate_answer_from_context(user_input, context):
    conversation=[{"role": "system", "content": "Assistant is a large language model trained by OpenAI."}]
    prompt = create_prompt(context,user_input)            
    conversation.append({"role": "assistant", "content": prompt})
    conversation.append({"role": "user", "content": user_input})
    reply = generate_answer(conversation)
    return reply