"""Main entrypoint for product-hunt-launches-makers-scraper Actor."""
import asyncio
import logging
from apify import Actor

try:
    from src.ph_client import ProductHuntClient
except ImportError:
    from ph_client import ProductHuntClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


async def main():
    async with Actor:
        actor_input = await Actor.get_input() or {}
        category = actor_input.get("category", "ai")
        max_items = actor_input.get("maxItems", 30)
        enrich_details = actor_input.get("enrichDetails", True)

        Actor.log.info(f"Starting Product Hunt scraper: category='{category}', maxItems={max_items}, enrichDetails={enrich_details}")

        client = ProductHuntClient()
        products = client.fetch_products(category=category, max_items=max_items, enrich_details=enrich_details)

        if not products:
            Actor.log.warning("No products extracted from Product Hunt.")
            await Actor.set_value("OUTPUT", {"productsExtracted": 0, "category": category})
            return

        # Charge pay-per-event if enabled on platform
        try:
            for p in products:
                try:
                    await Actor.charge({"eventName": "product-extracted", "count": 1})
                except Exception:
                    pass
        except Exception:
            pass

        # Push to dataset
        await Actor.push_data(products)
        await Actor.set_value("OUTPUT", {
            "productsExtracted": len(products),
            "category": category,
            "sampleProduct": products[0]["name"] if products else None
        })

        Actor.log.info(f"Successfully extracted and saved {len(products)} products to dataset.")


if __name__ == "__main__":
    asyncio.run(main())
