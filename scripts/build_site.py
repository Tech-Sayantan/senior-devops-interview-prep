"""Build the public study site from the repository's Markdown notes."""

import argparse
from dataclasses import dataclass
from html import escape
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
from string import Template
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit, urlunsplit
from xml.etree import ElementTree

from markdown import Markdown
from markdown.extensions import Extension
from markdown.extensions.toc import slugify
from markdown.treeprocessors import Treeprocessor


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site"
REPOSITORY = "https://github.com/Tech-Sayantan/senior-devops-interview-prep"
BUILD_MARKER = ".study-site-output"


@dataclass(frozen=True)
class Page:
    source: PurePosixPath
    route: str
    title: str
    preface: str
    body: str
    day: int | None


def load_page(source: PurePosixPath, route: str, day: int | None = None) -> Page:
    text = (ROOT / source).read_text(encoding="utf-8")
    heading = re.search(r"^# (\S[^\n]*)$", text, re.MULTILINE)
    if heading is None or not text[heading.end():].strip():
        raise ValueError(f"{source} must include a Markdown title followed by a body.")
    return Page(
        source, route, heading[1].strip(), text[:heading.start()].strip(),
        text[heading.end():], day
    )


def load_lessons() -> dict[int, Page]:
    lessons = {}
    for path in sorted((ROOT / "days").glob("day-*.md")):
        match = re.fullmatch(r"day-(\d+)(?:-[a-z0-9-]+)?", path.stem)
        if not match:
            raise ValueError(f"Invalid lesson filename: {path.name}")
        day = int(match[1])
        if day in lessons:
            raise ValueError(f"There is more than one lesson for Day {day}.")
        route = f"days/{path.stem}"
        lessons[day] = load_page(PurePosixPath(f"{route}.md"), route, day)
    if not lessons:
        raise ValueError("At least one lesson is needed to build the site.")
    return dict(sorted(lessons.items()))


def page_link(current: Page, destination: str) -> str:
    return f"{posixpath.relpath(destination, current.route)}/"


def section_id(value: str, separator: str) -> str:
    return slugify(re.sub(r"[\u2010-\u2015]", "-", value), separator)


class NoteLinks(Treeprocessor):
    def __init__(self, parser, page, routes, lessons):
        super().__init__(parser)
        self.page = page
        self.routes = routes
        self.lessons = lessons

    def run(self, root):
        for link in root.iter("a"):
            parts = urlsplit(link.get("href", ""))
            if parts.scheme or parts.netloc or parts.path.startswith("/"):
                continue
            path = posixpath.normpath(posixpath.join(
                self.page.source.parent.as_posix(), unquote(parts.path)
            ))
            if path in self.routes:
                destination = page_link(self.page, self.routes[path])
                link.set("href", urlunsplit(("", "", destination, parts.query, parts.fragment)))

        if self.page.day is None:
            self.link_published_lessons(root)

    def link_published_lessons(self, root):
        for row in root.iter("tr"):
            cells = row.findall("td")
            if len(cells) < 2:
                continue
            number = (cells[0].text or "").strip()
            heading = cells[1].find("strong")
            if not number.isdecimal() or heading is None or len(heading):
                continue
            lesson = self.lessons.get(int(number))
            if lesson and heading.text:
                link = ElementTree.SubElement(heading, "a", href=page_link(self.page, lesson.route))
                link.text, heading.text = heading.text, None


class NoteLinksExtension(Extension):
    def __init__(self, page, routes, lessons):
        super().__init__()
        self.page = page
        self.routes = routes
        self.lessons = lessons

    def extendMarkdown(self, parser):
        parser.treeprocessors.register(
            NoteLinks(parser, self.page, self.routes, self.lessons), "note_links", 8
        )


def reader_code_block(match: re.Match[str]) -> str:
    if 'class="language-mermaid"' in (match[1] or ""):
        return (
            '<figure class="lesson-diagram" data-mermaid-diagram>'
            '<div class="diagram-view" role="region" aria-label="Diagram" tabindex="0" hidden></div>'
            '<details class="diagram-source"><summary>View diagram source</summary>'
            f'{match[0]}</details></figure>'
        )
    return (
        '<div class="code-block"><button class="code-copy" type="button" '
        f'data-copy-code hidden>Copy</button>{match[0]}</div>'
    )


