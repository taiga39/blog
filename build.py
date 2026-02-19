#!/usr/bin/env python3
"""Minimal Markdown blog generator. No dependencies."""

import os
import re
import html
from datetime import datetime
from pathlib import Path

POSTS_DIR = Path(__file__).parent / "posts"
DIST_DIR = Path(__file__).parent / "docs"
SITE_TITLE = "taiga"
SITE_DESCRIPTION = "Tech blog by taiga39"
SITE_AUTHOR = "taiga39"


# --- Markdown parser ---

def parse_frontmatter(text):
    m = re.match(r"^---\n(.+?)\n---\n?(.*)", text, re.DOTALL)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    return meta, m.group(2)


def md_to_html(md):
    lines = md.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Fenced code block
        if line.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(html.escape(lines[i]))
                i += 1
            i += 1  # skip closing ```
            out.append(f'<pre><code>{chr(10).join(code_lines)}</code></pre>')
            continue

        # Headings
        hm = re.match(r"^(#{1,6})\s+(.+)$", line)
        if hm:
            level = len(hm.group(1))
            out.append(f"<h{level}>{inline(hm.group(2))}</h{level}>")
            i += 1
            continue

        # Unordered list
        if re.match(r"^[\-\*]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^[\-\*]\s+", lines[i]):
                items.append(f"<li>{inline(re.sub(r'^[\-\*]\s+', '', lines[i]))}</li>")
                i += 1
            out.append(f'<ul>{"".join(items)}</ul>')
            continue

        # Ordered list
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                items.append(f"<li>{inline(re.sub(r'^\d+\.\s+', '', lines[i]))}</li>")
                i += 1
            out.append(f'<ol>{"".join(items)}</ol>')
            continue

        # Horizontal rule
        if re.match(r"^(---|\*\*\*|___)$", line.strip()):
            out.append("<hr>")
            i += 1
            continue

        # Blockquote
        if line.startswith(">"):
            bq_lines = []
            while i < len(lines) and lines[i].startswith(">"):
                bq_lines.append(inline(re.sub(r"^>\s?", "", lines[i])))
                i += 1
            out.append(f'<blockquote><p>{"<br>".join(bq_lines)}</p></blockquote>')
            continue

        # Blank line
        if line.strip() == "":
            i += 1
            continue

        # Paragraph: collect consecutive non-empty lines
        para = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("```", "#", ">", "- ", "* ")):
            if re.match(r"^\d+\.\s+", lines[i]):
                break
            if re.match(r"^(---|\*\*\*|___)$", lines[i].strip()):
                break
            para.append(lines[i])
            i += 1
        out.append(f"<p>{inline(chr(10).join(para))}</p>")

    return "\n".join(out)


def inline(text):
    text = html.escape(text)
    # inline code
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # links
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    # images
    text = re.sub(r"!\[(.+?)\]\((.+?)\)", r'<img src="\2" alt="\1">', text)
    return text


# --- Templates ---

