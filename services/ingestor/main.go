package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"time"
)

type IngestRequest struct {
	FilePath string `json:"file_path"`
}

type IngestResponse struct {
	Status  string `json:"status"`
	Bytes   int    `json:"bytes_processed"`
	Elapsed string `json:"elapsed"`
}

func ingestHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	var req IngestRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// High-speed file reading (Go Specialty)
	content, err := ioutil.ReadFile(req.FilePath)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	elapsed := time.Since(start)
	log.Printf("GO_ENGINE | Processed %d bytes in %s", len(content), elapsed)

	json.NewEncoder(w).Encode(IngestResponse{
		Status:  "success",
		Bytes:   len(content),
		Elapsed: elapsed.String(),
	})
}

func main() {
	http.HandleFunc("/process", ingestHandler)
	port := "8081"
	fmt.Printf("🚀 Nexus Go Ingestor (Latency-Optimized) on port %s\n", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
