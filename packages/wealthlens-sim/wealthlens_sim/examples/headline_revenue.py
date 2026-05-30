"""End-to-end example: the headline revenue of a reform scenario.

Runs the engine over a deterministic synthetic population and prints a
WealthLens-Sim headline number — *"Reform X raises £Y bn (£low-£high)"* — with its
per-nation and per-decile breakdown and a provenance summary. The intervals are
propagated from the cited top-tail Pareto alpha range.

**Not a real estimate.** The v0.1 synthetic population is source-calibrated to
public Great Britain WAS/ONS aggregate marginals, but it is still generated data
rather than observed microdata. The headline remains illustrative until
validated against licensed microdata and behavioural assumptions. The printed
report says so on every run.

Run::

    python -m wealthlens_sim.examples.headline_revenue
"""

from __future__ import annotations

from functools import lru_cache

from wealthlens_sim import __version__ as wealthlens_sim_version
from wealthlens_sim.assumptions import load_assumptions
from wealthlens_sim.assumptions.schema import AssumptionRegistry
from wealthlens_sim.engine import EngineResult, Registries, simulate
from wealthlens_sim.reforms.a_annual_wealth import WealthTaxConfig
from wealthlens_sim.rules import FamilySelection, PolicyFamily, Scenario
from wealthlens_sim.schema.base import VersionTag
from wealthlens_sim.synth import SynthConfig, SyntheticPopulation, generate_population
from wealthlens_sim.top_tail.types import Interval


def _bn(interval: Interval) -> str:
    """Format a GBP-billions interval as ``£central bn (£low-£high)``."""
    return f"£{interval.central:,.1f} bn (£{interval.low:,.1f}-£{interval.high:,.1f})"


@lru_cache(maxsize=1)
def _population() -> SyntheticPopulation:
    """The example population, generated once (frozen + deterministic, so cacheable)."""
    return generate_population(SynthConfig(n_households=5_000, seed=20))


@lru_cache(maxsize=1)
def _assumptions() -> AssumptionRegistry:
    """The assumption registry, loaded from disk once."""
    return load_assumptions()


def example_result() -> EngineResult:
    """Score a 1%-above-£1m annual wealth tax over a seeded synthetic population.

    Deterministic: the same seed + scenario always yields the same result. A
    registry is supplied so the revenue carries real intervals and a complete
    provenance manifest. The population + registry are cached (both are immutable
    and seed-fixed), so repeated calls in tests/CLI don't re-draw or re-read disk.
    """
    population = _population()
    scenario = Scenario(
        name="annual wealth tax: 1% above £1m",
        version_tag=VersionTag(
            macro_baseline_version="NBS-2025",
            policy_version="2026-05-30",
            population_version="synth-v0.1",
            wealthlens_sim_version=wealthlens_sim_version,
        ),
        families=[
            FamilySelection(
                family=PolicyFamily.ANNUAL_WEALTH_TAX,
                config=WealthTaxConfig(threshold=1_000_000, rate=0.01),
            )
        ],
    )
    return simulate(population, scenario, registries=Registries(assumptions=_assumptions()))


_BANNER = "** ILLUSTRATIVE - synthetic, source-calibrated population; NOT a real revenue estimate **"


def build_report(result: EngineResult) -> str:
    """Render a human-readable headline report for ``result``.

    The headline line is self-labelled and a banner heads the report so that no
    single line can be lifted out of context and quoted as a real estimate.
    """
    lines = [
        _BANNER,
        "",
        f"Scenario: {result.scenario.name}",
        f"Population: {result.households_scored:,} synthetic households (source-calibrated, still illustrative)",
        "",
        f"  Headline revenue (ILLUSTRATIVE / synthetic): {_bn(result.total_revenue_gbp_bn)}",
        "",
        "  By nation:",
    ]
    for nation in sorted(result.revenue_by_nation):
        label = nation.replace("_", " ").title()
        lines.append(f"    {label:<18} {_bn(result.revenue_by_nation[nation])}")
    lines.append("")
    lines.append("  By wealth decile (lowest -> highest):")
    for i, interval in enumerate(result.revenue_by_decile, start=1):
        lines.append(f"    decile {i:>2}          {_bn(interval)}")
    lines.append("")
    consumed = sorted(result.provenance.assumptions_consumed)
    lines.append(
        f"  Provenance: {'complete' if result.provenance_complete else 'INCOMPLETE'}; "
        f"assumptions consumed: {', '.join(consumed) or 'none'}"
    )
    lines.append(
        "  Note: the v0.1 synthetic population is calibrated to public Great "
        "Britain ONS/WAS aggregate marginals, but it is still synthetic data "
        "rather than observed microdata. Intervals propagate the cited top-tail "
        "Pareto alpha. Verify behavioural assumptions and calibration before "
        "publishing."
    )
    return "\n".join(lines)


def main() -> None:
    print(build_report(example_result()))


if __name__ == "__main__":  # pragma: no cover - manual entry point
    main()
