package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"sync"
	"time"
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

func sendRequest(wg *sync.WaitGroup, id int, apiKey string, ch chan<- string) {
	defer wg.Done()

	requestBody := &RequestBody{
		Model: "gpt-3.5-turbo",
		Messages: []Message{
			{
				Role:    "user",
				Content: "Please write an overview of Text-to-SQL research.",
			},
		},
		Temperature: 0,
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

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		ch <- fmt.Sprintf("Request %d: Failed to send request - %s", id, err)
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		ch <- fmt.Sprintf("Request %d: Failed to read response body - %s", id, err)
		return
	}

	ch <- string(body)
}

func main() {
	var wg sync.WaitGroup
	ch := make(chan string, 100) // Channel to collect responses
	apiKey := os.Args[1]         // go run main.go api-key

	start := time.Now()
	for i := 1; i <= 100; i++ {
		wg.Add(1)
		go sendRequest(&wg, i, apiKey, ch)
	}

	wg.Wait()
	close(ch)

	elapsed := time.Since(start)
	fmt.Printf("GoAsync - All requests completed in %s\n", elapsed)

	for response := range ch {
		fmt.Println(response)
	}
}
