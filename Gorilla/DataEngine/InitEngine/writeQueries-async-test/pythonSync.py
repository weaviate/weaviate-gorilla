import requests
import json
import sys
import time

def send_request(api_key, content, id):
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
    response = requests.post(url, headers=headers, json=data)
    return f"Request {id}: {response.text}"

def main(api_key):
    content = "Please write an overview of Text-to-SQL research."
    start_time = time.time()
    for i in range(100):
        response = send_request(api_key, content, i+1)
        print(response)
    total_time = time.time() - start_time
    print(f"PythonSync - All requests completed in {total_time:.2f} seconds.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <api_key>")
        sys.exit(1)
    api_key = sys.argv[1]
    main(api_key)
