"""
Gerador estático do blog do Mokusai Dojo.

Junta os templates (tools/templates/) com o conteúdo de cada post
(tools/content/posts/) e escreve os arquivos finais em /blog/.
Não depende de nada além da biblioteca padrão do Python.

Uso: python3 tools/build_blog.py
"""
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(ROOT, "tools", "templates")
POSTS_CONTENT = os.path.join(ROOT, "tools", "content", "posts")
BLOG_OUT = os.path.join(ROOT, "blog")
SITE_URL = "https://mokusai.com.br"

# Ordem: mais recente primeiro.
POSTS = [
    {
        "slug": "primeira-aula-de-aikido",
        "title": "O que esperar da sua primeira aula de Aikido",
        "excerpt": "Alongamento, rolamentos, pegadas básicas e as primeiras técnicas de projeção e imobilização: veja como funciona a estrutura de uma aula para quem está começando.",
        "meta_description": "Entenda como é a estrutura de uma primeira aula de Aikido no Mokusai Dojo: aquecimento, rolamentos (ukemi), liberação de pegadas e técnicas básicas.",
        "category": "Primeiros Passos",
        "date_iso": "2026-08-17",
        "date_label": "17 de agosto de 2026",
        "author": "Sensei Felipe Alberto",
        "cover": "/assets/img/sobre-tatame.jpg",
        "cover_alt": "Tatame de treino do Mokusai Dojo",
        "body_file": "primeira-aula-de-aikido.html",
    },
]


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def render(template, values):
    out = template
    for key, val in values.items():
        out = out.replace("{{" + key + "}}", val)
    return out


def build():
    header = read(os.path.join(TEMPLATES, "header.html"))
    footer = read(os.path.join(TEMPLATES, "footer.html"))
    post_tpl = read(os.path.join(TEMPLATES, "post.html"))
    index_tpl = read(os.path.join(TEMPLATES, "blog_index.html"))

    if os.path.isdir(BLOG_OUT):
        shutil.rmtree(BLOG_OUT)

    cards = []
    for post in POSTS:
        body = read(os.path.join(POSTS_CONTENT, post["body_file"]))
        canonical = f"{SITE_URL}/blog/{post['slug']}/"
        og_image = post["cover"] if post["cover"].startswith("http") else f"{SITE_URL}{post['cover']}"

        page = render(post_tpl, {
            "TITLE": f"{post['title']} — Blog Mokusai Dojo",
            "META_DESCRIPTION": post["meta_description"],
            "CANONICAL": canonical,
            "POST_TITLE": post["title"],
            "OG_IMAGE": og_image,
            "CATEGORY": post["category"],
            "DATE_ISO": post["date_iso"],
            "DATE_LABEL": post["date_label"],
            "AUTHOR": post["author"],
            "COVER_IMG": post["cover"],
            "COVER_ALT": post["cover_alt"],
            "BODY": body,
            "HEADER": header,
            "FOOTER": footer,
        })
        write(os.path.join(BLOG_OUT, post["slug"], "index.html"), page)

        cards.append(f'''        <a class="post-card reveal" href="/blog/{post['slug']}/">
          <div class="post-card__media">
            <img src="{post['cover']}" alt="{post['cover_alt']}" loading="lazy" width="800" height="500">
          </div>
          <div class="post-card__body">
            <p class="post-card__meta">{post['category']} · {post['date_label']}</p>
            <h2>{post['title']}</h2>
            <p>{post['excerpt']}</p>
            <span class="post-card__link">Ler mais
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
            </span>
          </div>
        </a>''')

    index_page = render(index_tpl, {
        "HEADER": header,
        "FOOTER": footer,
        "POST_CARDS": "\n".join(cards),
    })
    write(os.path.join(BLOG_OUT, "index.html"), index_page)

    update_sitemap()
    print(f"Blog gerado: {len(POSTS)} post(s) em {BLOG_OUT}")


def update_sitemap():
    """Reescreve sitemap.xml com a home, a listagem do blog e cada post."""
    sitemap_path = os.path.join(ROOT, "sitemap.xml")
    today = max(p["date_iso"] for p in POSTS) if POSTS else "2026-08-17"

    urls = [
        (f"{SITE_URL}/", today, "monthly", "1.0"),
        (f"{SITE_URL}/blog/", today, "weekly", "0.8"),
    ]
    for post in POSTS:
        urls.append((f"{SITE_URL}/blog/{post['slug']}/", post["date_iso"], "monthly", "0.6"))

    entries = "\n".join(
        f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lastmod}</lastmod>\n"
        f"    <changefreq>{freq}</changefreq>\n    <priority>{priority}</priority>\n  </url>"
        for loc, lastmod, freq, priority in urls
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n"
    )
    write(sitemap_path, xml)


if __name__ == "__main__":
    build()
