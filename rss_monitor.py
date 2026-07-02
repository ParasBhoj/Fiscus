import feedparser
import requests
import re
from datetime import datetime
from dateutil import parser as date_parser
from dateutil.tz import gettz
from html import unescape
from typing import List, Dict, Any

INDIA_ZONE = gettz('Asia/Kolkata')

FEEDS = [
    {"source": "RBI", "kind": "press-releases", "url": "https://rbi.org.in/pressreleases_rss.xml", "verify_tls": True},
    {"source": "SEBI", "kind": "all-updates", "url": "https://www.sebi.gov.in/sebirss.xml", "verify_tls": False}
]

def strip_html(html_str: str) -> str:
    if not html_str:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', html_str)
    return text

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unescape(text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove BOM and non-breaking spaces
    text = text.replace('\uFEFF', ' ').replace('\u00A0', ' ')
    return text.strip()

def parse_published_at(raw_date: str) -> str:
    if not raw_date:
        return ""
    try:
        # Use python-dateutil for robust parsing
        dt = date_parser.parse(raw_date)
        # If naive, assume IST
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=INDIA_ZONE)
        return dt.isoformat()
    except Exception as e:
        return ""

def fetch_rss_feed(feed_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = []
    try:
        # Fetch using requests to handle TLS issues if needed
        response = requests.get(
            feed_config["url"], 
            headers={"User-Agent": "Antigravity/1.0"}, 
            verify=feed_config["verify_tls"],
            timeout=15
        )
        response.raise_for_status()
        
        # Parse the raw XML content with feedparser
        feed = feedparser.parse(response.content)
        
        channel_title = feed.feed.get("title", "")
        
        for entry in feed.entries:
            title = normalize_text(entry.get("title", ""))
            summary_raw = entry.get("summary", entry.get("description", ""))
            summary = normalize_text(strip_html(summary_raw))
            link = normalize_text(entry.get("link", ""))
            raw_published_at = entry.get("published", entry.get("updated", ""))
            published_at = parse_published_at(raw_published_at)
            
            # Create a unique ID
            entry_id = normalize_text(entry.get("id", ""))
            if not entry_id:
                entry_id = link if link else f"{feed_config['source']}:{title}"
                
            results.append({
                "source": feed_config["source"],
                "feedKind": feed_config["kind"],
                "channelTitle": channel_title,
                "title": title,
                "summary": summary,
                "url": link,
                "id": entry_id,
                "rawPublishedAt": raw_published_at,
                "publishedAt": published_at
            })
    except Exception as e:
        print(f"[!] Error fetching feed {feed_config['source']}: {e}")
        
    return results

def get_all_latest_updates() -> List[Dict[str, Any]]:
    import urllib3
    # Suppress InsecureRequestWarning for SEBI
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    all_updates = []
    for feed in FEEDS:
        all_updates.extend(fetch_rss_feed(feed))
    return all_updates

if __name__ == "__main__":
    updates = get_all_latest_updates()
    print(f"Fetched {len(updates)} updates from feeds.")
    if updates:
        print("Sample update:")
        import json
        print(json.dumps(updates[0], indent=2))
