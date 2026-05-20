package main

import (
	"encoding/json"
	"github.com/gorilla/schema"
	"log"
	"net/http"
	"net/url"
)

type ScreenshotParams struct {
	UserId   string `json:"userId"`
	URL      string `json:"url"`
	Width    int    `json:"width"`
	Height   int    `json:"height"`
	Full     bool   `json:"full"`
	Consent  bool   `json:"consent"`
	BlockAds bool   `json:"blockAds"`
}

type ContactText struct {
	Text string `json:"text"`
}

var decoder = schema.NewDecoder()

func parseScreenshotParamsGet(r *http.Request) ScreenshotParams {
	var params ScreenshotParams
	err := r.ParseForm()
	if err != nil {
		log.Println("parseAnyScreenshotRequest r.ParseForm ", err)
		return ScreenshotParams{}
	}
	if err := decoder.Decode(&params, r.Form); err != nil {
		log.Println("parseAnyScreenshotRequest decoder.Decode ", err)
		return ScreenshotParams{}
	}
	return params
}

func parseScreenshotParamsPost(r *http.Request) ScreenshotParams {
	var sParams ScreenshotParams
	err := json.NewDecoder(r.Body).Decode(&sParams)
	if err != nil {
		return ScreenshotParams{}
	}
	return sParams
}

func getMessageText(r *http.Request) string {
	var contactText ContactText
	err := json.NewDecoder(r.Body).Decode(&contactText)
	if err != nil {
		return ""
	}
	return contactText.Text
}

func isValidURL(str string) bool {
	u, err := url.ParseRequestURI(str)
	if err != nil {
		return false
	}
	if u.Scheme == "" || u.Host == "" {
		return false
	}
	if u.Scheme != "http" && u.Scheme != "https" {
		return false
	}
	return true
}

func isParamsOk(sParams *ScreenshotParams) bool {
	if !isValidURL(sParams.URL) {
		return false
	}
	return isEligible(sParams)
}
