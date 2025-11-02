import asyncio
import httpx

N_REQUESTS = 30  # Número de queries simultáneas

async def make_request(client, query):
    response = await client.post(
        "http://127.0.0.1:8000/chat/query",
        json={"query": query}
    )
    print(response.status_code, response.json())

async def main():
    async with httpx.AsyncClient(timeout=60) as client:
        tasks = [
            make_request(client, f"¿Consulta de estrés #{i}?") for i in range(N_REQUESTS)
        ]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
