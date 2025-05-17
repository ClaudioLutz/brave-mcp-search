import httpx

try:
    resp = httpx.post(
        "http://localhost:4000/tools/brave_web_search/invoke",
        json={"query": "Acme Corp info@", "count": 5}
    )
    resp.raise_for_status()  # Raise an exception for bad status codes
    print("Response JSON:", resp.json())
except httpx.HTTPStatusError as exc:
    print(f"HTTP error occurred: {exc}")
    print(f"Response content: {exc.response.text}")
except httpx.RequestError as exc:
    print(f"An error occurred while requesting {exc.request.url!r}.")
    print(f"Error details: {exc}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
