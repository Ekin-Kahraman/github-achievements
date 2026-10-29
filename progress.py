"""Combine observed badges with optional, explicitly supplied event counts."""

from checker import TIER_ORDER


def build_report(catalog, badges, counts=None):
    counts = {} if counts is None else counts
    if not isinstance(counts, dict):
        raise ValueError("Counts must be a JSON object keyed by achievement ID")
    known_ids = {entry["id"] for entry in catalog["achievements"]}
    if set(counts) - known_ids:
        raise ValueError("Unknown achievement ID in counts")
    if any(type(value) is not int or value < 0 for value in counts.values()):
        raise ValueError("Counts must be nonnegative integers")
    rows = []
    for entry in catalog["achievements"]:
        slug = entry["id"]
        observed = badges.get(slug)
        current_tier = observed["tier"] if observed else None
        milestones = sorted(entry["tiers"].items(), key=lambda pair: pair[1])
        # An unknown asset format is not enough evidence to infer a tier.
        if observed and current_tier not in TIER_ORDER:
            next_tier, target = None, None
        else:
            remaining_tiers = [
                (tier, minimum) for tier, minimum in milestones
                if not observed or TIER_ORDER[tier] > TIER_ORDER[current_tier]
            ]
            next_tier, target = remaining_tiers[0] if remaining_tiers else (None, None)
        count = counts.get(slug)
        rows.append({
            "id": slug,
            "name": entry["name"],
            "visible": observed is not None,
            "observed_tier": current_tier,
            "metric": entry["metric"],
            "supplied_count": count,
            "next_tier": next_tier,
            "target": target,
            "remaining": max(0, target - count) if target is not None and count is not None else None,
            "requires_payment": entry.get("requires_payment", False),
        })
    return rows
