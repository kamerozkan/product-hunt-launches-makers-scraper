# Product Hunt Scraper & Daily Launch Leads (Makers & Startups)

[![Run on Apify](https://apify.com/actor-badge?actor=kamerozkan/product-hunt-launches-makers-scraper)](https://apify.com/kamerozkan/product-hunt-launches-makers-scraper)
[![Apify Actor](https://img.shields.io/badge/Apify-Actor-blue.svg)](https://apify.com/kamerozkan/product-hunt-launches-makers-scraper)
[![Pricing](https://img.shields.io/badge/Pricing-$0.003%20/%20record-green.svg)](https://apify.com/kamerozkan/product-hunt-launches-makers-scraper)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg)](https://apify.com/kamerozkan/product-hunt-launches-makers-scraper)

Ultra-fast, browserless scraper and real-time data API for **Product Hunt** (`producthunt.com`). Extract new daily product launches, trending AI tools, developer software, official product websites, descriptions, and upvote metrics without browser overhead or proxy bandwidth fees.

---

## Who Buys and Uses This Actor?

- **B2B Outbound SDRs & Agency Owners**: Pitch design, development, marketing, or SEO services to newly launched startups immediately after they launch on Product Hunt.
- **Venture Capital & Angel Investors**: Track emerging software and breakout AI tools on day one. Filter by category (AI, Developer Tools, Productivity) to feed dealflow pipelines.
- **Product Managers & Founders**: Monitor competitors, analyze launch taglines, and benchmark upvote traction across your niche.
- **Lead Generation & Dealflow Aggregators**: Automatically enrich CRM databases with clean company domain names and product summaries.

---

## Key Features

- **Direct Official Websites**: Automatically extracts clean, direct external product URLs (`https://lovable.dev`, `https://n8n.io`) for instant B2B outreach.
- **Category Filtering**: Extract from high-demand categories: AI, Developer Tools, Productivity, Marketing, Design Tools, Finance, or All (Homepage).
- **Sub-Second Speed**: Built with asynchronous HTTP/2 requests. Runs in seconds on low memory (128 MB to 256 MB RAM).
- **Pay-Per-Event Value**: Priced at a flat **$0.003 per extracted product** ($3.00 per 1,000 leads). No expensive monthly subscription required.
- **Zero Proxy Costs**: Direct endpoints without aggressive anti-bot captchas or browser emulation costs.

---

## Input Example

```json
{
  "category": "ai",
  "maxItems": 30,
  "enrichDetails": true
}
```

### Input Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `category` | String | `"ai"` | Category: `"all"`, `"ai"`, `"developer-tools"`, `"productivity"`, `"marketing"`, `"design-tools"`, `"finance"`. |
| `maxItems` | Integer | `30` | Maximum number of products to extract (1 to 500). |
| `enrichDetails` | Boolean | `true` | When true, fetches official external website URL and extended overview. |

---

## Output Example

```json
{
  "id": "566141",
  "name": "Lovable",
  "tagline": "The world's first AI Fullstack Engineer",
  "slug": "lovable",
  "category": "ai",
  "productHuntUrl": "https://www.producthunt.com/products/lovable",
  "websiteUrl": "https://lovable.dev/?via=product-hunt",
  "cleanWebsite": "https://lovable.dev",
  "description": "The AI Fullstack Engineer that works. Ship lovable full-stack applications 20x faster than by writing code.",
  "votesCount": 39,
  "extractedAt": "2026-10-07T08:02:47.292829+00:00"
}
```

---

## Integrations & No-Code Automation

Connect your live Product Hunt stream directly into your existing business workflows:

### 1. Google Sheets (Live Sync)
Pull extracted products and websites directly into your spreadsheet:
- **Formula**: In cell A1, paste `=IMPORTDATA("https://api.apify.com/v2/datasets/{DATASET_ID}/items?format=csv&clean=1")`
- **Apify Integration**: Under the **Integrations** tab, enable **Google Sheets** to automatically append newly launched products after each run.

### 2. Make.com (Integromat)
- Add the **Apify: Run Actor** module to your scenario.
- Route newly discovered websites directly to Airtable, Notion, Slack alerts, or your CRM.

### 3. n8n Automation
- Use the native **Apify Node** to trigger scraping runs and send fresh product leads directly to your Postgres database or AI enrichment agent.

### 4. Clay & Dealflow Feeds
- Import the Apify dataset directly into Clay via Webhook to enrich founder contacts, LinkedIn URLs, and company funding.

### 5. Automated Weekly Schedule (Recurring Retention Recipe)

Never run scrapers manually. Keep your dealflow and lead pipeline updated automatically:
- **Trigger**: Every Monday at 08:00 UTC (cron: `0 8 * * 1`)
- **Apify Schedule**: Go to **Schedules** tab -> Create new schedule -> Select `product-hunt-launches-makers-scraper`
- **Destination**: Auto-append new rows to Google Sheets or send a Slack alert with the top 10 upvoted products of the week.

---

## Pricing

This Actor uses Apify's **Pay-Per-Event (PPE)** pricing model:
- **Rate**: $0.003 per extracted product.
- **1,000 Products**: $3.00.
- **Platform Usage**: Free platform compute units are included. You only pay for verified, extracted data items.

---

## Support & Feature Requests

Found a bug or need a specific topic filter added? Open an issue on the **Issues** tab.
