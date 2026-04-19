#!/usr/bin/env python3
"""Screen incremental Scopus BibTeX results with an LM Studio OpenAI endpoint.

The script performs two-stage screening for updated SLR candidates:

1. Deterministic prefiltering using publication window and obvious exclusions.
2. LLM-based classification against the review scope.

It preserves accepted BibTeX entries exactly as parsed from the input file and
writes a JSONL audit trail for every processed record.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from openai import OpenAI


DEFAULT_BASE_URL = "https://9b57-193-187-128-87.ngrok-free.app/v1"
DEFAULT_API_KEY = "lm-studio"
DEFAULT_MODEL = "openai/gpt-oss-20b"
DEFAULT_SINCE = date(2025, 2, 1)
DEFAULT_UNTIL = date(2026, 4, 19)
DEFAULT_SCOPUS_JSON = Path("parsifal_scopus_merged.json")

SYSTEM_PROMPT = """You are assisting with title-level and metadata-level screening for a systematic literature review on LLM-based linguistic steganography.

Task:
Classify one paper as INCLUDE, EXCLUDE, or MAYBE using only the metadata provided.

Scope:
We want PRIMARY STUDIES only.
We do NOT want surveys, reviews, editorials, books, book chapters, conference front matter, or generic theory papers.

Include only if the paper is directly about linguistic/text steganography, natural-language watermarking, or closely related information-hiding in text, and language-model methods such as LLMs, GPT, BERT, LLaMA, masked language models, or comparable NLP generation models are central to the method.

Exclude if the paper is mainly about image, video, audio, diffusion-image, multimodal watermarking, model ownership/fingerprinting, federated learning watermarking, malware/code watermarking, or generic AI-generated text detection unless it is clearly a text steganography/watermarking study relevant to the review.

Important:
- Full-text access cannot be verified here. Treat it as unresolved, not as a reason to exclude by itself.
- Be conservative. If relevance is unclear from the metadata, return MAYBE.
- Base the decision on the supplied title, venue, year, type, and DOI only. Do not invent facts.

Return strict JSON only with this schema:
{
  "decision": "include|exclude|maybe",
  "confidence": "high|medium|low",
  "primary_study": true,
  "peer_reviewed_likely": true,
  "llm_relevance": "direct|indirect|none",
  "text_steganography_relevance": "direct|indirect|none",
  "full_text_status": "manual_check_required",
  "reason": "one concise sentence",
  "exclusion_reason": "short label or empty string"
}"""

REPAIR_PROMPT = """Repair the following model output so it becomes valid JSON that exactly matches the required schema. Return JSON only and do not add commentary.

Required schema:
{
  "decision": "include|exclude|maybe",
  "confidence": "high|medium|low",
  "primary_study": true,
  "peer_reviewed_likely": true,
  "llm_relevance": "direct|indirect|none",
  "text_steganography_relevance": "direct|indirect|none",
  "full_text_status": "manual_check_required",
  "reason": "one concise sentence",
  "exclusion_reason": "short label or empty string"
}