def reader_markup(markup: str) -> str:
    markup = re.sub(r"<pre><code(\s[^>]*)?>.*?</code></pre>", reader_code_block, markup, flags=re.DOTALL)
    return markup.replace(
        "<table>", '<div class="table-scroll" role="region" aria-label="Study sessions" '
        'tabindex="0"><table>'
    ).replace("</table>", "</table></div>")


def reader_links(page: Page, curriculum: Page, lessons: dict[int, Page]) -> str:
    if page.day is None:
        first = next(iter(lessons.values()))
        return (
            f'<a class="button button-primary" href="{page_link(page, first.route)}">'
            f"Read Day {first.day} <span aria-hidden=\"true\">→</span></a>"
        )

    links = [
        f'<a class="button button-secondary" href="{page_link(page, curriculum.route)}">'
        '<span aria-hidden="true">←</span> Back to curriculum</a>'
    ]
    following = next((lesson for day, lesson in lessons.items() if day > page.day), None)
    if following:
        links.append(
            f'<a class="button button-primary" href="{page_link(page, following.route)}">'
            f"Read Day {following.day} <span aria-hidden=\"true\">→</span></a>"
        )
    return "\n          ".join(links)


def render_page(page, curriculum, lessons, routes, template, output):
    parser = Markdown(
        extensions=["fenced_code", "tables", "toc", NoteLinksExtension(page, routes, lessons)],
        extension_configs={"toc": {"toc_depth": "2-3", "slugify": section_id}},
    )
    preface = ""
    if page.preface:
        preface = f'<div class="article-preface">{reader_markup(parser.convert(page.preface))}</div>'
        parser.reset()
    content = reader_markup(parser.convert(page.body))
    first = next(iter(lessons.values()))
    if page.day is None:
        kicker = "Study plan"
        description = "A 60-day roadmap from cloud fundamentals to production scenarios and mock interviews."
        breadcrumb = ""
    else:
        kicker = "Lesson"
        description = (
            "See a request reach DNS, TCP, TLS, and HTTP, then replay the clues on your Mac."
            if page.day == 1 else ""
        )
        breadcrumb = (
            f'<li><a href="{page_link(page, curriculum.route)}">Curriculum</a></li>'
        )
    destination = output / page.route / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        template.substitute(
            title=escape(page.title),
            preface=preface,
            description=escape(description or page.title),
            subtitle=(
                f'<p class="article-subtitle">{escape(description)}</p>'
                if description and not page.preface else ""
            ),
            kicker=kicker,
            current_label=f"Day {page.day}" if page.day else "Curriculum",
            home=page_link(page, "."),
            curriculum=page_link(page, curriculum.route),
            first_lesson=page_link(page, first.route),
            first_day=first.day,
            curriculum_current=' aria-current="page"' if page == curriculum else "",
            lesson_current=' aria-current="page"' if page == first else "",
            breadcrumb=breadcrumb,
            assets=posixpath.relpath("assets", page.route),
            source_url=f"{REPOSITORY}/blob/main/{page.source.as_posix()}",
            repository=REPOSITORY,
            toc=parser.toc,
            content=content,
            reader_links=reader_links(page, curriculum, lessons),
        ),
        encoding="utf-8",
    )


def build_site(output: Path) -> None:
    if output.exists() and (
        not output.is_dir() or (any(output.iterdir()) and not (output / BUILD_MARKER).is_file())
    ):
        raise ValueError(f"Use an empty directory or a previous study site build: {output}")

    curriculum = load_page(PurePosixPath("60-day-study-plan.md"), "curriculum")
    lessons = load_lessons()
    pages = [curriculum, *lessons.values()]
    routes = {page.source.as_posix(): page.route for page in pages}
    routes["README.md"] = "."
    template = Template((SOURCE / "article.html").read_text(encoding="utf-8"))

    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".study-site-", dir=output.parent) as temporary:
        staging = Path(temporary) / "pages"
        staging.mkdir()
        shutil.copy2(SOURCE / "index.html", staging / "index.html")
        shutil.copytree(SOURCE / "assets", staging / "assets")
        for page in pages:
            render_page(page, curriculum, lessons, routes, template, staging)
        (staging / BUILD_MARKER).touch()
        if output.exists():
            shutil.rmtree(output)
        staging.rename(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    args = parser.parse_args()
    output = args.output.resolve()
    try:
        build_site(output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")
    print(f"Built study site in {output}")


if __name__ == "__main__":
    main()
