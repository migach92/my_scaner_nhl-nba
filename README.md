# 🏒🏀 Value Bet Scanner: Forebet vs Polymarket (NHL & NBA)

Automatically compare winning probabilities from [Forebet](https://www.forebet.com) with real‑time prediction market prices on [Polymarket](https://polymarket.com/?r=chance-trade).  
Find edges (value) where the market price is lower than the statistical model's estimate.

## Features
- Separate scanners for **NHL** and **NBA** – run only the sport you need
- Scrapes upcoming matches from Forebet (via ScraperAPI to bypass Cloudflare)
- Retrieves active Moneyline markets from Polymarket Gamma API
- Intelligent team‑name matching (normalizes abbreviations and alternate forms)
- Outputs **all matched matches** with percentage differences
- Highlights **value signals** where the discrepancy exceeds a configurable threshold (default 5%)
- Ready to run in any Python environment (Replit, GitHub Codespaces, local)

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/migach92/my_scaner_nhl-nba.git
cd my_scaner_nhl-nba
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get a ScraperAPI key
Forebet is protected by Cloudflare, so we use **ScraperAPI** to fetch the page reliably.

👉 **[Sign up with this link to get 5,000 free API calls and support the project](https://www.scraperapi.com/?fp_ref=anatoliy52)**

After signing up, copy your API key from the [ScraperAPI dashboard](https://www.scraperapi.com/dashboard).

### 4. Configure the script
Open the script you want to run and replace the placeholder with your key:
```python
API_KEY = 'YOUR_SCRAPERAPI_KEY'
```
Optional: Adjust `VALUE_THRESHOLD = 5.0` if you want a different sensitivity.

### 5. Run
Choose the sport you want to scan:

```bash
# NHL
python nhl_scanner.py

# NBA
python nba_scanner.py
```
You will see a table of all matched games and any value signals.

---

## Example Output (NHL or NBA)
```
📋 All matched matches:
   Boston Bruins vs Buffalo Sabres
      Forebet: 62.0% / 38.0%
      Polymarket: 56.0% / 44.0%
      Difference: Boston +6.0%, Buffalo -6.0%

🔔 VALUE SIGNALS (diff ≥ 5%)
#1 Boston Bruins vs Buffalo Sabres
   Bet on: Boston Bruins
   Forebet: 62.0%
   Polymarket: 56.0% (price 0.560)
   Value: +6.0%
   🔗 https://polymarket.com/event/...
```

---

## How It Works

1. **Forebet** → probability estimates are scraped using ScraperAPI.
2. **Polymarket** → Gamma API returns live market prices.
3. Team names are normalized (e.g., “Philadelphia Flyers” → “flyers”) and fuzzy‑matched.
4. If Forebet's probability exceeds Polymarket's implied probability by more than the threshold, it's flagged as a value bet.

---

## Platforms & Affiliate Links

These are the services that make this project possible.  
If you sign up through the links below, you support the development at **no extra cost** to you.

| Service | What it does | Affiliate link |
|---|---|---|
| **ScraperAPI** | Bypasses Cloudflare and proxies scraping requests | [Get 5,000 free calls →](https://www.scraperapi.com/?fp_ref=anatoliy52) |
| **Polymarket** | World's largest prediction market – trade on sports, politics, and more | [Join Polymarket →](https://polymarket.com/?r=chance-trade) |
| **Preddy Trade** | Polymarket‑based super‑terminal: copytrading, stop‑losses, multi‑wallet management | [Try Preddy Trade →](https://preddy.trade/?r=b16ef57) |

---

## Affiliate Disclosure

This project contains affiliate links. If you click on them and make a purchase or sign up, I may receive a commission. This does not affect the price you pay and helps me maintain and improve the tool. Thank you for your support!

---

## Contributing

Pull requests and suggestions are welcome. Please open an issue first to discuss what you would like to change.
