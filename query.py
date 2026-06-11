import argparse
import sys
import requests

ENDPOINT = "http://localhost:3030/publications/sparql"

PREFIXES = """
PREFIX : <http://aispire.example.org/publications/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""

INTENTS = {
    "list authors at NeurIPS": """
SELECT DISTINCT ?author
WHERE {
    ?paper :authoredBy ?author ;
           :publishedIn :NeurIPS .
}
LIMIT 10
""",
    "papers per topic": """
SELECT ?topic (COUNT(?paper) AS ?n)
WHERE {
    ?paper :topic ?topic .
}
GROUP BY ?topic
LIMIT 10
""",
    "coauthor pairs": """
SELECT DISTINCT ?a ?b
WHERE {
    ?paper :authoredBy ?a ;
           :authoredBy ?b .
    FILTER(str(?a) < str(?b))
}
LIMIT 10
""",
    "has prolific author": """
ASK {
    {
        SELECT ?author
        WHERE {
            ?p :authoredBy ?author .
        }
        GROUP BY ?author
        HAVING (COUNT(?p) > 10)
    }
}
""",
    "2023 papers with authors": """
CONSTRUCT {
    ?paper :authoredBy ?author .
}
WHERE {
    ?paper a :Paper ;
           :authoredBy ?author ;
           :year 2023 .
}
""",
    "top 5 cited": """
SELECT ?paper ?cc
WHERE {
    ?paper :citationCount ?cc .
}
ORDER BY DESC(?cc)
LIMIT 5
""",
    "hinton": """
SELECT ?author
WHERE {
    ?author ?label "Hinton" .
    FILTER(?label = skos:prefLabel || ?label = skos:altLabel)
}
""",
}


def build_query(intent: str) -> str:
    if intent not in INTENTS:
        supported = "\n".join(f"- {name}" for name in INTENTS)
        raise ValueError(f"Unknown intent: {intent}\nSupported intents:\n{supported}")
    return PREFIXES + INTENTS[intent]


def run_query(query: str) -> str:
    response = requests.get(
        ENDPOINT,
        params={"query": query},
        headers={"Accept": "text/csv"},
        timeout=10,
    )
    response.raise_for_status()
    return response.text


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dispatch fixed natural-language intents to SPARQL queries."
    )
    parser.add_argument("intent", help="Intent phrase, for example: 'top 5 cited'")
    args = parser.parse_args()

    try:
        query = build_query(args.intent)
        result = run_query(query)
        print(result)
        return 0
    except ValueError as e:
        print(e, file=sys.stderr)
        parser.print_usage(sys.stderr)
        return 2
    except requests.RequestException as e:
        print(f"Error contacting Fuseki: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())