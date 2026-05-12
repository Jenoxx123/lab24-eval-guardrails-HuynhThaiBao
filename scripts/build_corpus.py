from __future__ import annotations

import argparse
import re
import textwrap
from pathlib import Path
from types import SimpleNamespace

try:
    from langchain_community.document_loaders import WikipediaLoader
except Exception:
    WikipediaLoader = None

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

import requests


TOPICS = [
    "RAG architecture",
    "Chunking strategies",
    "Embedding models",
    "Retriever tuning",
    "Hybrid search",
    "Re-ranking",
    "Prompt grounding",
    "Hallucination control",
    "Evaluation metrics",
    "Latency optimization",
    "Caching patterns",
    "Guardrail layers",
]


def build_doc(topic: str, idx: int) -> str:
    base = f"""
    # {topic} - Note {idx:02d}

    ## Problem framing
    Retrieval-Augmented Generation (RAG) systems combine a retriever and a generator.
    In production, the key challenge is balancing factuality, recall, latency, and cost.
    Teams usually define SLOs for faithfulness, answer relevance, and response latency.

    ## Design choices
    A common baseline starts with semantic chunking, dense embeddings, top-k retrieval, and a concise answer prompt.
    Better performance often requires hybrid retrieval (BM25 plus vector), query rewriting, and reranking.
    Systems should avoid over-retrieval because extra context can reduce precision and increase latency.

    ## Failure patterns
    Frequent failures include missing key context, conflicting evidence across documents, stale index snapshots,
    and prompts that encourage speculation. Multi-hop questions expose shallow retrieval pipelines quickly.
    A robust evaluation loop should include synthetic and human-validated samples.

    ## Guardrails
    Input filtering should detect PII and off-topic requests. Output filtering should detect unsafe or policy-breaking
    responses before returning content to users. Audit logging should be asynchronous to avoid latency penalties.

    ## Operational guidance
    Track P50, P95, and P99 latency by layer. Evaluate retriever and generator separately to isolate bottlenecks.
    Run periodic drift checks after corpus updates. Keep experiment metadata so results are reproducible.

    ## Example scenario
    A support chatbot receives a query about policy updates. The retriever selects top-5 chunks,
    reranker promotes relevant passages, and the model answers with citations. If the safety classifier marks output
    as unsafe or high-risk, return a refusal template and log the incident.
    """
    return textwrap.dedent(base).strip() + "\n"


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-") or "doc"


def write_doc(path: Path, title: str, body: str, source: str) -> None:
    content = f"# {title}\n\nSource: {source}\n\n{body.strip()}\n"
    path.write_text(content, encoding="utf-8")


def download_wikipedia_pages(topics: list[str], max_docs_per_topic: int = 5, lang: str = "en") -> list:
    """
    Tải các trang Wikipedia theo danh sách topics.
    Trả về list Document (LangChain).
    """
    print(f"[Data Loader] Bat dau tai Wikipedia cho topics: {topics}")
    all_docs = []
    use_langchain = WikipediaLoader is not None
    for topic in topics:
        print(f"[Data Loader] Dang tai topic: '{topic}'...")
        if use_langchain:
            try:
                loader = WikipediaLoader(query=topic, load_max_docs=max_docs_per_topic, lang=lang)
                docs = loader.load()
                print(f"[Data Loader] Da tai {len(docs)} bai cho topic '{topic}' (LangChain).")
                all_docs.extend(docs)
                continue
            except Exception as exc:
                print(f"[Data Loader] LangChain loader failed for '{topic}': {exc}")

        # Fallback: MediaWiki API
        try:
            docs = download_wikipedia_pages_api(topic=topic, max_docs=max_docs_per_topic, lang=lang)
            print(f"[Data Loader] Da tai {len(docs)} bai cho topic '{topic}' (API fallback).")
            all_docs.extend(docs)
        except Exception as exc:
            print(f"[Data Loader] Loi topic '{topic}' via API: {exc}")
    print(f"[Data Loader] Tong so bai Wikipedia: {len(all_docs)}")
    return all_docs


def download_wikipedia_pages_api(topic: str, max_docs: int = 5, lang: str = "en") -> list:
    api = f"https://{lang}.wikipedia.org/w/api.php"
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": topic,
        "srlimit": max_docs,
        "format": "json",
    }
    sresp = requests.get(api, params=search_params, timeout=30)
    sresp.raise_for_status()
    titles = [item["title"] for item in sresp.json().get("query", {}).get("search", [])]

    docs = []
    for title in titles:
        extract_params = {
            "action": "query",
            "prop": "extracts",
            "explaintext": 1,
            "titles": title,
            "format": "json",
        }
        eresp = requests.get(api, params=extract_params, timeout=30)
        eresp.raise_for_status()
        pages = eresp.json().get("query", {}).get("pages", {})
        for _, page in pages.items():
            text = (page.get("extract") or "").strip()
            if not text:
                continue
            docs.append(
                SimpleNamespace(
                    page_content=text,
                    metadata={
                        "title": title,
                        "source": f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}",
                    },
                )
            )
    return docs


