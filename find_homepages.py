import httpx
import os
import json
from urllib.parse import urlparse

API_KEY = os.getenv("BRAVE_API_KEY")
SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
WIKIDATA_SEARCH = "https://www.wikidata.org/w/api.php"
WIKIDATA_ENTITY = "https://www.wikidata.org/w/api.php"

BLACKLIST = {"wikipedia.org", "facebook.com", "twitter.com", "linkedin.com"}

def is_official_candidate(url: str, company: str) -> bool:
    host = urlparse(url).hostname or ""
    # not blacklisted
    if any(domain in host for domain in BLACKLIST):
        return False
    # prefer if company in host
    return company.lower() in host.lower()

def get_brave_homepage(company: str, count: int = 10) -> str | None:
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": API_KEY
    }
    params = {"q": f'"{company}" official website', "count": count}
    try:
        resp = httpx.get(SEARCH_URL, headers=headers, params=params, timeout=10.0)
        resp.raise_for_status()
        results = resp.json().get("web", {}).get("results", [])
        # first pass: company in host & not blacklisted
        for r in results:
            url = r.get("url","")
            if is_official_candidate(url, company):
                return url
        # second pass: not blacklisted
        for r in results:
            url = r.get("url","")
            if urlparse(url).hostname not in BLACKLIST:
                return url
    except Exception:
        pass
    return None

def get_wikidata_homepage(company: str) -> str | None:
    # 1) find the entity
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": company
    }
    try:
        r = httpx.get(WIKIDATA_SEARCH, params=params, timeout=5.0)
        r.raise_for_status()
        search = r.json().get("search", [])
        if not search:
            return None
        qid = search[0]["id"]
        # 2) fetch P856 for that entity
        params = {
            "action": "wbgetclaims",
            "format": "json",
            "entity": qid,
            "property": "P856"
        }
        r2 = httpx.get(WIKIDATA_ENTITY, params=params, timeout=5.0)
        r2.raise_for_status()
        claims = r2.json().get("claims", {}).get("P856", [])
        if not claims:
            return None
        return claims[0]["mainsnak"]["datavalue"]["value"]
    except Exception:
        return None

if __name__ == "__main__":
    companies = ["Nestle", "Roche", "Novartis", "UBS"]
    out = {}
    for name in companies:
        url = get_brave_homepage(name)
        if not url:
            url = get_wikidata_homepage(name)
        out[name] = url or "Not found"
    print(json.dumps(out, indent=2))
