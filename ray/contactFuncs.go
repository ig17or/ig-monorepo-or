package main

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"
)

func randomStr(l int) string {
	randomBytes := make([]byte, l)
	rand.Read(randomBytes)
	return hex.EncodeToString(randomBytes)
}

func saveMessage(text string) bool {
	dateStr := time.Now().Format("2006-01-02")
	filename := fmt.Sprintf("%s%s_%s.txt", env.messages, dateStr, randomStr(4))
	file, err := os.Create(filename)
	if err != nil {
		log.Println("sendMessage os.Create", err)
		return false
	}
	defer file.Close()
	_, err = file.WriteString(text)
	if err != nil {
		log.Println("sendMessage file.WriteString", err)
		return false
	}
	return true
}

func sendMessage(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}
	r.Body = http.MaxBytesReader(w, r.Body, MB)
	text := getMessageText(r)
	if text == "" {
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	switch ok := saveMessage(text); ok {
	case true:
		w.WriteHeader(http.StatusOK)
	case false:
		w.WriteHeader(http.StatusInternalServerError)
	}
}
