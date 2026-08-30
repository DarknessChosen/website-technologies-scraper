# Website Technologies Scraper

A Python-based website technology detection tool built for the Veridion Software Engineering Intern coding challenge.

The scraper receives a list of website domains, fetches each website, extracts several observable signals from the response, and matches them against a rule-based technology knowledge base.

Besides detecting known technologies, the project also includes a candidate discovery mechanism for finding recurring unknown signals that may indicate technologies not yet present in the knowledge base.

---

## Features

- Reads domains from a Parquet input file
- Processes multiple websites in a single run
- Automatically normalizes domains to valid URLs
- Follows HTTP redirects
- Handles HTTP, DNS, TLS, connection and timeout errors without stopping the complete run
- Extracts signals from:
  - raw HTML
  - HTTP headers
  - script sources
  - meta tags
  - link elements
- Detects technologies by matching extracted website signals against configurable fingerprints
- Stores evidence for every detected technology
- Generates a JSON result file containing:
  - per-domain results
  - HTTP status codes
  - detected technologies
  - detection evidence
  - failed requests
  - execution summary
- Collects unknown external hostnames and ranks recurring signals for future technology discovery
- Ranks candidate signals based on their occurrence across different domains

---

## Project Structure

```text
website-technologies-scraper/
│
├── data/
│   ├── domains.parquet
│   └── technologies.json
│
├── output/
│   ├── results.json
│   └── candidate_signals.json
│
├── src/
│   └── main.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

---

## Running the Scraper

Place the input Parquet file inside the `data` directory as:

```text
data/domains.parquet
```

The file is expected to contain a column named:

```text
root_domain
```

Run the scraper from the project root:

```bash
python src/main.py
```

After the execution finishes, two output files are generated:

```text
output/results.json
output/candidate_signals.json
```

---

## Detection Process

The detection process is divided into two main stages.

### 1. Signal Extraction

For every successfully fetched website, the scraper extracts observable information from multiple sources.

Example:

```python
signals = {
    "html": [...],
    "headers": [...],
    "scripts": [...],
    "meta": [...],
    "links": [...]
}
```

Examples of extracted signals include:

```text
server: nginx
wp-content
cdn.jsdelivr.net
generator: WordPress
fonts.googleapis.com
```

### 2. Technology Matching

Technology fingerprints are stored separately in:

```text
data/technologies.json
```

Example:

```json
{
    "WordPress": {
        "html": [
            "wp-content",
            "wp-includes",
            "wp-json",
            "WordPress"
        ],

        "meta": [
            "generator: WordPress"
        ],

        "links": [
            "gmpg.org/xfn/11"
        ]
    }
}
```

The detection engine compares the extracted signals against the known fingerprints.

If a fingerprint matches, the technology is added to the website result together with the evidence responsible for the detection.

Example:

```json
{
    "WordPress": [
        "html contains 'wp-content'"
    ]
}
```

Keeping the detection rules outside the Python implementation makes the knowledge base easier to extend without modifying the detection engine itself.

---

## Technology Discovery

A fixed fingerprint database cannot contain every technology used on the web.

For this reason, the scraper also contains a candidate discovery mechanism.

External hostnames found in scripts and links that do not already match a known fingerprint are collected and aggregated across the entire dataset.

Example candidate:

```json
{
    "signal_type": "scripts",
    "candidate": "example-cdn.com",
    "occurrences": 15,
    "domains_count": 8,
    "sample_domains": [
        "https://example1.com",
        "https://example2.com"
    ]
}
```

Two metrics are collected:

- `occurrences` - total number of times the signal appeared
- `domains_count` - number of distinct websites containing the signal

`domains_count` is particularly useful because a signal appearing many times on a single website is less interesting than a signal independently appearing across many websites.

The candidates can then be manually investigated and classified as:

- a fingerprint for an already supported technology
- a fingerprint for a new technology
- a generic service or CDN
- normal website behaviour
- noise

Validated fingerprints can then be added to `technologies.json`.

This process was used during development to expand the original technology knowledge base based on patterns discovered directly in the provided dataset.

---

## Why Candidate Technologies Are Not Added Automatically

A recurring hostname does not necessarily identify a technology.

For example, a generic domain may host multiple unrelated products or services.

Automatically promoting every recurring candidate would therefore introduce false positives.

The current implementation intentionally prefers conservative detection:

> An ambiguous signal remains a candidate until there is enough evidence to classify it reliably.

This prioritizes detection precision over speculative coverage.

---

## Error Handling

Web crawling involves many failure conditions outside the control of the scraper.

The provided dataset contained websites with problems such as:

- unreachable domains
- DNS failures
- connection failures
- invalid TLS certificates
- HTTP errors
- slow or unresponsive servers
- redirects
- expired or parked domains

Errors are handled per domain, allowing the rest of the dataset to continue processing.

A failed website is recorded in the output instead of terminating the complete run.

Example:

```json
{
    "domain": "https://example.com",
    "status_code": null,
    "error": "connection error"
}
```

---

## Benchmark Run

The final test was performed on the complete dataset of 200 domains.

```text
Domains processed:                200
Successful requests:              137
Failed requests:                   63
Technology detections:            457
Unique technologies detected:      33
Runtime:                     ~4.5 min
```

The scraper processes the websites sequentially in the current implementation.

The runtime therefore depends heavily on external factors such as DNS resolution, network latency, remote server response times and request timeouts rather than only local CPU performance.

---

## Current Limitations

### Static HTTP analysis

The scraper analyzes the HTTP response and returned HTML.

Technologies loaded dynamically after JavaScript execution may therefore not be visible.

A headless browser could improve detection for such websites, but it would considerably increase processing cost.

### Rule-based fingerprint matching

The current detector uses substring-based fingerprints.

This approach is simple, explainable and easy to extend, but more advanced patterns may require:

- regular expressions
- version extraction
- multiple-signal rules
- conditional fingerprints

### No confidence score

All current matches are treated equally.

In practice, some signals are much stronger evidence than others.

For example:

```text
meta generator = WordPress
```

is significantly stronger than a generic external hostname.

A future implementation could classify evidence as weak, medium or strong and calculate a confidence score.

### Candidate URL information is simplified

The discovery system currently aggregates external hostnames.

This loses useful URL path information.

For example:

```text
www.google.com
```

is ambiguous, while:

```text
www.google.com/recaptcha/api.js
```

provides much stronger information.

Keeping the full URL or selected path components would improve future candidate classification.

### Link signals can contain noise

`<link>` elements may reference:

- stylesheets
- fonts
- CDNs
- icons
- canonical URLs
- alternate language versions
- unrelated external resources

Future versions could also analyze attributes such as `rel` to distinguish useful technology fingerprints from normal navigation metadata.

### Domain comparison

Candidate discovery currently compares complete hostnames. As a result, different subdomains belonging to the same website or organization may sometimes be treated as external candidates.

A future implementation could compare registrable domains instead, using the Public Suffix List to correctly handle domains such as example.co.uk.

### Parked and expired websites

A website can return HTTP `200 OK` while actually being an expired-domain or parking page.

HTTP success alone therefore does not guarantee that the original website is still active.

A future version could classify page states such as:

```text
active
parked
expired
unreachable
```

---

## Scaling to Millions of Domains

The current implementation is optimized for clarity and the provided benchmark rather than large-scale crawling.

Processing millions of domains within one or two months would require several architectural changes.

### Concurrent requests

The current scraper processes websites sequentially.

Using asynchronous HTTP requests or a bounded worker pool would allow many websites to be fetched simultaneously.

Concurrency should remain controlled to prevent excessive resource usage and avoid overwhelming remote servers.

### Connection pooling

A persistent HTTP client could manage connections more efficiently and reuse existing connections when multiple requests target the same origin. This would become more beneficial if the scraper later performs retries or fetches multiple resources from the same website.

### Distributed workers

The domain dataset could be partitioned and processed across multiple workers or machines.

A possible architecture would be:

```text
Input dataset
      |
      v
