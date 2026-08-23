Green Man Gaming Blog @ https://www.greenmangaming.com/blog/all-the-resident-evil-games-in-chronological-order/

CONFIRMED / HIGH CONFIDENCE

WordPress 6.8.2
- meta generator explicitly contains WordPress 6.8.2
- /wp-content/ paths
- /wp-includes/ paths
- /wp-json/oembed/ endpoint

Nginx
- HTTP Server response header: nginx

Gravatar
- resource loaded from secure.gravatar.com

AWS infrastructure
- WordPress oEmbed URL contains an
  *.vpce.amazonaws.com endpoint in us-east-1
- indicates AWS VPC Endpoint infrastructure
- does NOT by itself prove the entire website is hosted on AWS

UNCONFIRMED / NEEDS INVESTIGATION

Google-related services
- SID / SSID / SOCS cookies observed
- need to inspect cookie domain/origin before concluding anything

Observed:
- via: varnish
- x-served-by
- x-cache
- x-cache-hits

Candidate:
- Varnish: strong
- Fastly: investigate