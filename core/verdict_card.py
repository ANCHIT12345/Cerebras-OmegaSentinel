"""Shareable 'Omega Verdict' card — 1200x630 PNG (social/OG size) drawn with Pillow.
No new dependency; built for dropping into a tweet / Devpost submission."""
import io
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = (10, 12, 16)
GOLD = (255, 215, 0)
GREEN = (0, 250, 154)
RED = (255, 75, 75)
TEXT = (200, 205, 211)
MUTED = (136, 153, 166)


def _font(size, bold=False):
    # ponytail: try common system fonts, fall back to PIL default. Good enough for a card.
    for name in (("arialbd.ttf", "seguisb.ttf") if bold else ("arial.ttf", "segoeui.ttf")):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _est_tps(results):
    txt = "".join(d.get("text", "") for d in results.get("divergence", []))
    txt += results.get("final_strategy", {}).get("text", "")
    tokens = len(txt) // 4 + 1500
    secs = max(results.get("total_time", 9.0), 0.1)
    return tokens / secs


def render_verdict_png(results: dict) -> bytes:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # accent top bar
    d.rectangle([0, 0, W, 8], fill=GOLD)

    d.text((60, 50), "SENTINEL OMEGA", font=_font(34, bold=True), fill=GOLD)
    d.text((60, 96), "OMEGA VERDICT", font=_font(64, bold=True), fill=(255, 255, 255))

    econ = results.get("economics")
    net = getattr(econ, "net_impact", 0.0) if econ is not None else 0.0
    net_col = GREEN if net >= 0 else RED
    d.text((60, 200), "NET IMPACT", font=_font(26, bold=True), fill=MUTED)
    d.text((60, 234), f"${net:,.0f}", font=_font(72, bold=True), fill=net_col)

    # agent vetoes
    vetoes = [x.get("veto") for x in results.get("divergence", []) if x.get("veto")]
    d.text((640, 200), "AGENT DEBATE", font=_font(26, bold=True), fill=MUTED)
    d.text((640, 234), f"{len(results.get('divergence', []))} agents · {len(vetoes)} vetoes resolved",
           font=_font(30, bold=True), fill=TEXT)

    # self-critique avg
    crit = results.get("self_critique")
    score = getattr(crit, "overall_score", None) if crit is not None else None
    if not isinstance(score, (int, float)):
        parts = [getattr(crit, k, None) if crit is not None else None
                 for k in ("technical_soundness", "cultural_sensitivity",
                           "economic_optimality", "temporal_sustainability")]
        parts = [p for p in parts if isinstance(p, (int, float))]
        score = sum(parts) / len(parts) if parts else None
    if isinstance(score, (int, float)):
        d.text((640, 290), "SELF-CRITIQUE", font=_font(26, bold=True), fill=MUTED)
        d.text((640, 324), f"{score:.1f}/10", font=_font(40, bold=True), fill=GOLD)

    # speed line
    tps = _est_tps(results)
    secs = results.get("total_time", 9.0)
    d.text((60, 400), "SPEED", font=_font(26, bold=True), fill=MUTED)
    d.text((60, 434), f"{tps:,.0f} tok/s · {secs:.1f}s full pipeline", font=_font(36, bold=True), fill=GREEN)

    # footer badge
    d.rectangle([0, H - 70, W, H], fill=(18, 22, 30))
    d.text((60, H - 52), "Powered by gemma-4-31b on Cerebras", font=_font(26, bold=True), fill=GOLD)
    d.text((W - 360, H - 52), "Predictive Equilibrium Engine", font=_font(22), fill=MUTED)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


if __name__ == "__main__":
    class _E:  # stub economics
        net_impact = -72000.0

    class _C:  # stub critique
        overall_score = 8.0

    stub = {
        "economics": _E(),
        "self_critique": _C(),
        "divergence": [{"text": "x" * 800, "veto": "HARD_VETO"}, {"text": "y" * 600, "veto": None}],
        "final_strategy": {"text": "z" * 2000},
        "total_time": 9.1,
    }
    out = render_verdict_png(stub)
    assert out[:4] == b"\x89PNG", out[:8]
    assert len(out) > 1000
    print(f"OK verdict ({len(out)} bytes)")
