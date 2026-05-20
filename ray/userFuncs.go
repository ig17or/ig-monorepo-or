package main

import (
	"strconv"
)

func getCredits(user string) int {
	creditsStr := natsGet(user)
	if creditsStr == "" {
		return 0
	}
	creditsInt, err := strconv.Atoi(creditsStr)
	if err != nil {
		return 0
	}
	return creditsInt
}

func ensureCredits(user string) bool {
	if getCredits(user) > 0 {
		return true
	}
	return false
}

func decrCredits(sParams *ScreenshotParams) {
	if sParams.UserId == "demo" {
		return
	}
	creditsInt := getCredits(sParams.UserId)
	creditsStr := strconv.Itoa(creditsInt - 1)
	natsPut(sParams.UserId, creditsStr)
}

func isEligible(sParams *ScreenshotParams) bool {
	if sParams.UserId == "demo" {
		sParams.Width = 640
		sParams.Height = 480
		sParams.Full = false
		sParams.Consent = false
		sParams.BlockAds = false
		return true
	} else {
		return ensureCredits(sParams.UserId)
	}
}