Broken output:
{broken_output}
"""

DECISIONS = {"include", "exclude", "maybe"}
CONFIDENCE_LEVELS = {"high", "medium", "low"}
RELEVANCE_LEVELS = {"direct", "indirect", "none"}

NON_PRIMARY_SUBTYPES = {
    "review",
    "short survey",
    "conference review",
    "editorial",
    "note",
    "book",
    "book chapter",
    "letter",
}

FRONT_MATTER_PATTERNS = [
    re.compile(r"^proceedings of\b", re.IGNORECASE),
    re.compile(r"^international conference on\b", re.IGNORECASE),
    re.compile(r"^\d+(st|nd|rd|th)\s+international conference\b", re.IGNORECASE),
    re.compile(r"^satellite workshops held in parallel\b", re.IGNORECASE),
    re.compile(r"\bproceedings\b", re.IGNORECASE),
]

IRRELEVANT_PATTERNS = [
    (re.compile(r"\bimage\b", re.IGNORECASE), "image_scope"),
    (re.compile(r"\bvideo\b", re.IGNORECASE), "video_scope"),
    (re.compile(r"\baudio\b", re.IGNORECASE), "audio_scope"),
    (re.compile(r"\bspeech\b", re.IGNORECASE), "audio_scope"),
    (re.compile(r"\bdiffusion model\b", re.IGNORECASE), "diffusion_scope"),
    (re.compile(r"\btext-to-image\b", re.IGNORECASE), "diffusion_scope"),
    (re.compile(r"\bfederated learning\b", re.IGNORECASE), "federated_learning_scope"),
    (re.compile(r"\bfingerprinting\b", re.IGNORECASE), "model_fingerprinting_scope"),
    (re.compile(r"\bmalware\b", re.IGNORECASE), "malware_scope"),
]

TEXT_RELEVANCE_HINTS = [
    re.compile(r"\btext\b", re.IGNORECASE),
    re.compile(r"\blinguistic\b", re.IGNORECASE),
    re.compile(r"\blanguage model\b", re.IGNORECASE),
    re.compile(r"\bllm\b", re.IGNORECASE),
    re.compile(r"\bgpt\b", re.IGNORECASE),
    re.compile(r"\bbert\b", re.IGNORECASE),
    re.compile(r"\bwatermark(?:ing)?\b", re.IGNORECASE),
    re.compile(r"\bstegan(?:ography|ographic)\b", re.IGNORECASE),
]


@dataclass(slots=True)
class BibEntry:
    entry_type: str
    key: str
    raw_text: str
    fields: dict[str, str]


@dataclass(slots=True)
class ScopusMetadata:
    publication_date: str | None
    subtype_description: str | None
    title: str | None
    doi: str | None


@dataclass(slots=True)
class ScreenDecision:
    decision: str
    confidence: str
    primary_study: bool
    peer_reviewed_likely: bool
    llm_relevance: str
    text_steganography_relevance: str
    full_text_status: str
    reason: str
    exclusion_reason: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Filter incremental Scopus BibTeX results via LM Studio."
    )
    parser.add_argument(
        "--input-bib",
        default="references/parsifal_scopus.bib",
        help="Input BibTeX file to screen.",
    )
    parser.add_argument(
        "--output-bib",
        default="references/parsifal_scopus_filtered_incremental.bib",
        help="Accepted-only BibTeX output path.",
    )
    parser.add_argument(
        "--audit-jsonl",
        default="references/parsifal_scopus_filtered_incremental.jsonl",
        help="JSONL audit output path.",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Base URL for the OpenAI-compatible LM Studio endpoint.",
    )
    parser.add_argument(
        "--api-key",
        default=DEFAULT_API_KEY,
        help="API key passed to the OpenAI client.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Model identifier exposed by the LM Studio endpoint.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature for chat completions.",
    )
    parser.add_argument(
        "--since-date",
        type=parse_iso_date,
        default=DEFAULT_SINCE,
        help="Inclusive lower bound in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--until-date",
        type=parse_iso_date,
        default=DEFAULT_UNTIL,
        help="Inclusive upper bound in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=1,
        help="Number of concurrent LLM classification workers.",
    )
    parser.add_argument(
        "--scopus-json",
        default=str(DEFAULT_SCOPUS_JSON),
        help=(
            "Optional Scopus merged JSON export used to recover publication dates "
            "and subtype metadata when the BibTeX lacks them."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional cap on the number of LLM-screened records, for testing.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and prefilter only without calling the LLM endpoint.",
    )
    return parser.parse_args()


def parse_iso_date(raw: str) -> date:
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid date: {raw}") from exc


def parse_bibtex(path: Path) -> list[BibEntry]:
    content = path.read_text(encoding="utf-8")
    entries: list[BibEntry] = []

    i = 0
    while i < len(content):
        if content[i] != "@":
            i += 1
            continue

        entry_start = i
        i += 1
        while i < len(content) and content[i].isspace():
            i += 1

        type_start = i
        while i < len(content) and (content[i].isalnum() or content[i] == "_"):
            i += 1
        entry_type = content[type_start:i].strip().lower()
        if not entry_type:
            continue

        while i < len(content) and content[i].isspace():
            i += 1
        if i >= len(content) or content[i] != "{":
            continue

        brace_start = i
        brace_depth = 1
        i += 1

        key_start = i
        key_end = -1
        while i < len(content) and brace_depth > 0:
            char = content[i]
            if char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth -= 1
                if brace_depth == 0:
                    key_end = i
                    break
            elif brace_depth == 1 and char == ",":
                key_end = i
                break
            i += 1

        if key_end == -1:
            continue

        key = content[key_start:key_end].strip()
        i = brace_start
        brace_depth = 1
        i += 1
        entry_end = -1
        while i < len(content):
            char = content[i]
            if char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth -= 1
                if brace_depth == 0:
                    entry_end = i + 1
                    break
            i += 1

        if entry_end == -1:
            continue

        raw_entry = content[entry_start:entry_end]
        fields = extract_bib_fields(raw_entry)
        entries.append(BibEntry(entry_type=entry_type, key=key, raw_text=raw_entry, fields=fields))
        i = entry_end

    return entries


def extract_bib_fields(raw_entry: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    opening = raw_entry.find("{")
    if opening == -1:
        return fields

    comma_after_key = raw_entry.find(",", opening + 1)
    if comma_after_key == -1:
        return fields

    body = raw_entry[comma_after_key + 1 : raw_entry.rfind("}")]
    for segment in split_top_level_fields(body):
        if "=" not in segment:
            continue
        name, raw_value = segment.split("=", 1)
        field_name = name.strip().lower()
        value = strip_bib_value(raw_value.strip())
        if field_name:
            fields[field_name] = value
    return fields


def split_top_level_fields(body: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    brace_depth = 0
    quote_open = False

    for char in body:
        if char == '"' and brace_depth == 0:
            quote_open = not quote_open
        elif char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth = max(0, brace_depth - 1)

        if char == "," and brace_depth == 0 and not quote_open:
            segment = "".join(current).strip()
            if segment:
                parts.append(segment)
            current = []
            continue

        current.append(char)

    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def strip_bib_value(value: str) -> str:
    value = value.rstrip(",").strip()
    if len(value) >= 2 and value[0] == "{" and value[-1] == "}":
        value = value[1:-1]
    elif len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
    return re.sub(r"\s+", " ", value).strip()


def normalize_doi(value: str | None) -> str:
    return (value or "").strip().lower()


def normalize_title(value: str | None) -> str:
    text = (value or "").strip().lower()
    text = re.sub(r"[\s\-_]+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def load_scopus_metadata(path: Path) -> tuple[dict[str, ScopusMetadata], dict[str, ScopusMetadata]]:
    by_doi: dict[str, ScopusMetadata] = {}
    by_title: dict[str, ScopusMetadata] = {}

    if not path.exists():
        return by_doi, by_title

    data = json.loads(path.read_text(encoding="utf-8"))
    for record in data.get("search-results", {}).get("entry", []):
        metadata = ScopusMetadata(
            publication_date=record.get("prism:coverDate"),
            subtype_description=record.get("subtypeDescription"),
            title=record.get("dc:title"),
            doi=record.get("prism:doi"),
        )

        doi_key = normalize_doi(metadata.doi)
        title_key = normalize_title(metadata.title)
        if doi_key:
            by_doi[doi_key] = metadata
        if title_key and title_key not in by_title:
            by_title[title_key] = metadata

    return by_doi, by_title


def metadata_for_entry(
    entry: BibEntry,
    doi_index: dict[str, ScopusMetadata],
    title_index: dict[str, ScopusMetadata],
) -> ScopusMetadata | None:
    doi = normalize_doi(entry.fields.get("doi"))
    if doi and doi in doi_index:
        return doi_index[doi]
    title = normalize_title(entry.fields.get("title"))
    if title and title in title_index:
        return title_index[title]
    return None


def extract_publication_date(entry: BibEntry, metadata: ScopusMetadata | None) -> date | None:
    for raw_value in (
        entry.fields.get("publication_date"),
        entry.fields.get("date"),
        entry.fields.get("year"),
        metadata.publication_date if metadata else None,
    ):
        parsed = try_parse_date(raw_value)
        if parsed is not None:
            return parsed
    return None


def try_parse_date(raw_value: str | None) -> date | None:
    if not raw_value:
        return None

    value = raw_value.strip()
    full_match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", value)
    if full_match:
        year, month, day = map(int, full_match.groups())
        return date(year, month, day)

    year_match = re.match(r"^(\d{4})$", value)
    if year_match:
        return date(int(year_match.group(1)), 1, 1)

    return None


def build_openai_client(base_url: str, api_key: str) -> OpenAI:
    return OpenAI(base_url=base_url, api_key=api_key)


def validate_client(client: OpenAI, model: str) -> None:
    models = client.models.list()
    available = {item.id for item in models.data}
    if model not in available:
        raise RuntimeError(
            f"Model '{model}' is not exposed by the endpoint. Available models: {sorted(available)}"
        )


def title_and_venue_text(entry: BibEntry, metadata: ScopusMetadata | None) -> str:
    title = metadata.title if metadata and metadata.title else entry.fields.get("title", "")
    venue = entry.fields.get("journal") or entry.fields.get("booktitle") or entry.fields.get("publisher") or ""
    return f"{title} {venue}".strip()


def appears_front_matter(entry: BibEntry, metadata: ScopusMetadata | None) -> bool:
    title = metadata.title if metadata and metadata.title else entry.fields.get("title", "")
    if not title:
        return False
    return any(pattern.search(title) for pattern in FRONT_MATTER_PATTERNS)


def contains_any_hint(text: str, patterns: Iterable[re.Pattern[str]]) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def match_irrelevant_scope(text: str) -> str | None:
    for pattern, label in IRRELEVANT_PATTERNS:
        if pattern.search(text):
            if label == "model_fingerprinting_scope" and contains_any_hint(text, TEXT_RELEVANCE_HINTS):
                continue
            return label
    return None


def rule_prefilter(
    entry: BibEntry,
    metadata: ScopusMetadata | None,
    start_date: date,
    end_date: date,
) -> tuple[bool, dict[str, Any]]:
    title = metadata.title if metadata and metadata.title else entry.fields.get("title", "")
    venue = entry.fields.get("journal") or entry.fields.get("booktitle") or entry.fields.get("publisher") or ""
    subtype = (metadata.subtype_description or "").strip().lower() if metadata else ""
    publication_date = extract_publication_date(entry, metadata)

    if not title:
        return False, rule_decision("exclude", "missing_title", "Missing title metadata.", entry, metadata)

    if publication_date is None:
        return False, rule_decision(
            "exclude",
            "missing_year",
            "Publication date is unavailable in the BibTeX and local Scopus metadata.",
            entry,
            metadata,
        )
    if publication_date < start_date:
        return False, rule_decision(
            "exclude",
            "before_lower_bound",
            f"Publication date {publication_date.isoformat()} is before the incremental window.",
            entry,
            metadata,
        )
    if publication_date > end_date:
        return False, rule_decision(
            "exclude",
            "after_upper_bound",
            f"Publication date {publication_date.isoformat()} is after the incremental window.",
            entry,
            metadata,
        )

    if subtype in NON_PRIMARY_SUBTYPES:
        return False, rule_decision(
            "exclude",
            "non_primary_subtype",
            f"Scopus subtype '{metadata.subtype_description}' is out of scope for primary-study screening.",
            entry,
            metadata,
        )

    if appears_front_matter(entry, metadata):
        return False, rule_decision(
            "exclude",
            "front_matter",
            "Title/venue pattern indicates proceedings front matter rather than a primary study.",
            entry,
            metadata,
        )

    searchable = title
    irrelevant_scope = match_irrelevant_scope(searchable)
    if irrelevant_scope is not None:
        return False, rule_decision(
            "exclude",
            irrelevant_scope,
            "Title/venue metadata strongly indicates an out-of-scope modality or domain.",
            entry,
            metadata,
        )

    if not venue:
        return False, rule_decision(
            "exclude",
            "missing_venue",
            "Venue metadata is too incomplete to assess peer-review status.",
            entry,
            metadata,
        )

    return True, {
        "final_decision": "llm_review",
        "prefilter_result": "pass",
        "source": "rules",
        "reason": "Passed deterministic prefilter and requires LLM review.",
        "exclusion_reason": "",
    }


def rule_decision(
    final_decision: str,
    exclusion_reason: str,
    reason: str,
    entry: BibEntry,
    metadata: ScopusMetadata | None,
) -> dict[str, Any]:
    return {
        "final_decision": final_decision,
        "prefilter_result": "exclude",
        "source": "rules",
        "reason": reason,
        "exclusion_reason": exclusion_reason,
        "title": metadata.title if metadata and metadata.title else entry.fields.get("title", ""),
    }


def build_user_message(entry: BibEntry, metadata: ScopusMetadata | None, publication_date: date | None) -> str:
    title = metadata.title if metadata and metadata.title else entry.fields.get("title", "")
    authors = entry.fields.get("author", "")
    year = publication_date.year if publication_date else ""
    venue = entry.fields.get("journal") or entry.fields.get("booktitle") or entry.fields.get("publisher") or ""
    doi = entry.fields.get("doi", "")
    url = entry.fields.get("url", "")
    entry_type = metadata.subtype_description if metadata and metadata.subtype_description else entry.entry_type
    publication_date_text = publication_date.isoformat() if publication_date else ""

    return "\n".join(
        [
            f"Title: {title}",
            f"Authors: {authors}",
            f"Year: {year}",
            f"Publication date: {publication_date_text}",
            f"Entry type: {entry_type}",
            f"Venue: {venue}",
            f"DOI: {doi}",
            f"URL: {url}",
        ]
    )


def classify_with_lmstudio(
    client: OpenAI,
    entry: BibEntry,
    metadata: ScopusMetadata | None,
    model: str,
    temperature: float,
) -> tuple[ScreenDecision, str]:
    publication_date = extract_publication_date(entry, metadata)
    user_message = build_user_message(entry, metadata, publication_date)
    content = request_chat_completion(client, model, temperature, SYSTEM_PROMPT, user_message)
    try:
        payload = parse_response_payload(content)
        return screen_decision_from_payload(payload), "llm"
    except ValueError:
        repaired = request_chat_completion(
            client,
            model,
            temperature,
            "You repair malformed JSON output. Return JSON only.",
            REPAIR_PROMPT.format(broken_output=content),
        )
        try:
            payload = parse_response_payload(repaired)
            return screen_decision_from_payload(payload), "llm"
        except ValueError:
            return (
                ScreenDecision(
                    decision="maybe",
                    confidence="low",
                    primary_study=True,
                    peer_reviewed_likely=True,
                    llm_relevance="indirect",
                    text_steganography_relevance="indirect",
                    full_text_status="manual_check_required",
                    reason="Model output could not be parsed as valid JSON after one repair attempt.",
                    exclusion_reason="llm_parse_failure",
                ),
                "llm_parse_fallback",
            )


def request_chat_completion(
    client: OpenAI,
    model: str,
    temperature: float,
    system_prompt: str,
    user_message: str,
) -> str:
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    message = response.choices[0].message.content
    if not message:
        raise RuntimeError("LM Studio returned an empty completion.")
    return message.strip()


def parse_response_payload(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(content[start : end + 1])
            except json.JSONDecodeError as inner_exc:
                raise ValueError("Model output is not valid JSON.") from inner_exc
        raise ValueError("Model output is not valid JSON.") from exc


def screen_decision_from_payload(payload: dict[str, Any]) -> ScreenDecision:
    decision = str(payload.get("decision", "")).strip().lower()
    confidence = str(payload.get("confidence", "")).strip().lower()
    llm_relevance = str(payload.get("llm_relevance", "")).strip().lower()
    text_relevance = str(payload.get("text_steganography_relevance", "")).strip().lower()
    full_text_status = str(payload.get("full_text_status", "")).strip()
    reason = str(payload.get("reason", "")).strip()
    exclusion_reason = str(payload.get("exclusion_reason", "")).strip()

    if decision not in DECISIONS:
        raise ValueError("Invalid decision field.")
    if confidence not in CONFIDENCE_LEVELS:
        raise ValueError("Invalid confidence field.")
    if llm_relevance not in RELEVANCE_LEVELS:
        raise ValueError("Invalid llm_relevance field.")
    if text_relevance not in RELEVANCE_LEVELS:
        raise ValueError("Invalid text_steganography_relevance field.")
    if full_text_status != "manual_check_required":
        raise ValueError("Invalid full_text_status field.")
    if not reason:
        raise ValueError("Missing reason field.")

    return ScreenDecision(
        decision=decision,
        confidence=confidence,
        primary_study=bool(payload.get("primary_study", False)),
        peer_reviewed_likely=bool(payload.get("peer_reviewed_likely", False)),
        llm_relevance=llm_relevance,
        text_steganography_relevance=text_relevance,
        full_text_status=full_text_status,
        reason=reason,
        exclusion_reason=exclusion_reason,
    )


def write_filtered_bib(entries: list[BibEntry], included_keys: set[str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    included_entries = [entry.raw_text.rstrip() for entry in entries if entry.key in included_keys]
    if included_entries:
        output_path.write_text("\n\n".join(included_entries) + "\n", encoding="utf-8")
    else:
        output_path.write_text("", encoding="utf-8")


def write_audit_jsonl(records: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(record, ensure_ascii=False) for record in records]
    output_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def build_audit_record(
    entry: BibEntry,
    metadata: ScopusMetadata | None,
    publication_date: date | None,
    prefilter: dict[str, Any],
) -> dict[str, Any]:
    title = metadata.title if metadata and metadata.title else entry.fields.get("title", "")
    venue = entry.fields.get("journal") or entry.fields.get("booktitle") or entry.fields.get("publisher") or ""

    return {
        "key": entry.key,
        "title": title,
        "year": publication_date.year if publication_date else None,
        "publication_date": publication_date.isoformat() if publication_date else None,
        "venue": venue,
        "entry_type": entry.entry_type,
        "scopus_subtype": metadata.subtype_description if metadata else None,
        "prefilter_result": prefilter.get("prefilter_result"),
        "llm_result": None,
        "final_decision": prefilter.get("final_decision"),
        "confidence": None,
        "reason": prefilter.get("reason", ""),
        "exclusion_reason": prefilter.get("exclusion_reason", ""),
        "full_text_status": "manual_check_required",
        "source": prefilter.get("source", "rules"),
        "doi": entry.fields.get("doi", ""),
        "url": entry.fields.get("url", ""),
    }


def classify_one(
    entry: BibEntry,
    metadata: ScopusMetadata | None,
    client: OpenAI,
    model: str,
    temperature: float,
) -> tuple[str, ScreenDecision, str]:
    decision, source = classify_with_lmstudio(client, entry, metadata, model, temperature)
    return entry.key, decision, source


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_bib)
    output_bib = Path(args.output_bib)
    audit_jsonl = Path(args.audit_jsonl)
    scopus_json = Path(args.scopus_json)

    entries = parse_bibtex(input_path)
    doi_index, title_index = load_scopus_metadata(scopus_json)

    if args.dry_run:
        client = None
    else:
        try:
            client = build_openai_client(args.base_url, args.api_key)
            validate_client(client, args.model)
        except Exception as exc:  # noqa: BLE001
            print(f"Endpoint validation failed: {exc}", file=sys.stderr)
            return 1

    audit_records: list[dict[str, Any]] = []
    llm_queue: list[tuple[BibEntry, ScopusMetadata | None]] = []

    for entry in entries:
        metadata = metadata_for_entry(entry, doi_index, title_index)
        publication_date = extract_publication_date(entry, metadata)
        should_review, prefilter = rule_prefilter(entry, metadata, args.since_date, args.until_date)
        audit_record = build_audit_record(entry, metadata, publication_date, prefilter)
        audit_records.append(audit_record)
        if should_review:
            llm_queue.append((entry, metadata))

    if args.limit is not None:
        llm_queue = llm_queue[: args.limit]
        queued_keys = {entry.key for entry, _metadata in llm_queue}
        for record in audit_records:
            if record["prefilter_result"] == "pass" and record["key"] not in queued_keys:
                record["prefilter_result"] = "skipped_by_limit"
                record["final_decision"] = "exclude"
                record["reason"] = "Skipped due to --limit during test run."
                record["exclusion_reason"] = "limit_skip"
                record["source"] = "rules"

    if client is not None:
        if args.max_workers <= 1:
            llm_results = [
                classify_one(entry, metadata, client, args.model, args.temperature)
                for entry, metadata in llm_queue
            ]
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
                futures = [
                    executor.submit(
                        classify_one,
                        entry,
                        metadata,
                        client,
                        args.model,
                        args.temperature,
                    )
                    for entry, metadata in llm_queue
                ]
                llm_results = [future.result() for future in concurrent.futures.as_completed(futures)]

        llm_by_key = {key: (decision, source) for key, decision, source in llm_results}
        for record in audit_records:
            result = llm_by_key.get(record["key"])
            if result is None:
                continue
            decision, source = result
            record["llm_result"] = asdict(decision)
            record["final_decision"] = decision.decision
            record["confidence"] = decision.confidence
            record["reason"] = decision.reason
            record["exclusion_reason"] = decision.exclusion_reason
            record["full_text_status"] = decision.full_text_status
            record["source"] = source

    included_keys = {
        record["key"]
        for record in audit_records
        if record["final_decision"] == "include"
    }
    write_filtered_bib(entries, included_keys, output_bib)
    write_audit_jsonl(audit_records, audit_jsonl)
    print_summary(entries, audit_records, args.dry_run)
    return 0


def print_summary(entries: list[BibEntry], audit_records: list[dict[str, Any]], dry_run: bool) -> None:
    def count_where(predicate: Any) -> int:
        return sum(1 for record in audit_records if predicate(record))

    print(f"Total parsed: {len(entries)}")
    print(
        "Skipped before lower bound: "
        f"{count_where(lambda r: r['exclusion_reason'] == 'before_lower_bound')}"
    )
    print(
        "Skipped after upper bound: "
        f"{count_where(lambda r: r['exclusion_reason'] == 'after_upper_bound')}"
    )
    print(
        "Excluded by rule: "
        f"{count_where(lambda r: r['source'] == 'rules' and r['final_decision'] == 'exclude')}"
    )
    print(f"Sent to LLM: {count_where(lambda r: r['llm_result'] is not None)}")
    print(f"Included: {count_where(lambda r: r['final_decision'] == 'include')}")
    print(f"Excluded: {count_where(lambda r: r['final_decision'] == 'exclude')}")
    print(f"Maybe: {count_where(lambda r: r['final_decision'] == 'maybe')}")
    print(
        "Written to output bib: "
        f"{count_where(lambda r: r['final_decision'] == 'include')}"
    )
    if dry_run:
        print("Dry run: no LLM requests were sent.")


if __name__ == "__main__":
    raise SystemExit(main())