def format_date(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%b %d, %Y").replace(" 0", " ")

INDEX_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{site_description}">
  <meta name="author" content="{site_author}">
  <meta property="og:title" content="{site_title}">
  <meta property="og:description" content="{site_description}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{site_title}">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{site_title}">
  <meta name="twitter:description" content="{site_description}">
  <title>{site_title}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: Georgia, "Times New Roman", serif;
      background: #f5f4f0;
      color: #2c2c2c;
      line-height: 1.9;
    }}
    .container {{ max-width: 640px; margin: 0 auto; padding: 80px 20px 120px; }}
    h1 {{ font-size: 1.4rem; font-weight: 400; margin-bottom: 60px; }}
    .post {{ margin-bottom: 48px; }}
    .post-date {{ font-size: 0.72rem; color: #999; letter-spacing: 0.06em; }}
    .post-title a {{ font-size: 1rem; color: #2c2c2c; text-decoration: none; }}
    .post-title a:hover {{ color: #888; }}
    .post-excerpt {{ font-size: 0.85rem; color: #777; margin-top: 6px; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>{site_title}</h1>
{posts}
  </div>
</body>
</html>"""

POST_ENTRY = """\
    <div class="post">
      <div class="post-date">{date}</div>
      <div class="post-title"><a href="{slug}.html">{title}</a></div>
      <p class="post-excerpt">{excerpt}</p>
    </div>"""

ARTICLE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{excerpt}">
  <meta name="author" content="{site_author}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{excerpt}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="{site_title}">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{excerpt}">
  <title>{title}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: Georgia, "Times New Roman", serif;
      background: #f5f4f0;
      color: #2c2c2c;
      line-height: 1.9;
    }}
    .container {{ max-width: 640px; margin: 0 auto; padding: 80px 20px 120px; }}
    .back {{ font-size: 0.8rem; color: #999; text-decoration: none; }}
    .back:hover {{ color: #2c2c2c; }}
    .date {{ font-size: 0.72rem; color: #999; letter-spacing: 0.06em; margin-top: 60px; }}
    h1 {{ font-size: 1.3rem; font-weight: 400; margin-top: 8px; margin-bottom: 48px; }}
    .body p {{ margin-bottom: 1.6em; font-size: 0.92rem; }}
    .body pre {{ background: #eae9e5; padding: 16px 20px; margin-bottom: 1.6em; overflow-x: auto; border-radius: 4px; }}
    .body code {{ font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 0.84rem; }}
    .body p code {{ background: #eae9e5; padding: 2px 6px; border-radius: 3px; }}
    .body blockquote {{ border-left: 2px solid #ccc; padding-left: 16px; color: #666; margin-bottom: 1.6em; }}
    .body ul, .body ol {{ margin-bottom: 1.6em; padding-left: 1.4em; font-size: 0.92rem; }}
    .body li {{ margin-bottom: 0.4em; }}
    .body h2 {{ font-size: 1.1rem; font-weight: 400; margin: 2em 0 0.8em; }}
    .body h3 {{ font-size: 1rem; font-weight: 600; margin: 1.6em 0 0.6em; }}
    .body hr {{ border: none; border-top: 1px solid #ddd; margin: 2em 0; }}
    .body img {{ max-width: 100%; height: auto; margin-bottom: 1.6em; }}
  </style>
</head>
<body>
  <div class="container">
    <a href="index.html" class="back">&larr; Index</a>

    <div class="date">{date}</div>
    <h1>{title}</h1>

    <div class="body">
{body}
    </div>
  </div>
</body>
</html>"""


# --- Build ---

def build():
    DIST_DIR.mkdir(exist_ok=True)

    posts = []
    for f in sorted(POSTS_DIR.glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        meta, body_md = parse_frontmatter(raw)
        slug = f.stem
        body_html = md_to_html(body_md.strip())
        date_fmt = format_date(meta["date"])

        posts.append({
            "slug": slug,
            "title": meta["title"],
            "date": meta["date"],
            "date_fmt": date_fmt,
            "excerpt": meta.get("excerpt", ""),
            "body": body_html,
        })

    # Sort by date descending
    posts.sort(key=lambda p: p["date"], reverse=True)

    # Write article pages
    for p in posts:
        article = ARTICLE_TEMPLATE.format(
            title=html.escape(p["title"]),
            date=p["date_fmt"],
            body=p["body"],
            excerpt=html.escape(p["excerpt"]),
            site_title=SITE_TITLE,
            site_author=SITE_AUTHOR,
        )
        (DIST_DIR / f'{p["slug"]}.html').write_text(article, encoding="utf-8")

    # Write index
    entries = "\n".join(
        POST_ENTRY.format(
            date=p["date_fmt"],
            slug=p["slug"],
            title=html.escape(p["title"]),
            excerpt=html.escape(p["excerpt"]),
        )
        for p in posts
    )
    index = INDEX_TEMPLATE.format(
        site_title=SITE_TITLE,
        site_description=SITE_DESCRIPTION,
        site_author=SITE_AUTHOR,
        posts=entries,
    )
    (DIST_DIR / "index.html").write_text(index, encoding="utf-8")

    print(f"Built {len(posts)} posts -> dist/")


if __name__ == "__main__":
    build()
