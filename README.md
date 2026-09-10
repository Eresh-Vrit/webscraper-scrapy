# web-scraper

Crawls every route of a website starting from a given URL and writes the
discovered routes and scraped page data to a single Markdown report.

## Usage

```bash
Installation
uv sync
```

```bash
To run:
uv run web-scraper https://example.com
```

Options:

- `-o, --output` — output markdown file path (default: `<domain>_scrape.md`)
- `--max-pages` — max pages to crawl (default: 200)
- `--depth` — max link depth to follow (default: 5)
- `--delay` — delay between requests in seconds (default: 0.25)
- `--ignore-robots` — ignore robots.txt (respected by default)

For each page the report includes: status code, title, meta description,
headings, page text, internal/external links, forms (with inputs), and
images. It also lists all discovered routes and any links that look like API
endpoints.
