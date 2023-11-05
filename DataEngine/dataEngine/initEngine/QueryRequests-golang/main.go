package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
)

// RequestBody is the structure of the JSON payload to send in the POST request
type RequestBody struct {
	Model       string    `json:"model"`
	Messages    []Message `json:"messages"`
	Temperature float32   `json:"temperature"`
}

// Message defines the structure for the "messages" array in the RequestBody
type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

func makeMockRequest(wg *sync.WaitGroup, id int, apiKey string, ch chan<- string) {
	defer wg.Done()

	requestBody := &RequestBody{
		Model: "gpt-3.5-turbo",
		Messages: []Message{
			{
				Role:    "user",
				Content: "Say this is a test!",
			},
		},
		Temperature: 0.7,
	}

	jsonData, err := json.Marshal(requestBody)
	if err != nil {
		ch <- fmt.Sprintf("Request %d: Failed to marshal JSON - %s", id, err)
		return
	}

	req, err := http.NewRequest("POST", "https://api.openai.com/v1/chat/completions", bytes.NewBuffer(jsonData))
	if err != nil {
		ch <- fmt.Sprintf("Request %d: Failed to create request - %s", id, err)
		return
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)

	// Uncomment the lines below to actually send the request
	// client := &http.Client{}
	// resp, err := client.Do(req)
	// if err != nil {
	//     ch <- fmt.Sprintf("Request %d: Failed to send request - %s", id, err)
	//     return
	// }
	// defer resp.Body.Close()

	// Uncomment the lines below to read the response body
	// body, err := ioutil.ReadAll(resp.Body)
	// if err != nil {
	//     ch <- fmt.Sprintf("Request %d: Failed to read response body - %s", id, err)
	//     return
	// }

	// Mock response message
	body := fmt.Sprintf("Mock Response %d", id)

	ch <- fmt.Sprintf("Request %d: Success - %s", id, body)
}

func main() {
	var wg sync.WaitGroup
	ch := make(chan string, 10)   // Channel to collect responses
	apiKey := "your-api-key-here" // Replace with your actual API key

	for i := 1; i <= 10; i++ {
		wg.Add(1)
		go makeMockRequest(&wg, i, apiKey, ch)
	}

	wg.Wait()
	close(ch)

	for response := range ch {
		fmt.Println(response)
	}
}
