"""
Smart Optimizer Tool
====================

This module implements a "Selective Attention Optimizer" that combines the
ideas introduced in ``assistant.py`` and ``communication.py``—specifically the
selective attention utilities—with the pattern-scanning power of the classic
``grep`` command.

The goal is to help simplify large codebases by:
- focusing on high-signal regions of code (selective attention)
- detecting jargon, repetition, and redundant structures (grep-like scans)
- grounding findings with contextual summaries ("grounding")
- ranking actionable improvements by impact ("gravity")

Typical usage involves instantiating :class:`SelectiveAttentionOptimizer` and
calling :meth:`SelectiveAttentionOptimizer.optimize_text`. The returned
:class:`OptimizationReport` includes:
- detected jargon occurrences
- redundancy clusters
- contextual summaries
- refactoring suggestions and synthetic usage demonstrations

Running the module directly executes a small demonstration using an inline code
snippet.
"""
from __future__ import annotations

import re
import textwrap
from collections.abc import Sequence
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class JargonOccurrence:
    """Represents a single jargon hit within a code base."""

    term: str
    line_number: int
    line_content: str


@dataclass
class RedundancyCluster:
    """Captures repeated structures or near-duplicate regions."""

    signature: str
    occurrences: list[int] = field(default_factory=list)
    preview: str = ""

    @property
    def frequency(self) -> int:
        return len(self.occurrences)


@dataclass
class OptimizationReport:
    """Aggregate results produced by the optimizer."""

    grounded_summary: str
    gravity_ranking: list[tuple[str, float]]
    jargon_hits: list[JargonOccurrence]
    redundancies: list[RedundancyCluster]
    contextual_imports: list[str]
    clarity_definitions: list[str]
    simulation_examples: list[str]

    def pretty_print(self) -> str:
        """Render the report as a human-friendly multi-line string."""

        sections = ["Selective Attention Optimization Report", "=" * 46, ""]

        sections.append("Grounded Summary:")
        sections.append(textwrap.indent(self.grounded_summary.strip(), prefix="  "))
        sections.append("")

        sections.append("Gravity Ranking (higher score = greater impact):")
        for label, score in self.gravity_ranking:
            sections.append(f"  - {label}: {score:.2f}")
        sections.append("")

        if self.jargon_hits:
            sections.append("Detected Jargon / Ambiguous Phrases:")
            for hit in self.jargon_hits:
                sections.append(
                    f"  - Line {hit.line_number}: '{hit.term}' in {hit.line_content.strip()}"
                )
            sections.append("")

        if self.redundancies:
            sections.append("Redundancy Clusters:")
            for cluster in self.redundancies:
                sections.append(
                    f"  - Signature '{cluster.signature}' repeated {cluster.frequency} times;"
                    f" sample -> {cluster.preview.strip()}"
                )
            sections.append("")

        if self.contextual_imports:
            sections.append("Contextual Import Suggestions:")
            for imp in self.contextual_imports:
                sections.append(f"  - {imp}")
            sections.append("")

        if self.clarity_definitions:
            sections.append("Definition Clarifications:")
            sections.extend(f"  - {line}" for line in self.clarity_definitions)
            sections.append("")

        if self.simulation_examples:
            sections.append("Simulation Examples:")
            sections.extend(
                textwrap.indent(example, "  ") for example in self.simulation_examples
            )
            sections.append("")

        return "\n".join(sections).strip()


# ---------------------------------------------------------------------------
# Optimizer implementation
# ---------------------------------------------------------------------------


