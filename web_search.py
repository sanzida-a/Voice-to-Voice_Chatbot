import os
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

def serpapi_search(query, max_results=5):
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY not found in .env")

    search = GoogleSearch({
        "q": query,
        "api_key": api_key,
        "num": max_results
    })
    results = search.get_dict()

    output = []
    if "organic_results" in results:
        for r in results["organic_results"][:max_results]:
            output.append({
                "title": r.get("title"),
                "link": r.get("link"),
                "snippet": r.get("snippet", "")
            })
    return output

def summarize_results(results):
    if not results:
        return "No results found."
    return "\n".join([f"{i+1}. {r['title']} - {r['snippet']} (Source: {r['link']})"
                      for i, r in enumerate(results)])
