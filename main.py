#!/usr/bin/env python3
"""
Financial Regulatory News Ingestion Daemon
===========================================
This is the core pipeline that orchestrates:
1. RSS Monitoring (RBI & SEBI)
2. Playwright Scraping for full-text extraction
3. AI processing for structured data & semantic embeddings
4. Local SQLite storage via DatabaseConnector
5. Alerting for high-impact news
"""

import os
import sys
import asyncio
import time
import argparse
from typing import Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.box import ROUNDED

# Internal modules
import config
from rss_monitor import get_all_latest_updates
from scraper import scrape_single_url
from extractor import extract_structured_update
from db_connector import LocalSQLiteConnector
from embedder import generate_embedding
from notifier import send_alert

console = Console()

def display_banner():
    console.print()
    banner = Panel(
        "[bold cyan]▲ ANTIGRAVITY FINANCIAL DATA ENGINE (DAEMON) ▲[/bold cyan]\n"
        "[dim]RSS -> Scrape -> AI Extract -> Embed -> SQLite[/dim]",
        box=ROUNDED,
        expand=False,
        border_style="cyan"
    )
    console.print(banner)
    console.print()

async def process_single_update(item: Dict[str, Any], db: LocalSQLiteConnector, status):
    url = item["url"]
    
    # 1. Skip if already processed
    if db.url_exists(url):
        return False
        
    status.update(f"[bold white]New Update Detected![/bold white] Fetching {url}...")
    
    # 2. Scrape full text
    raw_text = await scrape_single_url(url)
    if not raw_text:
        # Fallback to the summary if scraping failed
        raw_text = item["summary"]
        
    # 3. AI Extraction
    status.update(f"[bold white]Extracting metrics via AI...[/bold white]")
    parsed_data = await extract_structured_update(raw_text, title_fallback=item["title"])
    
    if parsed_data:
        impact = parsed_data.regulatory_impact
        item["regulatory_impact"] = impact
        item["affected_entities"] = parsed_data.affected_entities
        # Override short summary with AI summary if we got one
        item["summary"] = parsed_data.summary
    else:
        item["regulatory_impact"] = "Unknown"
        item["affected_entities"] = []
        
    item["raw_text"] = raw_text
    
    # 4. Generate Semantic Embeddings
    status.update(f"[bold white]Generating semantic vectors...[/bold white]")
    # Combine title and raw_text for maximum search context, truncating to 10k chars for safety
    text_to_embed = f"Title: {item['title']}\n\n{raw_text}"
    embedding_bytes = await generate_embedding(text_to_embed[:10000])
    item["embedding"] = embedding_bytes
    
    # 5. Save to Database
    status.update(f"[bold white]Saving to Database...[/bold white]")
    db.insert_update(item)
    
    console.print(f"[green]✔ Processed and saved:[/green] {item['title'][:60]}...")
    
    # 6. Check for Alerts
    if "high" in item.get("regulatory_impact", "").lower():
        send_alert(item)
        
    return True

async def run_pipeline(db: LocalSQLiteConnector, limit: int = 0):
    with Status("[bold white]Fetching latest RSS feeds...[/bold white]", console=console, spinner="dots") as status:
        updates = get_all_latest_updates()
        # Sort all updates globally by publishedAt descending so we always process the newest news first
        updates.sort(key=lambda x: x["publishedAt"], reverse=True)
        status.update(f"[bold green]Found {len(updates)} items across feeds. Checking database...[/bold green]")
        
        new_items_processed = 0
        for item in updates:
            # If we've hit the limit of NEW items to process this cycle, stop.
            if limit > 0 and new_items_processed >= limit:
                break
                
            processed = await process_single_update(item, db, status)
            if processed:
                new_items_processed += 1
                
        if new_items_processed == 0:
            console.print("[dim]No new updates found in this cycle.[/dim]")
        else:
            console.print(f"[bold green]Cycle complete. Processed {new_items_processed} new updates.[/bold green]")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--daemon", action="store_true", help="Run continuously in a loop.")
    parser.add_argument("--interval", type=int, default=3600, help="Polling interval in seconds (default 3600 = 1 hour).")
    parser.add_argument("--limit", type=int, default=0, help="Limit the number of new updates to scrape per cycle (0 = no limit).")
    args = parser.parse_args()

    display_banner()
    
    if not config.OPENAI_API_KEY and not config.GEMINI_API_KEY:
        console.print("[bold red]Error: OPENAI_API_KEY or GEMINI_API_KEY required for extraction/embeddings.[/bold red]")
        sys.exit(1)

    db = LocalSQLiteConnector()
    
    if args.daemon:
        console.print(f"[bold yellow]Running in DAEMON mode. Polling every {args.interval} seconds with limit {args.limit}...[/bold yellow]")
        while True:
            await run_pipeline(db, limit=args.limit)
            console.print(f"[dim]Sleeping for {args.interval} seconds...[/dim]")
            await asyncio.sleep(args.interval)
    else:
        await run_pipeline(db, limit=args.limit)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold red]Daemon interrupted by user.[/bold red]")
        sys.exit(0)
