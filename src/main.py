import httpx
technology_rules = {
    "WordPress": {
        "html": [
            "wp-content",
            "wp-includes",
            "wp-json",
            "WordPress"
        ]
    },

    "Nginx": {
        "headers": {
            "server": [
                "nginx"
            ]
        }
    }
}


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
    
def detect_technologies(html, headers, rules):
    results = {}

    for technology, rule in technology_rules.items():
        evidence =[]
        
        for pattern in rule.get("html", []):
            if pattern.lower() in html.lower():
                evidence.append("HTML contains " + pattern)
        
        for header_name, patterns, in rule.get("headers", {}). items():
            header_value = headers.get(header_name, "")

            for pattern in patterns:
                if pattern.lower() in header_value.lower():
                    evidence.append(
                        "HTTP header " + header_name + " contains " + pattern
                    )
        
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

response = fetch_website(url)

if response is not None:

    print(response.status_code)

    html = response.text

    results = detect_technologies(
        html,
        response.headers,
        technology_rules
    )

    for technology, evidence in results.items():
        print_detection(technology, evidence)