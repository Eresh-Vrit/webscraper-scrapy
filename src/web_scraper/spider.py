from urllib.parse import urljoin, urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor


def _same_site(url: str, allowed_domain: str) -> bool:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    base = allowed_domain.lower().removeprefix("www.")
    return host == base or host.endswith("." + base)


class SiteSpider(scrapy.Spider):
    name = "site"

    def __init__(self, start_url, allowed_domain, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.allowed_domains = [allowed_domain]
        self._link_extractor = LinkExtractor()

    def parse(self, response):
        content_type = response.headers.get("Content-Type", b"").decode(errors="ignore")
        if "text/html" not in content_type:
            return

        title = response.css("title::text").get(default="").strip()
        meta_description = response.css(
            'meta[name="description"]::attr(content)'
        ).get(default="").strip()

        headings = {
            f"h{i}": [
                h.strip()
                for h in response.css(f"h{i} ::text, h{i}::text").getall()
                if h.strip()
            ]
            for i in (1, 2, 3)
        }

        internal_links, external_links = set(), set()
        for link in self._link_extractor.extract_links(response):
            target = internal_links if _same_site(link.url, self.allowed_domains[0]) else external_links
            target.add(link.url)

        forms = []
        for form in response.css("form"):
            forms.append({
                "action": urljoin(response.url, form.attrib.get("action", "")),
                "method": form.attrib.get("method", "get").upper(),
                "inputs": [
                    {"name": inp.attrib.get("name"), "type": inp.attrib.get("type", "text")}
                    for inp in form.css("input")
                    if inp.attrib.get("name")
                ],
            })

        images = sorted({
            urljoin(response.url, src)
            for src in response.css("img::attr(src)").getall()
        })

        text_nodes = response.xpath(
            "//body//text()[not(ancestor::script) and not(ancestor::style)]"
        ).getall()
        text = " ".join(t.strip() for t in text_nodes if t.strip())

        yield {
            "url": response.url,
            "status": response.status,
            "depth": response.meta.get("depth", 0),
            "title": title,
            "meta_description": meta_description,
            "headings": headings,
            "internal_links": sorted(internal_links),
            "external_links": sorted(external_links),
            "forms": forms,
            "images": images,
            "word_count": len(text.split()),
            "text": text,
        }

        for link in internal_links:
            yield response.follow(link, callback=self.parse)
