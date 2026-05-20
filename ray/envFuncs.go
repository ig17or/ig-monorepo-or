package main

import (
	"github.com/joho/godotenv"
	"log"
	"os"
)

type envStruct struct {
	hostPort    string
	natsConnect string
	messages    string
}

var env envStruct

func initEnv() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("godotenv.Load()", err)
	}
	env.hostPort = os.Getenv("hostPort")
	env.natsConnect = os.Getenv("natsConnect")
	env.messages = os.Getenv("messages")
}
