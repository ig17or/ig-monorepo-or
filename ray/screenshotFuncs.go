package main

import (
	"net/http"
)

var screenshotLimit = make(chan struct{}, 2)

func screenshot(w http.ResponseWriter, r *http.Request) {
	r.Body = http.MaxBytesReader(w, r.Body, MB)
	var sParams ScreenshotParams
	switch r.Method {
	case http.MethodGet:
		sParams = parseScreenshotParamsGet(r)
	case http.MethodPost:
		sParams = parseScreenshotParamsPost(r)
	default:
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}
	if sParams == (ScreenshotParams{}) {
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	if !isParamsOk(&sParams) {
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	var imageBytes []byte
	func() {
		screenshotLimit <- struct{}{}
		defer func() { <-screenshotLimit }()
		imageBytes = screenshotURL(&sParams)
	}()
	if imageBytes == nil {
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	sendBytes(w, imageBytes, &sParams)
	decrCredits(&sParams)
}
