import httpx
import json 
with open("data/technologies.json", "r", encoding="utf-8") as file:
    technology_rules = json.load(file)
from bs4 import BeautifulSoup

def fetch_website(url):
    try:
        response = httpx.get(url)
        response.raise_for_status()
        return response

    except httpx.HTTPStatusError as exc:
        print(
            f"Status code {exc.response.status_code} - "
            f"{exc.response.reason_phrase} "
            f"while requesting {exc.request.url!r}."
        )
        return None
    
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
        return None
    
def extract_script_sources(html):
    soup = BeautifulSoup(html, "html.parser")

    scripts = soup.find_all("script")
    script_sources = []

    for script in scripts:
        src = script.get("src")

        if src:
            script_sources.append(src)

    return script_sources

def extract_header_signals(headers):
    header_signals = []

    for name, value in headers.items():
        header_signals.append(f"{name}: {value}")
    
    return header_signals

def extract_meta_signals(html):
    soup = BeautifulSoup(html, "html.parser")

    meta_tags = soup.find_all("meta")
    meta_signals = []

    for meta in meta_tags:
        name = meta.get("name")
        content = meta.get("content")

        if name and content:
            meta_signals.append(f"{name}: {content}")
    
    return meta_signals

def extract_link_sources(html):
    soup = BeautifulSoup(html, "html.parser")

    links = soup.find_all("link")
    link_sources = []

    for link in links:
        href = link.get("href")

        if href:
            link_sources.append(href)

    return link_sources

def detect_technologies(signals, technology_rules):
    results = {}

    for technology, rules in technology_rules.items():
        evidence = []

        for signal_type, patterns in rules.items():
            signal_values = signals.get(signal_type, [])

            for pattern in patterns:
                for signal_value in signal_values:
                    if pattern.lower() in signal_value.lower():
                        evidence.append(
                            f"{signal_type} contains '{pattern}'"
                        )
                        break
        
        if evidence:
            results[technology] = evidence

    return results

def print_detection(technology, evidence):
    if evidence:
        print(technology + " detected")
        print("Evidence:")

        for item in evidence:
            print("- " + item)

url = "https://www.greenmangaming.com/blog/all-the-resident-evil-games-in-chronological-order/"
#url = "https://wordpress.org"

response = fetch_website(url)

if response is not None:
    
    print(f"Status code: {response.status_code} - {response.reason_phrase}")

    html = response.text
    script_sources = extract_script_sources(html)
    header_signals = extract_header_signals(response.headers)
    meta_signals = extract_meta_signals(html)
    link_sources = extract_link_sources(html)

    signals = {
        "html": [html],
        "headers": header_signals,
        "scripts": script_sources,
        "meta": meta_signals,
        "links": link_sources
    }

    results = detect_technologies(
        signals,
        technology_rules
    )

    for technology, evidence in results.items():
        print_detection(technology, evidence)