import httpx
from app.core.logger import logger

SS_BASE_URL = "https://api.semanticscholar.org/graph/v1"

PAPER_FIELDS = ",".join(
    [
        "paperId",
        "externalIds",
        "title",
        "abstract",
        "year",
        "authors",
        "citationCount",
        "influentialCitationCount",
        "referenceCount",
        "fieldsOfStudy",
        "url",
    ]
)


class SemanticScholarService:
    def fetch_paper_by_arxiv_id(self, arxiv_id: str):
        """
        Fetches paper details from Semantic Scholar using the provided arXiv ID."""

        with httpx.Client() as client:
            response = client.get(
                f"{SS_BASE_URL}/paper/arXiv:{arxiv_id}",
                params={"fields": PAPER_FIELDS},
                timeout=30.0,
            )

        if response.status_code == 400:
            logger.warning(
                f"Paper with arXiv ID {arxiv_id} not found on semantic scholar:: {response.text}"
            )
            return None
        response.raise_for_status()
        return response.json()

    def parse_paper(self, data: dict) -> dict:
        """Parse SS response into fields matching the Paper model."""
        return {
            "semantic_scholar_id": data.get("paperId"),
            "title": data.get("title"),
            "abstract": data.get("abstract"),
            "authors": [a["name"] for a in data.get("authors", [])],
            "citation_count": data.get("citationCount", 0),
            "influential_citation_count": data.get("influentialCitationCount", 0),
            "references_count": data.get("referenceCount", 0),
            "fields_of_study": data.get("fieldsOfStudy") or [],
            "source_url": data.get("url"),
            "doi": data.get("externalIds", {}).get("DOI"),
            "arxiv_id_from_ss": data.get("externalIds", {}).get("ArXiv"),
            "enriched_by": "semantic_scholar",
        }


semantic_service = SemanticScholarService()
