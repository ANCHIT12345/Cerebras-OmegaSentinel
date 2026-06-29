"""The Omega Orchestrator — the heart of Sentinel Omega."""
import asyncio
import time
import logging
from typing import Dict, Any, List, Optional

from core.api import call_gemma, call_gemma_stream
from core.config import settings
from core.telemetry import TelemetryVector, calculate_agent_weights
from core.monte_carlo import MonteCarloEngine
from core.simulator import TemporalSimulator
from core.economics import EconomicCalculator
from core.causal_chain import CausalChainGenerator
from core.critic import SelfCritic
from core.compliance import ComplianceChecker
from core.post_mortem import PostMortemGenerator
from core.memory import InstitutionalMemory
from agents.personas import build_personas
from utils.logger import audit_logger
from utils.rate_limiter import RateLimiter

logger = logging.getLogger("rare.omega")


class OmegaOrchestrator:
    def __init__(self, n_mc_sims: int = 7):
        self.personas = build_personas()
        self.rate_limiter = RateLimiter(max_concurrent=settings.MAX_CONCURRENT)
        self.monte_carlo = MonteCarloEngine(self.rate_limiter, n_sims=n_mc_sims)
        self.simulator = TemporalSimulator(self.rate_limiter)
        self.economics = EconomicCalculator(self.rate_limiter)
        self.causal = CausalChainGenerator(self.rate_limiter)
        self.critic = SelfCritic(self.rate_limiter)
        self.compliance = ComplianceChecker(self.rate_limiter)
        self.post_mortem = PostMortemGenerator()
        self.memory = InstitutionalMemory()

    async def run_omega(
        self,
        scenario: str,
        telemetry: TelemetryVector,
        images: Dict[str, str],
        evidence: Optional[Dict[str, str]] = None,
        event_cb=None,
    ) -> Dict[str, Any]:
        self._event_cb = event_cb
        self._evidence = evidence or {}
        timings: Dict[str, float] = {}

        def _emit_stage(name: str):
            if event_cb:
                event_cb({"type": "stage", "name": name, "seconds": timings.get(name, 0.0)})

        # 0. Institutional Memory Lookup
        t0 = time.time()
        past_incidents = self.memory.search_similar(scenario)
        timings["memory_lookup"] = time.time() - t0

        # 1. Monte Carlo Burst
        t1 = time.time()
        prob_map = await self.monte_carlo.run(scenario, images)
        timings["monte_carlo"] = time.time() - t1
        _emit_stage("monte_carlo")

        # 2. Agent Weights
        weights = calculate_agent_weights(telemetry)

        # 3. Divergence (4 multimodal agents, in parallel)
        t2 = time.time()
        divergence = await self._run_divergence(
            scenario, images, weights, prob_map, telegram=telemetry, past=past_incidents
        )
        timings["divergence"] = time.time() - t2
        _emit_stage("divergence")

        # 4. CEO Mediation — Draft v1
        t3 = time.time()
        draft = await self._run_mediation(divergence, weights, images, scenario)
        timings["mediation"] = time.time() - t3
        _emit_stage("mediation")

        # 5. Compliance check, re-mediate if VETO
        t4 = time.time()
        compliance = await self.compliance.check(draft["text"], images)
        timings["compliance"] = time.time() - t4
        _emit_stage("compliance")

        final_strategy = draft
        re_mediation_time = 0.0
        if compliance["status"] == "VETO":
            t5 = time.time()
            logger.info("Compliance VETO received — re-mediating")
            final_strategy = await self._run_mediation(
                divergence, weights, images, scenario,
                veto_feedback=compliance["reason"],
            )
            re_mediation_time = time.time() - t5
        timings.setdefault("re_mediation", re_mediation_time)

        # 6. Temporal Simulation (3 parallel jumps)
        t6 = time.time()
        temporal = await self.simulator.simulate(final_strategy["text"], scenario, images)
        timings["temporal"] = time.time() - t6
        _emit_stage("temporal")

        # 7. If any future state FAILS → re-mediate one more time
        temporal_re_time = 0.0
        failed = [t for t in temporal if t.status == "FAIL"]
        if failed:
            t7 = time.time()
            feedback = "\n".join(f"{t.time_label}: {t.narrative}" for t in failed)
            final_strategy = await self._run_mediation(
                divergence, weights, images, scenario, temporal_feedback=feedback,
            )
            temporal_re_time = time.time() - t7
        timings.setdefault("temporal_re_mediation", temporal_re_time)

        # 8. Economics
        t8 = time.time()
        economics = await self.economics.calculate(final_strategy["text"], telemetry, images)
        timings["economics"] = time.time() - t8
        _emit_stage("economics")

        # 9. Causal Chain (XAI)
        t9 = time.time()
        causal_chain = await self.causal.generate(final_strategy["text"], telemetry, images)
        timings["causal_chain"] = time.time() - t9
        _emit_stage("causal_chain")

        # 10. Self-Critique
        t10 = time.time()
        critique = await self.critic.score(final_strategy["text"], economics, causal_chain)
        timings["self_critique"] = time.time() - t10
        _emit_stage("self_critique")

        # 11. Post-Mortem
        post_mortem = self.post_mortem.generate(
            scenario, final_strategy["text"], temporal, economics, causal_chain, critique,
        )

        # 12. Save institutional memory
        self.memory.save(scenario, final_strategy["text"], critique, economics.net_impact)

        return {
            "probability_map": prob_map,
            "divergence": divergence,
            "final_strategy": final_strategy,
            "compliance": compliance,
            "temporal": temporal,
            "economics": economics,
            "causal_chain": causal_chain,
            "self_critique": critique,
            "post_mortem": post_mortem,
            "timings": timings,
            "total_time": sum(timings.values()),
            "weights": weights,
        }

    async def _run_divergence(self, scenario, images, weights, prob_map, telegram, past):
        agent_names = ["Operator", "Diplomat", "Red Team", "Compliance"]
        tasks = []

        past_context = ""
        if past:
            p = past[0]
            past_context = f"\n\nPAST INCIDENT: {p['resolution'][:300]} (Score: {p['effectiveness']:.0f}%)"

        for name in agent_names:
            persona = self.personas[name]
            image_uri = images.get(persona["image_key"]) if persona["image_key"] else None

            user_text = (
                f"CRISIS SCENARIO:\n{scenario}\n\n"
                f"TELEMETRY WEIGHTS (your voting power): {weights}\n"
                f"MONTE CARLO PROBABILITY: success={prob_map['success']}/{prob_map['total_sims']}, "
                f"degraded={prob_map['degraded']}, fail={prob_map['fail']}\n"
                f"KEY METRICS: error_rate={telegram.hard.error_rate}%, "
                f"sentiment={telegram.soft.sentiment_score}, "
                f"churn_risk={telegram.soft.churn_risk}%\n"
                f"YOUR KPI: {persona['kpi_config']['primary_kpi']}\n"
                f"YOUR INCENTIVE: {persona['kpi_config']['incentive']}\n"
                f"{past_context}\n\n"
                "Propose your solution based on the scenario, telemetry, and any context provided. "
                "If you must VETO the current trajectory, start your reply with your veto authority label."
            )

            ev_text = self._evidence.get(persona["image_key"], "") if persona.get("image_key") else ""
            if ev_text:
                user_text += f"\n\nEVIDENCE EXTRACTED FROM YOUR IMAGE (OCR):\n{ev_text[:1500]}"

            tasks.append(self._call_agent(name, persona, user_text, [image_uri] if image_uri else None, stream=True))

        results = await asyncio.gather(*tasks)
        return results

    async def _run_mediation(self, divergence, weights, images, scenario,
                              veto_feedback=None, temporal_feedback=None):
        persona = self.personas["Arbitrator"]
        all_images = [v for v in images.values() if v]

        positions = "\n\n".join(
            f"=== {d['name']} ===\n{d['text']}\nVETO: {d.get('veto', 'None')}"
            for d in divergence
        )

        extra = ""
        if veto_feedback:
            extra += f"\n\nCOMPLIANCE VETO RECEIVED:\n{veto_feedback}\nYou MUST address this."
        if temporal_feedback:
            extra += f"\n\nTEMPORAL FAILURE PREDICTED:\n{temporal_feedback}\nYou MUST prevent this future state."

        user_text = (
            f"CRISIS: {scenario}\n"
            f"AGENT WEIGHTS: {weights}\n\n"
            f"STAKEHOLDER POSITIONS:\n{positions}\n{extra}\n\n"
            "As CEO, find the Nash Equilibrium. No KPI may be destroyed.\n"
            "Address every VETO explicitly.\n"
            "Output a single hardened strategy in markdown."
        )

        return await self._call_agent("Arbitrator", persona, user_text, all_images, stream=True)

    async def _call_agent(self, name, persona, user_text, image_uris=None, stream=False):
        async with self.rate_limiter:
            start = time.time()
            try:
                if stream and getattr(self, "_event_cb", None):
                    def _delta(d, _n=name):
                        self._event_cb({"type": "token", "agent": _n, "delta": d})
                    text = await call_gemma_stream(
                        persona["system_prompt"], user_text,
                        images=image_uris,
                        reasoning_effort=persona.get("reasoning_effort", "high"),
                        max_tokens=settings.MAX_TOKENS, on_delta=_delta,
                    )
                else:
                    text = await call_gemma(
                        persona["system_prompt"], user_text,
                        images=image_uris,
                        reasoning_effort=persona.get("reasoning_effort", "high"),
                        max_tokens=settings.MAX_TOKENS,
                    )
            except Exception as e:
                logger.warning(f"Agent {name} failed: {e}")
                text = f"AGENT_OFFLINE ({name}): {e}"

            latency = time.time() - start

            veto = None
            text_up = text.upper()
            for vtype in ["HARD_VETO", "BRAND_VETO", "SYSTEMIC_VETO", "REGULATORY_VETO"]:
                if vtype in text_up:
                    veto = vtype
                    break

            audit_logger.log_event("Omega", name, user_text[:200], text, latency)
            return {"name": name, "text": text, "veto": veto, "latency": latency}