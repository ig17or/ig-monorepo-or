package main

import (
	"github.com/playwright-community/playwright-go"
	"log"
	"regexp"
)

type Scraper struct {
	pw      *playwright.Playwright
	browser playwright.Browser
	context playwright.BrowserContext
}

var globalScraper *Scraper
var consentWords *regexp.Regexp

func initPlaywright() {
	pw, err := playwright.Run()
	if err != nil {
		log.Fatal("initPlaywright playwright.Run ", err)
	}
	browser, err := pw.Chromium.Launch(playwright.BrowserTypeLaunchOptions{
		Headless: playwright.Bool(true),
		Args: []string{
			"--disable-blink-features=AutomationControlled",
			"--no-sandbox",
			"--disable-dev-shm-usage",
		},
	})
	if err != nil {
		log.Fatal("initPlaywright pw.Chromium.Launch ", err)
	}
	context, err := browser.NewContext(playwright.BrowserNewContextOptions{
		UserAgent: playwright.String("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"),
	})
	if err != nil {
		log.Fatal("initPlaywright browser.NewContext ", err)
	}
	globalScraper = &Scraper{
		pw:      pw,
		browser: browser,
		context: context,
	}
	consentWords = regexp.MustCompile(`(?i)accept|agree|consent|allow|got it|ok|yes|aceptar|de acuerdo|akzeptieren|einverstanden|zustimmen|erlauben`)
}

func closePlaywright() {
	if globalScraper == nil {
		return
	}
	globalScraper.context.Close()
	globalScraper.browser.Close()
	globalScraper.pw.Stop()
}

func setupAdBlocking(page playwright.Page) error {
	adPatterns := []string{
		"*google-analytics.com*",
		"*doubleclick.net*",
		"*googlesyndication.com*",
		"*adservice.google.com*",
		"*adnxs.com*",
		"*facebook.net*",
		"*amazon-adsystem.com*",
	}
	for _, pattern := range adPatterns {
		err := page.Route(pattern, func(route playwright.Route) {
			route.Abort()
		})
		if err != nil {
			return err
		}
	}
	return nil
}

func pushConsent(page playwright.Page) {
	pageBtn := page.GetByRole("button", playwright.PageGetByRoleOptions{
		Name: consentWords,
	})
	if count, _ := pageBtn.Count(); count > 0 {
		pageBtn.First().Click()
		return
	}
	for _, f := range page.Frames() {
		frameBtn := f.GetByRole("button", playwright.FrameGetByRoleOptions{
			Name: consentWords,
		})
		if count, _ := frameBtn.Count(); count > 0 {
			frameBtn.First().Click()
			return
		}
	}
}

func screenshotURL(sParams *ScreenshotParams) []byte {
	page, err := globalScraper.context.NewPage()
	if err != nil {
		log.Fatal("screenshotURL NewPage", err)
	}
	defer page.Close()
	if sParams.BlockAds {
		if err := setupAdBlocking(page); err != nil {
			log.Println("screenshotURL setupAdBlocking ", err)
			return nil
		}
	}
	err = page.SetViewportSize(sParams.Width, sParams.Height)
	if err != nil {
		log.Println("screenshotURL SetViewportSize ", err)
		return nil
	}
	err = page.AddInitScript(playwright.Script{
		Content: playwright.String(`Object.defineProperty(navigator, 'webdriver', {get: () => undefined})`),
	})
	if err != nil {
		log.Println("screenshotURL AddInitScript ", err)
		return nil
	}
	_, err = page.Goto(sParams.URL, playwright.PageGotoOptions{
		WaitUntil: playwright.WaitUntilStateNetworkidle,
		//WaitUntil: playwright.WaitUntilStateDomcontentloaded,
		Timeout: playwright.Float(30000),
	})
	if err != nil {
		log.Println("screenshotURL page.Goto ", err)
		return nil
	}
	if sParams.Consent {
		pushConsent(page)
	}
	imageBytes, err := page.Screenshot(playwright.PageScreenshotOptions{
		FullPage: playwright.Bool(sParams.Full),
		Type:     playwright.ScreenshotTypePng,
	})
	if err != nil {
		log.Println("screenshotURL page.Screenshot ", err)
		return nil
	}
	return imageBytes
}
