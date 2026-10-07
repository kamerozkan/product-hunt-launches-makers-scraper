"""Deploy, build, test, and package product-hunt-launches-makers-scraper on Apify."""
import datetime
import json
import os
import sys
import time
import urllib.request

TOKEN_PATH = os.path.expanduser("~/.config/apify/token")
TOKEN = open(TOKEN_PATH).read().strip()
BASE_URL = "https://api.apify.com/v2"

ACTOR_NAME = "product-hunt-launches-makers-scraper"
PROJECT_DIR = "/Users/kamerozkan/.gemini/antigravity/scratch/product-hunt-launches-makers-scraper"


def api_call(method, path, body=None):
    url = f"{BASE_URL}{path}"
    data_bytes = None
    headers = {"Authorization": f"Bearer {TOKEN}"}
    if body is not None:
        data_bytes = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def collect_sources():
    sources = []
    ignored = {"deploy_and_verify.py", ".DS_Store", "test_run.py", "logo.png"}
    for root, _, files in os.walk(PROJECT_DIR):
        if ".git" in root or "__pycache__" in root:
            continue
        for f in sorted(files):
            if f in ignored or f.endswith(".pyc"):
                continue
            if f.startswith(".") and f not in [".actor"]:
                continue
            full = os.path.join(root, f)
            rel = os.path.relpath(full, PROJECT_DIR)
            content = open(full, "r", encoding="utf-8", errors="ignore").read()
            sources.append({"name": rel, "content": content, "format": "TEXT"})
    return sources


