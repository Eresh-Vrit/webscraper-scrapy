import re

API_HINTS = ("/api/", "/v1/", "/v2/", ".json", "/graphql")


def _anchor(url: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", url.lower()).strip("-")


def _looks_like_api(url: str) -> bool:
    return any(hint in url.lower() for hint in API_HINTS)


def _page_section(page: dict) -> list[str]:
    lines = [f"### {page['url']}", ""]
    lines.append(f"- **Status:** {page['status']}")
    lines.append(f"- **Depth:** {page['depth']}")
    if page["title"]:
        lines.append(f"- **Title:** {page['title']}")
    if page["meta_description"]:
        lines.append(f"- **Meta description:** {page['meta_description']}")
    lines.append(f"- **Word count:** {page['word_count']}")
    lines.append("")

    heading_lines = [
        f"**{level.upper()}:** " + "; ".join(page["headings"][level])
        for level in ("h1", "h2", "h3")
        if page["headings"].get(level)
    ]
    if heading_lines:
        lines.extend(heading_lines)
        lines.append("")

    if page["forms"]:
        lines.append("**Forms:**")
        for form in page["forms"]:
            input_desc = ", ".join(f"{i['name']} ({i['type']})" for i in form["inputs"])
            lines.append(f"- `{form['method']}` {form['action']} — inputs: {input_desc or 'none'}")
        lines.append("")

    if page["internal_links"]:
        lines.append(f"**Internal links ({len(page['internal_links'])}):**")
        lines.extend(f"- {link}" for link in page["internal_links"])
        lines.append("")

    if page["external_links"]:
        lines.append(f"**External links ({len(page['external_links'])}):**")
        lines.extend(f"- {link}" for link in page["external_links"])
        lines.append("")

    if page["images"]:
        shown = page["images"][:50]
        lines.append(f"**Images ({len(page['images'])}):**")
        lines.extend(f"- {img}" for img in shown)
        if len(page["images"]) > 50:
            lines.append(f"- ...and {len(page['images']) - 50} more")
        lines.append("")

    if page["text"]:
        lines.append("**Page text:**")
        lines.append("")
        lines.append("```")
        lines.append(page["text"][:5000] + ("..." if len(page["text"]) > 5000 else ""))
        lines.append("```")
        lines.append("")

    lines.append("---")
    lines.append("")
    return lines


def build_report(pages: list[dict], start_url: str) -> str:
    lines = [f"# Site Scrape Report", "", f"- **Start URL:** {start_url}", f"- **Pages crawled:** {len(pages)}", ""]

    lines.append("## Discovered Routes")
    lines.append("")
    for i, page in enumerate(sorted(pages, key=lambda p: p["url"]), 1):
        lines.append(f"{i}. [{page['url']}](#{_anchor(page['url'])}) — status {page['status']}")
    lines.append("")

    api_like = sorted({
        link
        for p in pages
        for link in (*p["internal_links"], *(f["action"] for f in p["forms"]))
        if _looks_like_api(link)
    })
    if api_like:
        lines.append("## Potential API Endpoints")
        lines.append("")
        lines.extend(f"- {link}" for link in api_like)
        lines.append("")

    lines.append("## Pages")
    lines.append("")
    for page in pages:
        lines.extend(_page_section(page))

    return "\n".join(lines)
