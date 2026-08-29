import httpx
import json 
with open("data/technologies.json", "r", encoding="utf-8") as file:
    technology_rules = json.load(file)
from bs4 import BeautifulSoup

def fetch_website(url):
    try:
        response = httpx.get(url)
        response.raise_for_status()
        return response, None

    except httpx.HTTPStatusError as exc:
        http_error = {
            "status_code": exc.response.status_code,
            "error": exc.response.reason_phrase
        }

        print(
            f"Status code {exc.response.status_code} - "
            f"{exc.response.reason_phrase} "
            f"while requesting {exc.request.url!r}."
        )
        return None, http_error
    
    except httpx.RequestError as exc:
        request_error = {
            "status_code": None,
            "error": str(exc)
        }

        print(f"An error occurred while requesting {exc.request.url!r}.")
        return None, request_error
    
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

        print ()

input_domains = []

with open("data/test_domains.txt", "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()

        if line :
            input_domains.append(line)

website_results = []

for domain in input_domains:
    print("=" * 60)
    print(f"Website: {domain}")
    print("=" * 60)

    response, error = fetch_website(domain)

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

        website_result = {
            "domain": domain,
            "status_code": response.status_code,
            "technologies": results
        }
        
        website_results.append(website_result)


        for technology, evidence in results.items():
            print_detection(technology, evidence)
    
    elif error is not None:

            website_result = {
                "domain": domain,
                "status_code": error.get("status_code"),
                "error": error.get("error")
            }
            
            website_results.append(website_result)

domains_processed = len(input_domains)

successful_domains= 0
failed_domains= 0
total_technologies_identified = 0
unique_technologies = set()

for website in website_results:
    if "error" in website:
        failed_domains += 1
    else:
        successful_domains += 1

    technologies = website.get("technologies", {})

    total_technologies_identified += len(technologies)

    for technology in technologies:
        unique_technologies.add(technology)

unique_technologies_identified = len(unique_technologies)

summary = {
    "domains_processed": domains_processed,
    "successful_domains": successful_domains,
    "failed_domains": failed_domains,
    "total_technologies_identified": total_technologies_identified,
    "unique_technologies_identified": unique_technologies_identified
}

final_results = {
    "summary": summary,
    "websites": website_results
}

with open("output/results.json", "w", encoding="utf-8") as file:
    json.dump(final_results, file, indent=4)