class SelectiveAttentionOptimizer:
    """Optimize source code by combining selective attention and grep-like scans."""

    DEFAULT_JARGON = (
        "synergy",
        "paradigm",
        "ideation",
        "holistic",
        "leveraging",
        "impactful",
        "next-gen",
        "nimble",
        "mission-critical",
    )

    def __init__(
        self,
        jargon_terms: Sequence[str] | None = None,
        redundancy_window: int = 3,
        attention_focus: str = "auto",
    ) -> None:
        self.jargon_terms = tuple(sorted(set(jargon_terms or self.DEFAULT_JARGON)))
        self.redundancy_window = max(1, redundancy_window)
        self.attention_focus = attention_focus

    # ------------------------------------------------------------------
    # Core public API
    # ------------------------------------------------------------------

    def optimize_text(self, source: str) -> OptimizationReport:
        """Run the optimizer pipeline on the provided source text."""

        lines = source.splitlines()
        attention_scores = self._selective_attention(lines)
        jargon_hits = self._detect_jargon(lines)
        redundancies = self._detect_redundancies(lines)

        grounded_summary = self._generate_grounding(
            lines, attention_scores, jargon_hits, redundancies
        )
        gravity_ranking = self._apply_gravity(
            attention_scores, jargon_hits, redundancies
        )
        contextual_imports = self._suggest_imports(lines)
        clarity_definitions = self._clarify_definitions(lines)
        simulations = self._simulate_usage(clarity_definitions)

        return OptimizationReport(
            grounded_summary=grounded_summary,
            gravity_ranking=gravity_ranking,
            jargon_hits=jargon_hits,
            redundancies=redundancies,
            contextual_imports=contextual_imports,
            clarity_definitions=clarity_definitions,
            simulation_examples=simulations,
        )

    # ------------------------------------------------------------------
    # Pipeline stages
    # ------------------------------------------------------------------

    def _selective_attention(self, lines: Sequence[str]) -> dict[int, float]:
        """Compute attention scores for each line using heuristic focus modes."""

        scores: dict[int, float] = {}
        for idx, line in enumerate(lines, start=1):
            normalized = line.strip()
            if not normalized:
                continue

            length_score = min(len(normalized) / 80, 1.0)
            keyword_boost = (
                0.2 if re.search(r"\b(todo|fixme|hack)\b", normalized, re.I) else 0.0
            )
            complexity_boost = (
                0.3 if any(ch in normalized for ch in ("(", ")", "{", "}")) else 0.0
            )

            if self.attention_focus == "high_value" and length_score < 0.5:
                continue

            scores[idx] = round(
                min(1.0, length_score + keyword_boost + complexity_boost), 3
            )
        return scores

    def _detect_jargon(self, lines: Sequence[str]) -> list[JargonOccurrence]:
        """Locate jargon-like terminology using regex scans (grep analogue)."""

        matches: list[JargonOccurrence] = []
        for idx, line in enumerate(lines, start=1):
            lowered = line.lower()
            for term in self.jargon_terms:
                if term in lowered:
                    matches.append(
                        JargonOccurrence(term=term, line_number=idx, line_content=line)
                    )
        return matches

    def _detect_redundancies(self, lines: Sequence[str]) -> list[RedundancyCluster]:
        """Identify repeated n-gram signatures across the code base."""

        window = self.redundancy_window
        signatures: dict[str, RedundancyCluster] = {}

        for idx in range(len(lines) - window + 1):
            segment = tuple(line.strip() for line in lines[idx : idx + window])
            if not any(segment):
                continue

            signature = "|".join(segment)
            cluster = signatures.setdefault(
                signature,
                RedundancyCluster(signature=signature, preview="\n".join(segment[:2])),
            )
            cluster.occurrences.append(idx + 1)

        return [cluster for cluster in signatures.values() if cluster.frequency > 1]

    def _generate_grounding(
        self,
        lines: Sequence[str],
        attention_scores: dict[int, float],
        jargon_hits: Sequence[JargonOccurrence],
        redundancies: Sequence[RedundancyCluster],
    ) -> str:
        """Create a concise narrative summary contextualising findings."""

        focused_lines = sorted(
            attention_scores.items(), key=lambda item: item[1], reverse=True
        )[:5]
        focused_preview = [
            f"L{idx}: {lines[idx-1].strip()}" for idx, _ in focused_lines
        ]

        summary = [
            "Selective attention identified high-density regions requiring review.",
            f"Top focused lines: {', '.join(focused_preview) if focused_preview else 'None'}.",
            f"Jargon hits: {len(jargon_hits)} across {len(set(hit.term for hit in jargon_hits))} unique terms.",
            f"Redundancy clusters: {len(redundancies)} requiring deduplication.",
        ]
        return " ".join(summary)

    def _apply_gravity(
        self,
        attention_scores: dict[int, float],
        jargon_hits: Sequence[JargonOccurrence],
        redundancies: Sequence[RedundancyCluster],
    ) -> list[tuple[str, float]]:
        """Score remediation themes by impact ("gravity")."""

        gravity: list[tuple[str, float]] = []

        if attention_scores:
            gravity.append(("High-complexity spans", max(attention_scores.values())))
        if jargon_hits:
            gravity.append(
                (
                    "Clarify ambiguous terminology",
                    min(1.0, 0.3 + 0.1 * len(jargon_hits)),
                )
            )
        if redundancies:
            redundancy_score = min(
                1.0, 0.2 + 0.05 * sum(cluster.frequency for cluster in redundancies)
            )
            gravity.append(("Normalize repeated structures", redundancy_score))

        return sorted(gravity, key=lambda item: item[1], reverse=True)

    def _suggest_imports(self, lines: Sequence[str]) -> list[str]:
        """Infer import statements based on observed usage patterns."""

        suggestions: dict[str, str] = {}
        token_map = {
            "Path": "from pathlib import Path",
            "datetime": "from datetime import datetime",
            "json": "import json",
            "re": "import re",
            "Counter": "from collections import Counter",
        }

        for line in lines:
            for token, statement in token_map.items():
                if token in line and statement not in suggestions:
                    suggestions[statement] = token
        return list(suggestions.keys())

    def _clarify_definitions(self, lines: Sequence[str]) -> list[str]:
        """Suggest clearer definition headers for functions/classes lacking docstrings."""

        clarifications: list[str] = []
        definition_pattern = re.compile(r"^(class|def)\s+([A-Za-z_][\w]*)")

        for idx, line in enumerate(lines, start=1):
            match = definition_pattern.match(line.strip())
            if not match:
                continue

            keyword, name = match.groups()
            has_docstring = False

            # Peek ahead for docstring presence
            for look_ahead in lines[idx : idx + 3]:
                if look_ahead.strip().startswith(('"""', "'''")):
                    has_docstring = True
                    break

            if not has_docstring:
                clarifications.append(
                    f"Line {idx}: Consider adding a docstring to {keyword} `{name}` to clarify intent."
                )
        return clarifications

    def _simulate_usage(self, clarity_definitions: Sequence[str]) -> list[str]:
        """Create synthetic demonstrations of how improved code could be exercised."""

        examples: list[str] = []
        for entry in clarity_definitions[:3]:
            match = re.search(r"\b(def|class)\s+([A-Za-z_][\w]*)", entry)
            if not match:
                continue

            kind, name = match.groups()
            if kind == "def":
                examples.append(
                    textwrap.dedent(
                        f"""
                        # Example: invoking the optimized function with different arguments
                        try:
                            print({name}(42))
                            print({name}(user="alice", verbose=True))
                        except Exception as exc:
                            print("Simulation detected integration gap:", exc)
                        """
                    ).strip()
                )
            else:
                examples.append(
                    textwrap.dedent(
                        f"""
                        # Example: instantiating the class after adding clarifying docs
                        instance = {name}()
                        print("Instance:", instance)
                        """
                    ).strip()
                )
        return examples


# ---------------------------------------------------------------------------
# Demonstration harness
# ---------------------------------------------------------------------------


def _demo() -> None:
    sample_code = textwrap.dedent(
        '''
        import os
        import json  # kept for demonstration; remove if unused in real modules

        def process_data(data):
            """Return only the dictionary items from an iterable.

            Args:
                data: Iterable of arbitrary items.

            Returns:
                List of items that are dictionaries, preserving order.
            """
            result = []
            for item in data:
                if isinstance(item, dict):
                    result.append(item)
            return result

        class DataManager:
            """Lightweight container for data operations.

            Extend with concrete load/save methods as needed.
            """
            pass
        '''
    ).strip()

    optimizer = SelectiveAttentionOptimizer(attention_focus="auto")
    report = optimizer.optimize_text(sample_code)
    print(report.pretty_print())


if __name__ == "__main__":
    _demo()
