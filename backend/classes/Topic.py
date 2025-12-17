from dataclasses import dataclass

@dataclass
class Content:
    topic_id: str
    title: str
    summary: str
    source_spans: list[dict]
    key_terms: list[str]
    raw_text: str


