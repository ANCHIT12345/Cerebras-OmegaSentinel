"""Post-Mortem Generator — formats a professional incident report."""
from datetime import datetime
from typing import List


class PostMortemGenerator:
    def generate(self, scenario: str, strategy: str, temporal, economics, causal_chain, critique) -> str:
        report = f"""# INCIDENT REPORT — SENTINEL OMEGA
## Date: {datetime.now().isoformat()}
## Crisis: {scenario[:200]}

### 1. Executive Summary
{strategy[:600]}

### 2. Root Cause Analysis
**Root Cause:** {causal_chain.root_cause}

**Cascade:**
"""
        for e in causal_chain.cascade_events:
            report += f"- {e}\n"
        report += f"\n**Final Impact (if untreated):** {causal_chain.final_impact}\n"
        report += f"**Resolution breaks chain at:** {causal_chain.resolution_link}\n\n"

        report += (
            "### 3. Resolution Applied\n"
            f"{strategy}\n\n"
            "### 4. Economic Impact\n"
            f"- Cost of Downtime: ${economics.cost_of_downtime:,.0f}\n"
            f"- Cost of Fix: ${economics.cost_of_fix:,.0f}\n"
            f"- Brand Damage: ${economics.brand_damage_cost:,.0f}\n"
            f"- Revenue Recovered: ${economics.revenue_recovered:,.0f}\n"
            f"- **Net Impact: ${economics.net_impact:,.0f}**\n"
            f"- Summary: {economics.summary}\n\n"
            "### 5. Temporal Forecast\n"
        )

        for t in temporal:
            report += f"\n**{t.time_label}** [{t.status}]\n{t.narrative}\n"
            report += f"  - System: {t.system_health}\n"
            report += f"  - Sentiment: {t.brand_sentiment}\n"
            report += f"  - Financial: {t.financial_impact}\n"
            report += f"  - Regulatory: {t.regulatory_risk}\n"

        report += (
            "\n### 6. Self-Critique Assessment\n"
            f"- Technical Soundness: {critique.technical_soundness}/10\n"
            f"- Cultural Sensitivity: {critique.cultural_sensitivity}/10\n"
            f"- Economic Optimality: {critique.economic_optimality}/10\n"
            f"- Temporal Sustainability: {critique.temporal_sustainability}/10\n"
            f"- **Overall: {critique.overall_score:.1f}/10**\n"
            f"- Recommended Improvement: {critique.recommended_improvement}\n\n"
            "---\n"
            "Approved by: Sentinel-Omega v3.0\n"
            f"Confidence Score: {critique.overall_score * 10:.0f}%\n"
        )
        return report