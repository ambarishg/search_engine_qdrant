import openai
key = 'd6bcc40e68fc4119abcd43b4661dc8e3'
location = 'eastus'
endpoint = 'https://openaidemos007.openai.azure.com/'
openai.api_type = "azure"
openai.api_key = key
openai.api_base = endpoint
deployment_id_gpt4='gpt4'
openai.api_key = key

import openai
from openai import AzureOpenAI

client = AzureOpenAI(
  azure_endpoint = endpoint, 
  api_key=key,  
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