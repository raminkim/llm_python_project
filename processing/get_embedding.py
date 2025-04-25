from openai import OpenAI

def get_embedding(client: OpenAI, text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding