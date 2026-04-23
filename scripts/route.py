"""katib route — end-to-end routing (sensor → gate → action).

Thin JSON-emitting CLI that chains:

    context_sensor.infer_signals(transcript)   # Day 9
    gate.evaluate(signals, capabilities)        # Day 8
    gate.resolve(q1, q2, closest)               # Day 8 (after AskUserQuestion)

Two subcommands:

    route.py infer     — first pass. Reads transcript, fires the gate, emits
                         next action as JSON (render / present_candidates /
                         ask_questions / ask_intent / error).

    route.py resolve   — second pass. After the agent has run AskUserQuestion
                         on a fired gate, consume the Q1/Q2 labels and emit
                         the final action (render / wait / graduate).

Output contract: ALL exit paths emit exactly one JSON document on stdout.
Errors emit {"action": "error", ...}. Raw tracebacks are caught at main().

Agent flow (from SKILL.md):

    1. Write transcript to tempfile
    2. uv run scripts/route.py infer --transcript-file <path> [--lang X] [--brand Y] [--recipe Z]
    3. Parse JSON; dispatch on "action":
        - "render"              → uv run scripts/build.py <recipe> --lang X --brand Y
        - "present_candidates"  → AskUserQuestion → pick recipe → re-call infer with --recipe
        - "ask_questions"       → AskUserQuestion (payload embedded) →
                                   uv run scripts/route.py resolve --q1 ... --q2 ...
        - "ask_intent"          → ask user (plain text) → re-call infer with new transcript
        - "error"               → relay message to user

Stale capabilities.yaml is auto-regenerated if any recipe file is newer.
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from dataclasses import asdict, is_dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.capabilities import load_capabilities  # noqa: E402
from core.context_sensor import enumerate_brands, infer_signals  # noqa: E402
from core.gate import (  # noqa: E402
    Signals,
    evaluate,
    resolve,
)

CAPS_FILE = REPO_ROOT / "capabilities.yaml"
RECIPES_DIR = REPO_ROOT / "recipes"
COMPONENTS_DIR = REPO_ROOT / "components"


# ---------------------------------------------------------------- helpers


def _dumps(obj: dict) -> str:
    """JSON serialize, preserving dataclasses via asdict()."""
    return json.dumps(obj, ensure_ascii=False, default=_json_default)


def _json_default(o):
    if is_dataclass(o):
        return asdict(o)
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"not JSON-serializable: {type(o).__name__}")


def _ensure_capabilities_fresh() -> tuple[dict, list[str]]:
    """Regenerate capabilities.yaml if any recipe or component is newer.

    Returns (caps_dict, notes[]) — notes records whether a regen happened.
    """
    notes: list[str] = []
    newest_source = 0.0
    for d in (RECIPES_DIR, COMPONENTS_DIR):
        if not d.exists():
            continue
        for p in d.rglob("*.yaml"):
            mtime = p.stat().st_mtime
            if mtime > newest_source:
                newest_source = mtime

    caps_mtime = CAPS_FILE.stat().st_mtime if CAPS_FILE.exists() else 0.0
    if newest_source > caps_mtime:
        # Regenerate via subprocess to keep this script small
        import subprocess

        result = subprocess.run(
            ["uv", "run", "scripts/generate_capabilities.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            notes.append(
                f"capabilities regeneration failed: {result.stderr.strip()}"
            )
        else:
            notes.append("capabilities.yaml regenerated (sources newer)")

    return load_capabilities(), notes


def _build_plan_action(plan, inference=None) -> dict:
    """Emit a render action from a ResolvedPlan."""
    return {
        "action": "render",
        "recipe": plan.recipe,
        "lang": plan.lang,
        "brand": plan.brand,
        "slug": plan.slug,
        "summary": inference.summary if inference else None,
        "reasons": inference.reasons if inference else [],
    }


def _build_candidates_action(candidates, summary, confidence) -> dict:
    """MEDIUM outcome — top 2-4 candidates as an AUQ-compatible payload."""
    options = []
    # AUQ accepts 2-4 options; cap at 4.
    for m in candidates[:4]:
        desc = m.data.get("description") or ""
        target_pages = m.data.get("target_pages")
        pages_str = (
            f" ({target_pages[0]}–{target_pages[1]}pp)"
            if isinstance(target_pages, list) and len(target_pages) == 2
            else ""
        )
        options.append(
            {
                "label": m.name,
                "description": (desc[:110] + "...") if len(desc) > 110 else desc + pages_str,
            }
        )
    # Ensure min 2 options for AUQ — pad with a "not listed" escape if only 1
    if len(options) < 2:
        options.append(
            {
                "label": "None of these — ask me instead",
                "description": "I don't see a fit; let's discuss what you need.",
            }
        )
    return {
        "action": "present_candidates",
        "confidence": confidence,
        "summary": summary,
        "question": {
            "question": "Which recipe matches your document?",
            "header": "Pick recipe",
            "options": options,
            "multiSelect": False,
        },
    }


def _build_ask_questions_action(decision, inference) -> dict:
    """LOW outcome — gate fired 2 questions (FIT + FREQUENCY)."""
    return {
        "action": "ask_questions",
        "confidence": decision.confidence.level,
        "summary": inference.summary,
        "closest_recipe": decision.closest.name if decision.closest else None,
        "closest_score": decision.closest.score if decision.closest else None,
        "intent": inference.signals.intent,
        "questions": [q.to_ask_user_question() for q in decision.questions],
        # Label→value mapping the agent needs after AUQ returns answers
        "answer_map": {
            "fit": {
                "Yes, fits": "yes-fits",
                "Partial fit": "partial",
                "No, fundamentally different": "no-different",
            },
            "frequency": {
                "One-off": "one-off",
                "Occasional": "occasional",
                "Recurring": "recurring",
            },
        },
    }


def _build_ask_intent_action(message, inference) -> dict:
    return {
        "action": "ask_intent",
        "message": message,
        "summary": inference.summary if inference else None,
    }


# ---------------------------------------------------------------- infer


def _cmd_infer(args) -> dict:
    # 1. Load + freshen capabilities
    caps, cap_notes = _ensure_capabilities_fresh()

    # 2. Read transcript
    if args.transcript_file:
        transcript = Path(args.transcript_file).read_text(encoding="utf-8")
    elif args.transcript:
        transcript = args.transcript
    else:
        transcript = ""

    # 3. Run sensor
    known = enumerate_brands()
    inference = infer_signals(transcript, known_brands=known)

    # 4. Apply explicit overrides
    override_notes: list[str] = []
    signals = inference.signals
    if args.lang:
        if signals.lang and signals.lang != args.lang:
            override_notes.append(
                f"lang override: inferred={signals.lang} → explicit={args.lang}"
            )
        signals = Signals(
            intent=signals.intent,
            lang=args.lang,
            brand=signals.brand,
            known_brands=signals.known_brands,
        )
    if args.brand:
        if signals.brand and signals.brand != args.brand:
            override_notes.append(
                f"brand override: inferred={signals.brand} → explicit={args.brand}"
            )
        signals = Signals(
            intent=signals.intent,
            lang=signals.lang,
            brand=args.brand,
            known_brands=signals.known_brands,
        )

    # 5. Explicit recipe short-circuits the gate entirely
    if args.recipe:
        if args.recipe not in caps.get("recipes", {}):
            return {
                "action": "error",
                "code": "unknown_recipe",
                "message": (
                    f"Recipe {args.recipe!r} not found in capabilities.yaml. "
                    f"Available: {sorted(caps.get('recipes', {}).keys())}"
                ),
            }
        lang = signals.lang or "en"
        out = {
            "action": "render",
            "recipe": args.recipe,
            "lang": lang,
            "brand": signals.brand,
            "slug": args.slug,
            "summary": f"Explicit recipe {args.recipe!r}; lang={lang}; brand={signals.brand or 'default'}.",
            "reasons": inference.reasons + override_notes,
        }
        if cap_notes:
            out["capability_notes"] = cap_notes
        return out

    # 6. Gate
    decision = evaluate(signals, caps)

    # Observability: include summary + reasons on every outcome
    base_reasons = inference.reasons + override_notes + decision.confidence.reasons

    if decision.outcome == "proceed":
        plan = decision.plan
        if args.slug:
            plan.slug = args.slug
        out = _build_plan_action(plan, inference)
        out["confidence"] = decision.confidence.level
        out["reasons"] = base_reasons
    elif decision.outcome == "choose":
        out = _build_candidates_action(
            decision.candidates, inference.summary, decision.confidence.level
        )
        out["reasons"] = base_reasons
    elif decision.outcome == "fire":
        out = _build_ask_questions_action(decision, inference)
        out["reasons"] = base_reasons
    else:  # needs-intent
        message = (
            decision.message
            or "No intent extracted — please describe the document you want to render."
        )
        out = _build_ask_intent_action(message, inference)
        out["reasons"] = base_reasons

    if cap_notes:
        out["capability_notes"] = cap_notes
    return out


# ---------------------------------------------------------------- resolve


def _cmd_resolve(args) -> dict:
    caps, cap_notes = _ensure_capabilities_fresh()
    # Rebuild a minimal closest — route.py resolve is stateless between
    # calls, so the caller re-supplies the closest recipe name + intent.
    from core.capabilities import find_closest_recipe

    closest = None
    if args.closest_recipe:
        recipes = caps.get("recipes", {})
        if args.closest_recipe in recipes:
            from core.capabilities import RecipeMatch

            data = recipes[args.closest_recipe]
            closest = RecipeMatch(
                name=args.closest_recipe,
                score=0.0,
                data=dict(data),
                reasons=["re-attached from resolve args"],
            )
        else:
            return {
                "action": "error",
                "code": "unknown_recipe",
                "message": f"closest recipe {args.closest_recipe!r} not found in capabilities",
            }
    elif args.intent:
        closest = find_closest_recipe(args.intent, caps)

    try:
        resolution = resolve(
            args.q1,
            args.q2,
            closest,
            intent=args.intent or "",
            force_graduation=args.force_graduation,
            force_graduation_justification=args.justification,
        )
    except ValueError as e:
        return {"action": "error", "code": "bad_resolve_args", "message": str(e)}

    if resolution.action == "fill-closest" or resolution.action == "log-and-fill":
        out = {
            "action": "render",
            "recipe": resolution.fill_recipe,
            "lang": args.lang or "en",
            "brand": args.brand,
            "slug": args.slug,
            "reasons": resolution.reasons,
            "log_entry": resolution.log_entry,  # Day 13 writer consumes this
            "resolved_action": resolution.action,
        }
    elif resolution.action == "log-and-wait":
        out = {
            "action": "wait",
            "message": (
                "Your request has been logged for graduation review. "
                "No render will happen — a new recipe would be needed."
            ),
            "reasons": resolution.reasons,
            "log_entry": resolution.log_entry,
        }
    else:  # request-graduation
        out = {
            "action": "graduate",
            "message": (
                "Graduation requested. This requires scaffolding a new recipe; "
                "review the justification and run the component/recipe CLI."
            ),
            "reasons": resolution.reasons,
            "log_entry": resolution.log_entry,
        }
    if cap_notes:
        out["capability_notes"] = cap_notes
    return out


# ---------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_infer = sub.add_parser("infer", help="Run context sensor → gate, emit next action.")
    src = p_infer.add_mutually_exclusive_group()
    src.add_argument("--transcript-file", type=str, help="Path to transcript text file.")
    src.add_argument("--transcript", type=str, help="Transcript inline (small inputs).")
    p_infer.add_argument("--recipe", type=str, help="Explicit recipe override — skips gate.")
    p_infer.add_argument("--lang", type=str, choices=["en", "ar", "bilingual"])
    p_infer.add_argument("--brand", type=str, help="Explicit brand override.")
    p_infer.add_argument("--slug", type=str, help="Output folder slug override.")
    p_infer.set_defaults(func=_cmd_infer)

    p_resolve = sub.add_parser("resolve", help="Resolve gate Q1/Q2 answers to final action.")
    p_resolve.add_argument("--q1", required=True, choices=["yes-fits", "partial", "no-different"])
    p_resolve.add_argument(
        "--q2", required=True, choices=["one-off", "occasional", "recurring"]
    )
    p_resolve.add_argument("--closest-recipe", type=str, help="Name of closest recipe from infer step.")
    p_resolve.add_argument("--intent", type=str, help="Original intent text.")
    p_resolve.add_argument("--lang", type=str, choices=["en", "ar", "bilingual"])
    p_resolve.add_argument("--brand", type=str)
    p_resolve.add_argument("--slug", type=str)
    p_resolve.add_argument("--force-graduation", action="store_true")
    p_resolve.add_argument("--justification", type=str)
    p_resolve.set_defaults(func=_cmd_resolve)

    args = ap.parse_args(argv)

    try:
        out = args.func(args)
    except Exception as e:
        # Never let a raw traceback hit stdout — would break the subprocess
        # JSON contract. Emit structured error; log trace to stderr.
        traceback.print_exc(file=sys.stderr)
        out = {
            "action": "error",
            "code": "internal_error",
            "message": f"{type(e).__name__}: {e}",
        }

    print(_dumps(out))
    return 0 if out.get("action") != "error" else 1


if __name__ == "__main__":
    sys.exit(main())
