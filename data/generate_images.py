#!/usr/bin/env python3
"""Generate 4 realistic test images for Sentinel Omega multimodal demo.

Produces:
  data/sample_images/architecture_diagram.png  — microservices topology with visible SPoF
  data/sample_images/dashboard_screenshot.png — Grafana-style metric dashboard with spikes
  data/sample_images/twitter_screenshot.png    — angry tweets about Black Friday outage
  data/sample_images/error_log_image.png       — stack trace with visible PII (compliance bait)

Run:  python data/generate_images.py
"""
import os
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sample_images")
os.makedirs(OUT, exist_ok=True)


# ──────────────────────────────────────────────────────────
# 1. ARCHITECTURE DIAGRAM
# ──────────────────────────────────────────────────────────
def gen_architecture():
    fig, ax = plt.subplots(1, 1, figsize=(14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.set_facecolor("#0E1117")
    fig.patch.set_facecolor("#0E1117")
    ax.axis("off")

    # Title
    ax.text(7, 9.5, "Microservices Architecture — Payment Gateway",
            fontsize=16, color="#FFD700", ha="center", weight="bold")
    ax.text(7, 9.1, "v2.4.1 — deployed 12:00 AM Black Friday",
            fontsize=9, color="#FF4B4B", ha="center", style="italic")

    def box(x, y, w, h, label, color, bg):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                              edgecolor=color, facecolor=bg, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, label, ha="center", va="center",
                fontsize=9, color=color, weight="bold")

    def arrow(x1, y1, x2, y2, color="#555"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                     arrowstyle="->", mutation_scale=15, color=color, linewidth=1.8))

    # Edge / CDN
    box(0.5, 7.5, 2.5, 1.2, "CDN / Edge\n(Cloudflare)", "#00D4FF", "#162028")
    # Load Balancer
    box(4, 7.5, 2.5, 1.2, "Load Balancer\n(NGINX)", "#00D4FF", "#162028")
    # API Gateway
    box(7.5, 7.5, 2.5, 1.2, "API Gateway\n(Kong)", "#00D4FF", "#162028")
    arrow(3, 8.1, 4, 8.1)
    arrow(6.5, 8.1, 7.5, 8.1)

    # Checkout Service (the new deploy)
    box(11, 7.5, 2.5, 1.2, "Checkout Service\nv2.4.1 ← BAD", "#FF4B4B", "#2A1010")
    arrow(10, 8.1, 11, 8.1)

    # Cache layer — Redis
    box(1, 5, 2.5, 1.2, "Redis Cache\n(Clone-A)", "#00FA9A", "#0A2010")
    # Cache second node
    box(4, 5, 2.5, 1.2, "Redis Cache\n(Clone-B)", "#00FA9A", "#0A2010")
    arrow(12.25, 7.5, 2.25, 6.2, color="#FF4B4B")  # checkout → cache A
    arrow(12.25, 7.5, 5.25, 6.2, color="#FF4B4B")

    # Payment Gateway (the poison source)
    box(8, 5, 2.5, 1.2, "Payment Gateway\n← RACE CONDITION", "#FF4B4B", "#2A1010")
    arrow(12.25, 7.5, 9.25, 6.2, color="#FF4B4B")

    # DB Layer — single node (SPoF!)
    box(5, 2.5, 2.5, 1.3, "PostgreSQL Primary\n(NO REPLICA!)\n← SINGLE POINT\n   OF FAILURE", "#FF4B4B", "#2A1010")
    arrow(2.25, 5, 6, 3.8, color="#555")
    arrow(5.25, 5, 6.5, 3.8, color="#555")
    arrow(9.25, 5, 7, 3.8, color="#FF4B4B")

    # Queue
    box(0.5, 2.5, 2.5, 1.2, "Kafka Queue\n(events)", "#9B59B6", "#180A20")
    arrow(2.25, 5, 1.75, 3.7, color="#555")

    # Monitoring
    box(10.5, 2.5, 2.5, 1.2, "Monitoring\n(Prometheus)", "#FFA500", "#201810")
    arrow(12.25, 5, 11.75, 3.7, color="#555")

    # Warning annotation
    ax.text(7, 1.5, "⚠  No DB replica — all writes go to a single PostgreSQL node.\n"
                    "⚠  Cache has no fallback — cold-cache triggers thundering herd.\n"
                    "⚠  Payment Gateway has no circuit breaker — cascading failure unblocked.",
            fontsize=8, color="#FF4B4B", ha="center",
            bbox=dict(boxstyle="round", facecolor="#1A0A0A", edgecolor="#FF4B4B"))

    path = os.path.join(OUT, "architecture_diagram.png")
    fig.savefig(path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  ✅ {path}")


# ──────────────────────────────────────────────────────────
# 2. DASHBOARD SCREENSHOT (Grafana-style)
# ──────────────────────────────────────────────────────────
def gen_dashboard():
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    fig.patch.set_facecolor("#0E1117")
    fig.suptitle("Production Dashboard — Black Friday 12:01 AM",
                 fontsize=14, color="#FFD700", weight="bold", y=0.98)

    np.random.seed(42)
    x = np.arange(0, 60)  # 60 minutes

    # Error Rate
    ax = axes[0, 0]
    err = np.concatenate([np.random.poisson(0.5, 30), np.random.poisson(25, 30)])
    err = np.clip(err, 0, 60)
    ax.plot(x, err, color="#FF4B4B", linewidth=2)
    ax.fill_between(x, 0, err, alpha=0.3, color="#FF4B4B")
    ax.axhline(y=1, color="#00FA9A", linestyle="--", alpha=0.5, label="SLO < 1%")
    ax.set_title("Error Rate (%)", color="#FF4B4B", fontsize=11)
    ax.set_facecolor("#0E1117")
    ax.tick_params(colors="#888")
    ax.legend(fontsize=7, loc="upper left", facecolor="#161B22", labelcolor="#E0E0E0")

    # Latency P99
    ax = axes[0, 1]
    lat = np.concatenate([np.random.normal(120, 20, 30), np.random.normal(2400, 300, 30)])
    ax.plot(x, lat, color="#FFA500", linewidth=2)
    ax.axhline(y=200, color="#00FA9A", linestyle="--", alpha=0.5, label="SLO 200ms")
    ax.set_title("P99 Latency (ms)", color="#FFA500", fontsize=11)
    ax.set_facecolor("#0E1117")
    ax.tick_params(colors="#888")
    ax.legend(fontsize=7, loc="upper left", facecolor="#161B22", labelcolor="#E0E0E0")

    # DB Connections
    ax = axes[1, 0]
    conn = np.concatenate([np.random.normal(120, 20, 30), np.random.normal(980, 30, 30)])
    conn = np.clip(conn, 0, 1000)
    ax.plot(x, conn, color="#00D4FF", linewidth=2)
    ax.axhline(y=1000, color="#FF4B4B", linestyle="--", alpha=0.5, label="Max Pool")
    ax.set_title("DB Connection Pool", color="#00D4FF", fontsize=11)
    ax.set_facecolor("#0E1117")
    ax.tick_params(colors="#888")
    ax.legend(fontsize=7, loc="upper left", facecolor="#161B22", labelcolor="#E0E0E0")

    # Cache Hit Rate
    ax = axes[1, 1]
    hit = np.concatenate([np.random.normal(95, 3, 30), np.random.normal(12, 5, 30)])
    hit = np.clip(hit, 0, 100)
    ax.plot(x, hit, color="#00FA9A", linewidth=2)
    ax.axhline(y=85, color="#FFA500", linestyle="--", alpha=0.5, label="Threshold 85%")
    ax.set_title("Cache Hit Rate (%)", color="#00FA9A", fontsize=11)
    ax.set_facecolor("#0E1117")
    ax.tick_params(colors="#888")
    ax.legend(fontsize=7, loc="upper right", facecolor="#161B22", labelcolor="#E0E0E0")

    # Annotate the spike
    axes[0, 0].annotate("← deploy at T+30", xy=(30, 25), xytext=(35, 50),
                        fontsize=8, color="#FF4B4B",
                        arrowprops=dict(arrowstyle="->", color="#FF4B4B"))

    # X labels
    for ax in axes.flat:
        ax.set_xlabel("Time (min)", fontsize=8, color="#888")
        for spine in ax.spines.values():
            spine.set_color("#333")

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    path = os.path.join(OUT, "dashboard_screenshot.png")
    fig.savefig(path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  ✅ {path}")


# ──────────────────────────────────────────────────────────
# 3. TWITTER SCREENSHOT
# ──────────────────────────────────────────────────────────
def gen_twitter():
    from PIL import Image, ImageDraw, ImageFont

    W, H = 800, 700
    bg = "#15202B"  # Twitter dark
    card_bg = "#192734"
    text_color = "#E1E8ED"
    sub_color = "#8899A6"
    red = "#FF4B4B"
    blue = "#1DA1F2"

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    try:
        font_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_u = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except OSError:
        font_h = ImageFont.load_default()
        font_u = font_h
        font_b = font_h
        font_s = font_h

    # Header
    draw.rectangle([0, 0, W, 50], fill="#1C2D3F")
    draw.text((20, 12), "X", fill=blue, font=font_h)
    draw.text((50, 14), "Posts", fill=text_color, font=font_u)

    tweets = [
        ("@justin_bf_shopper", "Justin", "Black Friday shopper with 200k followers", red,
         "I've been waiting ALL YEAR for this. Trying to buy a TV and your checkout is BROKEN for 40 minutes straight. You had ONE job. #BoycottBrandsCheckout", "11:58 PM", 14200),
        ("@tech_crunch_reader", "Emma", "Tech journalist", "#FFA500",
         "Sources tell me this is a race condition in their payment gateway deployment. Cache is poisoned. This is a SEV-1. #BlackFridayOutage", "12:01 AM", 8700),
        ("@sarah_tokyo", "Sarah", "Tokyo-based e-commerce consultant", "#FF4B4B",
         "日本の顧客が結合を引き上げる準備をしています。これは信用の危機です。\n(JP customers preparing to pull integrations. This is a trust crisis.) #BoycottYourBrand", "12:03 AM", 5400),
        ("@bigretailer_api", "BigRetailer Inc.", "Official partner account", red,
         "We are formally notifying BrandCheckout that we will terminate our integration within 30 minutes if SLA is not restored. This is unacceptable.", "12:05 AM", 12300),
    ]

    y = 60
    for handle, name, bio, badge, body, time, likes in tweets:
        # Card background
        draw.rectangle([15, y, W - 15, y + 140], fill=card_bg)

        # Avatar (colored circle)
        cx, cy = 50, y + 35
        draw.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=badge)

        # Name + handle
        draw.text((80, y + 18), f"{name}", fill=text_color, font=font_u)
        draw.text((80 + font_u.getlength(f"{name}") + 8, y + 18), handle, fill=sub_color, font=font_b)
        draw.text((W - 80, y + 18), time, fill=sub_color, font=font_s)

        # Bio
        draw.text((80, y + 40), bio, fill=sub_color, font=font_s)

        # Tweet body (wrapped)
        wrapped = textwrap.fill(body, width=70)
        draw.text((80, y + 60), wrapped, fill=text_color, font=font_b)

        # Stats
        stats_y = y + 118
        draw.text((80, stats_y), f"💬 3.2K   🔁 8.1K   ❤️ {likes:,}", fill=sub_color, font=font_s)

        y += 155

    # Bottom bar
    draw.text((300, H - 25), "Trending: #BoycottBrandsCheckout  #BoycottYourBrand  #BlackFridayOutage",
              fill=red, font=font_s)

    path = os.path.join(OUT, "twitter_screenshot.png")
    img.save(path)
    print(f"  ✅ {path}")


# ──────────────────────────────────────────────────────────
# 4. ERROR LOG IMAGE (with PII — compliance bait)
# ──────────────────────────────────────────────────────────
def gen_error_log():
    from PIL import Image, ImageDraw, ImageFont

    W, H = 900, 750
    bg = "#1E1E1E"
    header_bg = "#2D2D2D"
    text_color = "#D4D4D4"
    red = "#F44747"
    yellow = "#DCDCAA"
    green = "#6A9955"
    cyan = "#4EC9B0"

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    try:
        font_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 14)
        font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 12)
        font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 11)
    except OSError:
        font_h = ImageFont.load_default()
        font_b = font_h
        font_s = font_h

    # Terminal header
    draw.rectangle([0, 0, W, 30], fill=header_bg)
    draw.ellipse([10, 8, 22, 20], fill="#FF5F56")
    draw.ellipse([28, 8, 40, 20], fill="#FFBD2E")
    draw.ellipse([46, 8, 58, 20], fill="#27C93F")
    draw.text((70, 7), "production-server-01 — kubectl logs -f checkout-service", fill=text_color, font=font_b)

    lines = [
        ("12:01:14.287", "INFO", green, "checkout-service started, version=2.4.1, commit=abc123f"),
        ("12:01:15.001", "INFO", green, "Connected to Redis cluster cache-01:6379, cache-02:6379"),
        ("12:01:15.342", "INFO", green, "Connected to PostgreSQL primary db-primary:5432"),
        ("12:01:16.100", "WARN", yellow, "Cache hit rate dropped to 85.2% (threshold: 90%)"),
        ("12:01:18.423", "WARN", yellow, "Detected concurrent write to session_key=pay_sess_8e2f... race condition suspected"),
        ("12:01:22.771", "ERROR", red, "NullPointerException in PaymentGatewayHandler.handleCheckout()"),
        ("12:01:22.772", "ERROR", red, "  at com.brand.checkout.PaymentGateway.validateCache(PaymentGateway.java:147)"),
        ("12:01:22.773", "ERROR", red, "  at com.brand.checkout.CheckoutService.process(CheckoutService.java:89)"),
        ("12:01:22.774", "ERROR", red, "  at com.brand.api.GatewayHandler.dispatch(GatewayHandler.java:234)"),
        ("12:01:23.101", "ERROR", red, "Failed checkout for user: john.doe@email.com (order_id=ORD-9182736)"),
        ("12:01:23.102", "ERROR", red, "Payment session corrupted: pay_sess_8e2f1a3b — card_token=4242vis...4242"),
        ("12:01:23.103", "ERROR", red, "  raw_billing_address: 1-2-3 Shibuya, Tokyo, JP 150-0002 — phone: +81-90-1234-5678"),
        ("12:01:24.001", "ERROR", red, "Connection pool exhausted (980/1000) — checkout requests timing out"),
        ("12:01:25.341", "ERROR", red, "Cache miss for key pay_sess_8e2f1a3b — falling back to DB"),
        ("12:01:25.342", "ERROR", red, "DB query timeout (5000ms) — pool has 0 available connections"),
        ("12:01:26.100", "FATAL", red, "Circuit breaker OPEN — all payment routes returning 503"),
        ("12:01:27.000", "ERROR", red, "Kafka consumer lag: 45,000 messages — downstream services affected"),
        ("12:01:28.500", "WARN", yellow, "Prometheus alert fired: BlackFridayCheckoutDown (severity=critical)"),
        ("12:01:30.000", "ERROR", red, "403 checkout requests failed in last 60s (error rate: 40.3%)"),
        ("12:01:31.200", "FATAL", red, "JP region API returning 503 for 100% of requests — pull integration risk HIGH"),
        ("12:01:33.000", "INFO", green, "PagerDuty incident #INC-2026-4521 created — oncall: @devops_lead"),
        ("12:01:34.500", "WARN", yellow, "SOC2 audit log export started (contains PII — requires encryption at rest)"),
    ]

    y = 40
    for ts, level, color, msg in lines:
        draw.text((10, y), ts, fill=cyan, font=font_s)
        draw.text((110, y), f"[{level:5}]", fill=color, font=font_s)
        draw.text((175, y), msg, fill=text_color, font=font_s)
        y += 17

    # Red box around PII lines
    y_pii_start = 40 + 10 * 17  # line index 10 (0-based)
    draw.rectangle([173, y_pii_start - 2, W - 10, y_pii_start + 3 * 17 + 2],
                   outline=red, width=1)
    draw.text((W - 200, y_pii_start + 3 * 17 + 10),
              "← PII VISIBLE (GDPR Art. 5/25/32, SOC2 CC6.1)",
              fill=red, font=font_s)

    # Status bar
    draw.rectangle([0, H - 25, W, H], fill="#007ACC")
    draw.text((10, H - 22), "Log stream: checkout-service  |  Lines: 22  |  ERROR: 14  |  ⚠ PII DETECTED: 3",
              fill="#FFFFFF", font=font_s)

    path = os.path.join(OUT, "error_log_image.png")
    img.save(path)
    print(f"  ✅ {path}")


# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating test images for Sentinel Omega multimodal demo...")
    gen_architecture()
    gen_dashboard()
    gen_twitter()
    gen_error_log()
    print("\n✅ All 4 images saved to data/sample_images/")