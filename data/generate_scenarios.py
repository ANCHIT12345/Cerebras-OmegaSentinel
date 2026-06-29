#!/usr/bin/env python3
"""Generate 10,000+ crisis scenarios into SQLite for fast search.

Run once:  python data/generate_scenarios.py
Produces:  data/scenarios.db
"""
import os
import sqlite3
import random
import itertools
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "scenarios.db")

SECTORS = [
    ("e-commerce", "global checkout service", "Black Friday", "major retailers"),
    ("fintech", "payment processing platform", "quarter-close", "trading partners"),
    ("healthcare", "electronic health records system", "morning rounds", "hospital networks"),
    ("telecom", "5G core network", "rush hour", "mobile carriers"),
    ("logistics", "global shipping tracker", "holiday peak", "shipping partners"),
    ("gaming", "multiplayer matchmaker", "launch night", "game studios"),
    ("SaaS", "CRM SaaS platform", "end-of-quarter", "enterprise clients"),
    ("energy", "smart grid SCADA", "winter demand", "utility providers"),
    ("media", "video streaming CDN", "premiere night", "content studios"),
    ("aerospace", "satellite telemetry relay", "rendezvous window", "government agencies"),
]

CRISES = [
    ("cache poisoning", "a race condition in the latest deployment is poisoning the distributed cache with corrupted state"),
    ("DDoS amplification", "a UDP reflection attack is amplifying inbound traffic 40x against the edge load balancers"),
    ("DB connection exhaustion", "the connection pool is exhausted — every checkout request is timing out within 3 seconds"),
    ("thundering herd", "a cold-cache event triggered 100% of users to slam the origin database simultaneously"),
    ("certificate expiry", "the TLS certificate on the primary gateway expired at midnight — every client is disconnecting"),
    ("DNS failure", "the authoritative DNS provider is returning NXDOMAIN for 30% of customer domains"),
    ("cascading failure", "a single downstream dependency hung, draining the thread pool, toppling every frontend"),
    ("memory leak", "the new release leaks 200MB/hour per node — pods are OOM-killing every 12 minutes"),
    ("ransomware", "production DB is encrypted — a ransom note demands BTC within 2 hours or data is leaked"),
    ("data breach", "an attacker exfiltrated 4M PII records via a misconfigured S3 bucket acl"),
    ("API gateway meltdown", "the API gateway is returning 504 for 60% of routes — internal sign-off failed silently"),
    ("payment processor throttle", "Visa/Mastercard throttled the gateway API keys after error-rate spikes"),
    ("cache stampede", "expiring keys triggered 5M concurrent recomputes — Redis cluster at 100% CPU"),
    ("dependency outage", "upstream identity provider (Okta) is down — no user can auth to any service"),
    ("CDN origin shield failure", "the origin shield dropped — 80% of static asset requests now bypass cache"),
    ("DB replication lag", "replica lag spiked to 90 seconds — reads are returning stale data with corrupt orders"),
    ("message queue poisoning", "a bad producer published malformed events — the Kafka consumer is in a crash loop"),
    ("disk full", "disk fills at 2GB/min from a runaway log — pods can't write state and crash"),
    ("network partition", "split-brain between two DCs — writes are divergent, conflict resolution is manual"),
    ("SSL chain break", "intermediate CA cert expired browser-side — 100% of mobile clients fail TLS handshake"),
]

REGIONS = [
    "US-East", "US-West", "EU-West", "EU-Central", "APAC-Tokyo",
    "APAC-Singapore", "LATAM-São-Paulo", "MEA-Dubai", "Global",
]

SEVERITIES = ["SEV-1", "SEV-2", "SEV-3"]

TIMES = [
    "peak business hours", "Black Friday midnight", "Sunday night low-traffic",
    "mid-morning rush", "holiday weekend maintenance window", "quarter-close day",
    "European morning overlap with Asian close", "scheduled deploy window",
    "election-night traffic surge", "post-Cyber-Monday exhaustion",
]

CEOS = [
    "demands a real-time status update every 15 minutes",
    "wants to speak publicly in 30 minutes and needs the facts",
    "is calling the CTO directly every 10 minutes, distracting engineers",
    "has scheduled an all-hands in 60 minutes — needs the narrative",
    "wants to know if we should engage the PR firm and external counsel",
    "is asking the head of SRE to brief the board chair personally",
    "wants the SLA-customer list ranked by churn risk within the hour",
    "is debating whether to issue service credits preemptively",
]

