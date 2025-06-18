import traceback
from openai import AsyncOpenAI


async def get_embedding(client: AsyncOpenAI, chunks) -> list:
    try:
        response = await client.embeddings.create(
            input=chunks,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"get_embedding Error: {traceback.format_exc()}")
        return None