def main():
    print("=== STEP 1: CREATE OR UPDATE ACTOR (PRIVATE) ===")
    st, res = api_call("GET", f"/acts/kamerozkan~{ACTOR_NAME}")

    actor_id = None
    if st == 200:
        actor_id = res["data"]["id"]
        print(f"Actor exists: ID={actor_id}")
    else:
        create_payload = {
            "name": ACTOR_NAME,
            "title": "Product Hunt Scraper & Daily Launch Leads (Makers & Startups)",
            "description": "Extract trending Product Hunt launches, makers, tech tags, upvote counts, rankings, and product URLs. Ultra-fast HTTP, zero proxy fees, $0.003/product.",
            "isPublic": False
        }
        st2, res2 = api_call("POST", "/acts", body=create_payload)
        if st2 != 201:
            print("Create failed:", st2, res2)
            sys.exit(1)
        actor_id = res2["data"]["id"]
        print(f"Created new PRIVATE Actor: ID={actor_id}")

    # Set metadata, pricing, and pictureUrl (KEEP isPublic: False)
    ph_logo_s3 = "https://apify-image-uploads-prod.s3.us-east-1.amazonaws.com/ralZdliP7uuVVznKq/nL9aYZlXKgqBrn5v9-apify-ph.png"
    update_payload = {
        "title": "Product Hunt Scraper & Daily Launch Leads (Makers & Startups)",
        "description": "Extract trending Product Hunt launches, makers, tech tags, upvote counts, rankings, and product URLs. Ultra-fast HTTP, zero proxy fees, $0.003/product.",
        "seoTitle": "Product Hunt Scraper & Maker Leads API | Apify",
        "seoDescription": "Extract trending Product Hunt launches, maker profiles, upvotes, and product websites. Fast API for B2B dealflow and early adopter lead generation.",
        "categories": ["LEAD_GENERATION", "MARKETING", "DEVELOPER_TOOLS"],

        "pictureUrl": ph_logo_s3,
        "isPublic": False,
        "defaultRunOptions": {
            "build": "latest",
            "timeoutSecs": 3600,
            "memoryMbytes": 256
        }
    }
    if not res.get("data", {}).get("pricingInfos"):
        update_payload["pricingInfos"] = [
            {
                "pricingModel": "PAY_PER_EVENT",
                "pricingPerEvent": {
                    "actorChargeEvents": {
                        "product-extracted": {
                            "eventTitle": "Product Extracted",
                            "eventDescription": "Charged per individual Product Hunt product extracted with official website, tagline, and launch details.",
                            "eventPriceUsd": 0.003,
                            "isPrimaryEvent": True
                        }
                    }
                }
            }
        ]
    st_up, res_up = api_call("PUT", f"/acts/{actor_id}", body=update_payload)

    print(f"Actor configured (isPublic={res_up['data']['isPublic']}): HTTP {st_up}")

    print("=== STEP 2: UPLOAD SOURCE FILES ===")
    sources = collect_sources()
    print(f"Uploading {len(sources)} source files...")
    ver_payload = {
        "versionNumber": "1.0",
        "buildTag": "latest",
        "envVars": [],
        "sourceType": "SOURCE_FILES",
        "sourceFiles": sources
    }
    st_ver, res_ver = api_call("PUT", f"/acts/{actor_id}/versions/1.0", body=ver_payload)
    if st_ver not in (200, 201):
        # try post if 1.0 does not exist
        st_ver, res_ver = api_call("POST", f"/acts/{actor_id}/versions", body=ver_payload)
    print(f"Source files uploaded: HTTP {st_ver}")

    print("=== STEP 3: TRIGGER DOCKER BUILD ===")
    st_bld, res_bld = api_call("POST", f"/acts/{actor_id}/builds?version=1.0", body={})
    if st_bld != 201:
        print("Build trigger failed:", st_bld, res_bld)
        sys.exit(1)
    build_id = res_bld["data"]["id"]
    print(f"Build triggered: ID={build_id}")

    for _ in range(40):
        time.sleep(3)
        st_chk, res_chk = api_call("GET", f"/acts/{actor_id}/builds/{build_id}")
        status = res_chk["data"]["status"]
        print(f"Build status: {status}")
        if status in ("SUCCEEDED", "FAILED", "ABORTED"):
            break

    if status != "SUCCEEDED":
        print("Build FAILED!")
        sys.exit(1)
    build_num = res_chk["data"]["buildNumber"]
    print(f"Build #{build_num} SUCCEEDED!")

    print("=== STEP 4: RUN ISOLATED TEST RUN ON APIFY ===")
    test_input = {"category": "ai", "maxItems": 10, "enrichDetails": True}
    st_run, res_run = api_call("POST", f"/acts/{actor_id}/runs", body=test_input)
    if st_run != 201:
        print("Test run trigger failed:", st_run, res_run)
        sys.exit(1)
    run_id = res_run["data"]["id"]
    print(f"Test run started: ID={run_id}")

    t0 = time.time()
    for _ in range(40):
        time.sleep(2)
        st_rc, res_rc = api_call("GET", f"/actor-runs/{run_id}")
        run_st = res_rc["data"]["status"]
        print(f"Test run status: {run_st}")
        if run_st in ("SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED"):
            break

    duration = round(time.time() - t0, 1)
    if run_st != "SUCCEEDED":
        print("Test run FAILED!")
        sys.exit(1)

    ds_id = res_rc["data"]["defaultDatasetId"]
    st_ds, res_ds = api_call("GET", f"/datasets/{ds_id}/items?limit=10")
    items = res_ds if isinstance(res_ds, list) else []
    print(f"Test run SUCCEEDED in {duration}s! Extracted {len(items)} items.")
    if items:
        print("Sample item:", items[0].get("name"), "->", items[0].get("cleanWebsite"))

    cost = res_rc["data"].get("usageTotalUsd", 0.0001)

    res_data = {
        "actor_id": actor_id,
        "actor_name": ACTOR_NAME,
        "build_num": build_num,
        "run_id": run_id,
        "duration": duration,
        "items_count": len(items),
        "cost": cost,
        "sample_item": items[0] if items else {}
    }

    with open(os.path.join(PROJECT_DIR, "test_result.json"), "w") as f:
        json.dump(res_data, f, indent=2)

    print("=== STEP 5: SEND TELEGRAM APPROVAL CARD ===")
    sample_prod = items[0] if items else {}
    sample_name = sample_prod.get("name", "Product")
    sample_url = sample_prod.get("cleanWebsite") or sample_prod.get("websiteUrl") or "N/A"
    
    bot_token = open(os.path.expanduser("~/.config/telegram/token")).read().strip()
    chat_id = open(os.path.expanduser("~/.config/telegram/chat_id")).read().strip()
    
    card_text = (
        "🚀 *YENİ AKTÖR ONAY TALEBİ (Vardiya Raporu)*\n\n"
        f"🏷 *Aktör:* `{ACTOR_NAME}`\n"
        f"🆔 *ID:* `{actor_id}`\n"
        f"⚡️ *Test:* {len(items)} ürün / {duration}s (Hafif HTTP - SIFIR Proxy)\n"
        f"💰 *Model:* Pay-per-event ($0.003 / kayıt)\n"
        f"🎯 *Örnek Veri:* {sample_name} -> {sample_url}\n\n"
        "Aktör Apify üzerinde *PRIVATE* olarak test edildi. Onayınızla mağazada yayına açılacaktır."
    )
    
    tg_payload = {
        "chat_id": chat_id,
        "text": card_text,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "✅ ONAYLA (Store'da Yayınla)", "callback_data": f"publish:{actor_id}"},
                    {"text": "❌ REDDET (Sil/Gizle)", "callback_data": f"reject:{actor_id}"}
                ]
            ]
        }
    }
    
    tg_req = urllib.request.Request(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        data=json.dumps(tg_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(tg_req, timeout=15) as resp:
            print(f"Telegram notification sent: HTTP {resp.status}")
    except Exception as e:
        print(f"Telegram notification failed: {e}")

    return res_data


if __name__ == "__main__":
    main()

