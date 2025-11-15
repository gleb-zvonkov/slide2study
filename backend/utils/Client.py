from openai import OpenAI

API_KEY= "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"

def getClient():
    client = OpenAI(api_key=API_KEY)
    return client
