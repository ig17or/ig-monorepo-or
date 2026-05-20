package main

import (
	"context"
	"errors"
	"fmt"
	"github.com/nats-io/nats.go"
	"github.com/nats-io/nats.go/jetstream"
	"log"
	"time"
)

var (
	nc *nats.Conn
	kv jetstream.KeyValue
)

func initNats() {
	var err error
	nc, err = nats.Connect(env.natsConnect)
	if err != nil {
		log.Fatal("nats.Connect: ", err)
	}
	js, err := jetstream.New(nc)
	if err != nil {
		log.Fatal("jetstream.New: ", err)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	kv, err = js.CreateKeyValue(ctx, jetstream.KeyValueConfig{
		Bucket: "users",
	})
	if err != nil {
		log.Fatal("js.CreateKeyValue: ", err)
	}
}

func natsGetWithErr(key string) (string, error) {
	entry, err := kv.Get(context.Background(), key)
	if err != nil {
		if errors.Is(err, jetstream.ErrKeyNotFound) {
			return "", nil
		}
		return "", err
	}
	return string(entry.Value()), nil
}

func natsGet(key string) string {
	entry, err := kv.Get(context.Background(), key)
	if err != nil {
		return ""
	}
	return string(entry.Value())
}

func natsPut(key string, value string) {
	_, err := kv.Put(context.Background(), key, []byte(value))
	if err != nil {
		log.Println("natsPut ", key, err)
	}
}

func natsUpdate(key string, newValue string) error {
	ctx := context.Background()
	entry, err := kv.Get(ctx, key)
	if err != nil {
		return err
	}
	_, err = kv.Update(ctx, key, []byte(newValue), entry.Revision())
	if err != nil {
		return fmt.Errorf("concurrency conflict: %w", err)
	}
	return nil
}

func natsDel(key string) error {
	return kv.Delete(context.Background(), key)
}
