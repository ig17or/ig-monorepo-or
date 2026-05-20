package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"
)

const (
	KB = 1 << 10 // 1_024
	MB = 1 << 20 // 1_048_576
	GB = 1 << 30 // 1_073_741_824
)

func healthCheck(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
}

func sendBytes(w http.ResponseWriter, imageBytes []byte, sParams *ScreenshotParams) {
	w.Header().Set("Content-Type", "image/png")
	w.Header().Set("Content-Length", strconv.Itoa(len(imageBytes)))
	w.WriteHeader(http.StatusOK)
	_, err := w.Write(imageBytes)
	if err != nil {
		log.Println("sendBytes ", sParams.UserId, err)
	}
}

func index(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusNotFound)
}

func main() {
	initEnv()
	initPlaywright()
	defer closePlaywright()
	initNats()
	defer nc.Drain()
	server := &http.Server{
		Addr:              env.hostPort,
		ReadHeaderTimeout: 2 * time.Second,
		ReadTimeout:       30 * time.Second,
		WriteTimeout:      60 * time.Second,
		IdleTimeout:       30 * time.Second,
		MaxHeaderBytes:    10 * 1024 * 1024,
	}
	http.HandleFunc("/healthCheck", healthCheck)
	http.HandleFunc("/api/screenshot", screenshot)
	http.HandleFunc("/api/sendMessage", sendMessage)
	http.HandleFunc("/", index)
	go func() {
		log.Println("Starting API on ", env.hostPort)
		err := server.ListenAndServe()
		if err != nil {
			log.Fatal("server.ListenAndServe ", err)
		}
	}()
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	sig := <-stop
	log.Println("Received stop signal ", sig)
	if sig == syscall.SIGTERM {
		ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
		defer cancel()
		err := server.Shutdown(ctx)
		if err != nil {
			log.Println("Shutdown error ", err)
		}
	} else {
		server.Close()
	}
}
