from openai import OpenAI


def getClient():
    client = OpenAI(api_key=API_KEY)
    return client