Task queue
      |
      +------ Worker 1
      +------ Worker 2
      +------ Worker 3
      +------ ...
      |
      v
Result storage
```

### Retry strategy

Temporary failures should be retried using limited retries and exponential backoff.

Permanent failures should be recorded without repeatedly wasting resources.

### Incremental persistence

Results should be written progressively rather than only after the complete crawl finishes.

This would allow interrupted workers to resume from checkpoints instead of restarting the entire dataset.

### Tiered detection

Most websites could first be analyzed using inexpensive HTTP requests.

Only websites requiring JavaScript execution could then be sent to a more expensive headless-browser processing stage.

```text
HTTP detector
     |
     +---- enough evidence ---> result
     |
     +---- insufficient ------> browser worker
```

### Efficient rule matching

As the fingerprint database grows to hundreds or thousands of technologies, repeatedly comparing every signal against every fingerprint becomes increasingly expensive.

Possible improvements include:

- pre-indexing fingerprints by signal type
- compiled regular expressions
- normalized fingerprints
- multi-pattern matching algorithms
- caching repeated assets and domains

### Data storage

For millions of domains, structured formats such as Parquet would be more efficient than one large JSON document.

Results could also be partitioned and processed incrementally.

---

## Future Improvements

Possible improvements include:

- asynchronous crawling
- connection pooling
- configurable concurrency
- request retries and exponential backoff
- HTTP fallback where appropriate
- JavaScript rendering using a headless browser
- confidence scoring
- strong and weak fingerprint classification
- version detection
- regular-expression fingerprints
- multi-signal detection rules
- URL path-aware candidate discovery
- candidate hostname normalization
- Public Suffix List domain comparison
- parked-domain detection
- filtering link elements using their `rel` attribute
- incremental result storage
- automated candidate ranking
- larger and continuously updated technology knowledge base

---

## Design Philosophy

The goal of this implementation was not to guess as many technologies as possible.

Instead, the scraper aims to provide detections that can be explained through observable evidence.

The same principle applies to technology discovery: recurring unknown signals are surfaced for investigation rather than automatically being classified.

This keeps the system extensible while reducing the risk of false-positive detections.