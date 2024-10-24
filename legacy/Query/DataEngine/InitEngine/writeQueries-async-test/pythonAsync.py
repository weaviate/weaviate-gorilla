import requests
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def send_request(session, api_key, content, id):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "temperature": 0
    }
    response = session.post(url, headers=headers, json=data)
    return f"Request {id}: {response.text}"

def main(api_key):
    content = "Please write an overview of Text-to-SQL research."
    responses = []
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(send_request, session, api_key, content, i) for i in range(100)]
            start_time = time.time()
            for future in as_completed(futures):
                responses.append(future.result())
            total_time = time.time() - start_time
    print(f"PythonAsync - All requests completed in {total_time:.2f} seconds.")
    for response in responses:
        print(response)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <api_key>")
        sys.exit(1)
    api_key = sys.argv[1]
    main(api_key)