def build_from_wikipedia(docs_dir: Path, topics: list[str], max_docs_per_topic: int, lang: str) -> int:
    docs = download_wikipedia_pages(topics=topics, max_docs_per_topic=max_docs_per_topic, lang=lang)
    created = 0
    for i, doc in enumerate(docs, start=1):
        title = str(doc.metadata.get("title", f"wiki_{i}"))
        source = str(doc.metadata.get("source", "wikipedia"))
        filename = f"wiki_{i:03d}_{slugify(title)[:70]}.md"
        write_doc(docs_dir / filename, title=title, body=doc.page_content, source=source)
        created += 1
    return created


def build_from_day18(docs_dir: Path, day18_data_dir: Path) -> int:
    created = 0
    if not day18_data_dir.exists():
        print(f"[Data Loader] Day18 data dir not found: {day18_data_dir}")
        return 0

    for ext in ("*.md", "*.txt"):
        for src in sorted(day18_data_dir.glob(ext)):
            text = src.read_text(encoding="utf-8", errors="ignore")
            dst = docs_dir / f"day18_{slugify(src.stem)}.md"
            write_doc(dst, title=src.stem, body=text, source=str(src))
            created += 1

    if PdfReader is None:
        print("[Data Loader] pypdf unavailable. Skip PDF extraction.")
        return created

    for pdf in sorted(day18_data_dir.glob("*.pdf")):
        try:
            reader = PdfReader(str(pdf))
            for pidx, page in enumerate(reader.pages, start=1):
                text = (page.extract_text() or "").strip()
                if not text:
                    continue
                dst = docs_dir / f"day18_{slugify(pdf.stem)}_p{pidx:03d}.md"
                write_doc(
                    dst,
                    title=f"{pdf.stem} - Page {pidx}",
                    body=text,
                    source=f"{pdf}#page={pidx}",
                )
                created += 1
        except Exception as exc:
            print(f"[Data Loader] Loi doc PDF {pdf.name}: {exc}")
    return created


def build_synthetic(docs_dir: Path, count: int = 60) -> int:
    created = 0
    for i in range(1, count + 1):
        topic = TOPICS[(i - 1) % len(TOPICS)]
        path = docs_dir / f"rag_note_{i:03d}.md"
        path.write_text(build_doc(topic, i), encoding="utf-8")
        created += 1
    return created


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build corpus for Lab 24.")
    parser.add_argument(
        "--sources",
        default="day18,wikipedia,synthetic",
        help="Comma-separated sources: day18,wikipedia,synthetic",
    )
    parser.add_argument(
        "--topics",
        default="Artificial intelligence,Machine learning,Deep learning,Large language model",
        help="Comma-separated Wikipedia topics.",
    )
    parser.add_argument("--max-docs-per-topic", type=int, default=5)
    parser.add_argument("--lang", default="en")
    parser.add_argument("--synthetic-count", type=int, default=60)
    parser.add_argument(
        "--day18-data-dir",
        default=r"C:\assignments-main\Day 18\C401_B2_Day18\data",
        help="Path to Day 18 data directory.",
    )
    parser.add_argument("--reset-docs", action="store_true", help="Delete docs/*.md before building.")
    parser.add_argument("--output-dir", default="docs", help="Output corpus directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    docs_dir = Path(args.output_dir)
    docs_dir.mkdir(parents=True, exist_ok=True)

    if args.reset_docs:
        for f in docs_dir.glob("*.md"):
            try:
                f.chmod(0o666)
                f.unlink()
            except Exception as exc:
                print(f"[Data Loader] Skip delete {f.name}: {exc}")
        print("[Data Loader] Cleared docs/*.md")

    selected_sources = [s.strip().lower() for s in args.sources.split(",") if s.strip()]
    topics = [t.strip() for t in args.topics.split(",") if t.strip()]

    total = 0
    if "day18" in selected_sources:
        count = build_from_day18(docs_dir=docs_dir, day18_data_dir=Path(args.day18_data_dir))
        print(f"[Data Loader] Day18 docs created: {count}")
        total += count

    if "wikipedia" in selected_sources:
        count = build_from_wikipedia(
            docs_dir=docs_dir,
            topics=topics,
            max_docs_per_topic=args.max_docs_per_topic,
            lang=args.lang,
        )
        print(f"[Data Loader] Wikipedia docs created: {count}")
        total += count

    if "synthetic" in selected_sources:
        count = build_synthetic(docs_dir=docs_dir, count=args.synthetic_count)
        print(f"[Data Loader] Synthetic docs created: {count}")
        total += count

    print(f"[Data Loader] Total docs created: {total}")
    print(f"[Data Loader] Output dir: {docs_dir.resolve()}")


if __name__ == "__main__":
    main()
