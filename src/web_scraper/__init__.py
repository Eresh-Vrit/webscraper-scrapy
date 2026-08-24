import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse

from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher

from web_scraper.report import build_report
from web_scraper.spider import SiteSpider


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crawl every route of a website and export the scraped data to a Markdown file."
    )
    parser.add_argument("url", help="Start URL to crawl, e.g. https://example.com")
    parser.add_argument("-o", "--output", help="Output markdown file path (default: <domain>_scrape.md)")
    parser.add_argument("--max-pages", type=int, default=200, help="Max pages to crawl (default: 200)")
    parser.add_argument("--depth", type=int, default=5, help="Max link depth to follow (default: 5)")
    parser.add_argument("--delay", type=float, default=0.25, help="Delay between requests in seconds (default: 0.25)")
    parser.add_argument("--ignore-robots", action="store_true", help="Ignore robots.txt (respected by default)")
    args = parser.parse_args()

    start_url = args.url
    if not urlparse(start_url).scheme:
        start_url = "https://" + start_url
    domain = urlparse(start_url).netloc

    pages = []

    def collect_item(item, response, spider):
        pages.append(item)

    dispatcher.connect(collect_item, signal=signals.item_scraped)

    process = CrawlerProcess(settings={
        "ROBOTSTXT_OBEY": not args.ignore_robots,
        "LOG_LEVEL": "INFO",
        "USER_AGENT": "web-scraper-bot/0.1 (route crawler; local use)",
        "DEPTH_LIMIT": args.depth,
        "CLOSESPIDER_PAGECOUNT": args.max_pages,
        "AUTOTHROTTLE_ENABLED": True,
        "DOWNLOAD_DELAY": args.delay,
    })
    process.crawl(SiteSpider, start_url=start_url, allowed_domain=domain)
    process.start()

    if not pages:
        print("No pages were scraped. Check the URL and robots.txt settings.")
        sys.exit(1)

    report = build_report(pages, start_url)
    output_path = Path(args.output) if args.output else Path(f"{domain.replace('.', '_')}_scrape.md")
    output_path.write_text(report, encoding="utf-8")

    print(f"Scraped {len(pages)} pages. Report written to {output_path.resolve()}")