SOCIAL = [
    "public sentiment is plummeting on X (Twitter)",
    "angry tweets are going viral with #BoycottYourBrand",
    "Reddit threads are pinning blame and gaining 5k upvotes",
    "Hacker News is dissecting our outage in real time",
    "major tech press is asking for comment within the hour",
    "TikTok creators are filming broken checkouts and going viral",
    "affected partners are tweeting screenshots of failed transactions",
    "the JP market is trending #BoycottYourBrand with 12k posts/min",
]


def build_context(sector, crisis_desc, region, severity, time_ctx, ceo, social):
    sector_name, sector_obj, peak, partners = sector
    crisis_name, crisis_text = crisis_desc
    parts = [
        f"It is {time_ctx}. The {sector_obj} ({sector_name}, {region}) is in crisis.",
        f"{crisis_text.capitalize()}.",
        f"Current impact: elevated error rates, partner escalation, and {social}.",
        f"Tier-1 {partners} are threatening to pull integrations. The CEO {ceo}.",
    ]
    return " ".join(parts)


def build_title(sector, crisis_desc, region, severity):
    sector_name, _, _, _ = sector
    crisis_name, _ = crisis_desc
    return f"{severity} [{sector_name.title()}] {crisis_name.title()} — {region}"


def build_image_keys(crisis_name):
    keys = []
    if any(k in crisis_name for k in ("cache", "DB", "memory", "queue", "disk", "replication")):
        keys.extend(["architecture", "dashboard"])
    if any(k in crisis_name for k in ("breach", "ransomware", "SSL", "certificate")):
        keys.extend(["error_log", "dashboard"])
    if any(k in crisis_name for k in ("DDoS", "thundering", "stampede")):
        keys.extend(["dashboard"])
    keys.append("twitter")
    # dedupe, cap 4
    seen = set()
    out = []
    for k in keys:
        if k not in seen:
            seen.add(k)
            out.append(k)
        if len(out) >= 4:
            break
    return out


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            context TEXT,
            sector TEXT,
            crisis_type TEXT,
            region TEXT,
            severity TEXT,
            time_context TEXT,
            image_keys TEXT
        )
    """)
    # Index for fast LIKE search on the most-searched columns
    conn.execute("CREATE INDEX idx_sector ON scenarios(sector)")
    conn.execute("CREATE INDEX idx_crisis ON scenarios(crisis_type)")
    conn.execute("CREATE INDEX idx_region ON scenarios(region)")
    conn.execute("CREATE INDEX idx_severity ON scenarios(severity)")
    conn.execute("CREATE INDEX idx_title ON scenarios(title)")
    conn.commit()

    rng = random.Random(42)  # reproducible

    rows = []
    seen_titles = set()
    pool = list(itertools.product(SECTORS, CRISES, REGIONS, SEVERITIES, TIMES))
    rng.shuffle(pool)

    target = 12000
    for sector, crisis, region, sev, time_ctx in pool:
        if len(rows) >= target:
            break
        ceo = rng.choice(CEOS)
        social = rng.choice(SOCIAL)
        title = build_title(sector, crisis, region, sev)
        # Dedupe by title (some combos may collide)
        if title in seen_titles:
            title = f"{title} #{rng.randint(1,9999)}"
        seen_titles.add(title)
        context = build_context(sector, crisis, region, sev, time_ctx, ceo, social)
        img_keys = build_image_keys(crisis[0])
        rows.append((
            title,
            context,
            sector[0],
            crisis[0],
            region,
            sev,
            time_ctx,
            ",".join(img_keys),
        ))

    conn.executemany(
        "INSERT INTO scenarios (title, context, sector, crisis_type, region, severity, time_context, image_keys) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM scenarios").fetchone()[0]
    conn.close()
    print(f"✅ Generated {count:,} scenarios → {DB_PATH}")

    # Quick sanity check: search demo
    test_conn = sqlite3.connect(DB_PATH)
    res = test_conn.execute(
        "SELECT title FROM scenarios WHERE context LIKE ? LIMIT 5",
        ("%cache poisoning%",),
    ).fetchall()
    print(f"\nSample search 'cache poisoning' returned {len(res)} matches:")
    for r in res:
        print(f"  - {r[0]}")
    print(f"\nDistribution by sector:")
    for sector, n in test_conn.execute("SELECT sector, COUNT(*) FROM scenarios GROUP BY sector ORDER BY COUNT(*) DESC"):
        print(f"  {sector:15s}: {n}")
    test_conn.close()


if __name__ == "__main__":
    main()