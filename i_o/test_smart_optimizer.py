"""
Comprehensive unit tests for Smart Optimizer
"""

import pytest
import textwrap
from smart_optimizer import (
    SelectiveAttentionOptimizer,
    OptimizationReport,
    JargonOccurrence,
    RedundancyCluster
)


class TestJargonOccurrence:
    """Test JargonOccurrence dataclass."""

    def test_jargon_occurrence_creation(self):
        """Test creating JargonOccurrence instances."""
        occurrence = JargonOccurrence(
            term="synergy",
            line_number=5,
            line_content="We need to leverage synergy here"
        )

        assert occurrence.term == "synergy"
        assert occurrence.line_number == 5
        assert occurrence.line_content == "We need to leverage synergy here"

    def test_jargon_occurrence_equality(self):
        """Test JargonOccurrence equality."""
        occ1 = JargonOccurrence("paradigm", 10, "test line")
        occ2 = JargonOccurrence("paradigm", 10, "test line")
        occ3 = JargonOccurrence("synergy", 10, "test line")

        assert occ1 == occ2
        assert occ1 != occ3


class TestRedundancyCluster:
    """Test RedundancyCluster dataclass."""

    def test_redundancy_cluster_creation(self):
        """Test creating RedundancyCluster instances."""
        cluster = RedundancyCluster(
            signature="def test():",
            occurrences=[1, 5, 10],
            preview="def test(): pass"
        )

        assert cluster.signature == "def test():"
        assert cluster.occurrences == [1, 5, 10]
        assert cluster.preview == "def test(): pass"
        assert cluster.frequency == 3

    def test_redundancy_cluster_empty(self):
        """Test RedundancyCluster with no occurrences."""
        cluster = RedundancyCluster(signature="test")
        assert cluster.frequency == 0


class TestOptimizationReport:
    """Test OptimizationReport dataclass."""

    def test_optimization_report_creation(self):
        """Test creating OptimizationReport instances."""
        jargon = [JargonOccurrence("synergy", 5, "line content")]
        redundancies = [RedundancyCluster("signature", [1, 2])]
        report = OptimizationReport(
            grounded_summary="Test summary",
            gravity_ranking=[("test", 0.8)],
            jargon_hits=jargon,
            redundancies=redundancies,
            contextual_imports=["import os"],
            clarity_definitions=["Line 1: Add docstring"],
            simulation_examples=["example code"]
        )

        assert report.grounded_summary == "Test summary"
        assert len(report.jargon_hits) == 1
        assert len(report.redundancies) == 1

    def test_pretty_print_basic(self):
        """Test pretty printing of optimization report."""
        report = OptimizationReport(
            grounded_summary="Basic summary",
            gravity_ranking=[("test", 0.5)],
            jargon_hits=[],
            redundancies=[],
            contextual_imports=[],
            clarity_definitions=[],
            simulation_examples=[]
        )

        output = report.pretty_print()
        assert "Basic summary" in output
        assert "test: 0.50" in output

    def test_pretty_print_with_content(self):
        """Test pretty printing with full content."""
        jargon = [JargonOccurrence("paradigm", 3, "def paradigm():")]
        redundancies = [RedundancyCluster("def test():", [1, 5])]
        report = OptimizationReport(
            grounded_summary="Full test summary",
            gravity_ranking=[("high", 0.9), ("low", 0.1)],
            jargon_hits=jargon,
            redundancies=redundancies,
            contextual_imports=["import json"],
            clarity_definitions=["Line 1: Add docstring to function"],
            simulation_examples=["print('test')"]
        )

        output = report.pretty_print()
        assert "Full test summary" in output
        assert "paradigm" in output
        assert "def test():" in output
        assert "import json" in output


class TestSelectiveAttentionOptimizer:
    """Test SelectiveAttentionOptimizer class."""

    def test_optimizer_creation_default(self):
        """Test creating optimizer with default parameters."""
        optimizer = SelectiveAttentionOptimizer()
        assert len(optimizer.jargon_terms) > 0
        assert "synergy" in optimizer.jargon_terms
        assert optimizer.redundancy_window == 3
        assert optimizer.attention_focus == "auto"

    def test_optimizer_creation_custom(self):
        """Test creating optimizer with custom parameters."""
        custom_jargon = ["custom", "terms"]
        optimizer = SelectiveAttentionOptimizer(
            jargon_terms=custom_jargon,
            redundancy_window=5,
            attention_focus="high_value"
        )

        assert optimizer.jargon_terms == ("custom", "terms")
        assert optimizer.redundancy_window == 5
        assert optimizer.attention_focus == "high_value"

    def test_selective_attention_basic(self):
        """Test selective attention scoring."""
        optimizer = SelectiveAttentionOptimizer()
        lines = [
            "short line",
            "this is a much longer line with more content",
            "   indented line   ",
            "",
            "def function(param):",
            "    # TODO: implement this",
            "    return param + 1"
        ]

        scores = optimizer._selective_attention(lines)

        # Should have scores for non-empty lines
        assert len(scores) > 0
        # Lines with keywords should have higher scores
        assert any(score > 0.1 for score in scores.values())

    def test_detect_jargon_basic(self):
        """Test basic jargon detection."""
        optimizer = SelectiveAttentionOptimizer(jargon_terms=["synergy", "paradigm"])
        lines = [
            "This line has synergy",
            "Normal line",
            "Another paradigm here",
            "SYNERGY in caps",  # Should be case insensitive
        ]

        hits = optimizer._detect_jargon(lines)

        assert len(hits) == 3  # synergy, paradigm, SYNERGY
        terms = [hit.term for hit in hits]
        assert "synergy" in terms
        assert "paradigm" in terms

    def test_detect_jargon_no_matches(self):
        """Test jargon detection with no matches."""
        optimizer = SelectiveAttentionOptimizer(jargon_terms=["nonexistent"])
        lines = ["normal line", "another line"]

        hits = optimizer._detect_jargon(lines)
        assert len(hits) == 0

    def test_detect_redundancies_basic(self):
        """Test basic redundancy detection."""
        optimizer = SelectiveAttentionOptimizer(redundancy_window=2)
        lines = [
            "def test():",
            "    pass",
            "def test():",  # Duplicate
            "    pass",
            "def other():",
            "    return 1"
        ]

        clusters = optimizer._detect_redundancies(lines)

        assert len(clusters) == 1
        cluster = clusters[0]
        assert cluster.signature == "def test():|pass"
        assert cluster.frequency == 2
        assert cluster.occurrences == [1, 3]

    def test_detect_redundancies_no_duplicates(self):
        """Test redundancy detection with no duplicates."""
        optimizer = SelectiveAttentionOptimizer()
        lines = ["line 1", "line 2", "line 3"]

        clusters = optimizer._detect_redundancies(lines)
        assert len(clusters) == 0

    def test_generate_grounding(self):
        """Test grounding summary generation."""
        optimizer = SelectiveAttentionOptimizer()
        lines = ["def test():", "normal line"]
        scores = {1: 0.8, 2: 0.3}
        jargon = [JargonOccurrence("test", 1, "line")]
        redundancies = [RedundancyCluster("sig", [1, 2])]

        summary = optimizer._generate_grounding(lines, scores, jargon, redundancies)

        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "jargon hits" in summary.lower()
        assert "redundancy clusters" in summary.lower()

    def test_apply_gravity_basic(self):
        """Test gravity ranking calculation."""
        optimizer = SelectiveAttentionOptimizer()
        scores = {1: 0.8, 2: 0.6}
        jargon = [JargonOccurrence("term", 1, "line")] * 3
        redundancies = [RedundancyCluster("sig", [1, 2, 3])]

        ranking = optimizer._apply_gravity(scores, jargon, redundancies)

        assert isinstance(ranking, list)
        assert len(ranking) > 0
        # Should be sorted by score descending
        assert ranking[0][1] >= ranking[-1][1]

    def test_suggest_imports_basic(self):
        """Test import suggestion functionality."""
        optimizer = SelectiveAttentionOptimizer()
        lines = [
            "import os",
            "from pathlib import Path",
            "Path",
            "datetime.now()",
            "json.dumps(data)"
        ]

        suggestions = optimizer._suggest_imports(lines)

        # Should suggest imports for used but not imported items
        assert isinstance(suggestions, list)

    def test_clarity_definitions_basic(self):
        """Test clarity definition suggestions."""
        optimizer = SelectiveAttentionOptimizer()
        lines = [
            "def function_without_docstring():",
            "    pass",
            "",
            "class ClassWithoutDocstring:",
            "    pass",
            "",
            'def function_with_docstring():',
            '    """This has a docstring"""',
            "    pass"
        ]

        definitions = optimizer._clarify_definitions(lines)

        assert isinstance(definitions, list)
        # Should find functions/classes without docstrings
        assert len(definitions) > 0
        assert "function_without_docstring" in str(definitions)
        assert "ClassWithoutDocstring" in str(definitions)

    def test_simulate_usage_basic(self):
        """Test usage simulation generation."""
        optimizer = SelectiveAttentionOptimizer()
        definitions = [
            "Line 1: Consider adding a docstring to def test_function",
            "Line 5: Consider adding a docstring to class TestClass"
        ]

        simulations = optimizer._simulate_usage(definitions)

        assert isinstance(simulations, list)
        assert len(simulations) <= 3  # Limited to 3 examples

    def test_optimize_text_integration(self):
        """Test full optimization pipeline."""
        sample_code = textwrap.dedent("""
            import os
            def test_function():
                synergy = "test"
                paradigm = synergy * 2
                return paradigm

            def another_function():
                synergy = "duplicate"
                paradigm = synergy * 2
                return paradigm
        """).strip()

        optimizer = SelectiveAttentionOptimizer()
        report = optimizer.optimize_text(sample_code)

        assert isinstance(report, OptimizationReport)
        assert report.grounded_summary
        assert isinstance(report.gravity_ranking, list)
        assert isinstance(report.jargon_hits, list)
        assert isinstance(report.redundancies, list)
        assert isinstance(report.contextual_imports, list)
        assert isinstance(report.clarity_definitions, list)
        assert isinstance(report.simulation_examples, list)


class TestOptimizerEdgeCases:
    """Test optimizer edge cases and error conditions."""

    def test_empty_source_code(self):
        """Test optimization of empty source code."""
        optimizer = SelectiveAttentionOptimizer()
        report = optimizer.optimize_text("")

        assert isinstance(report, OptimizationReport)
        assert report.grounded_summary != ""

    def test_single_line_code(self):
        """Test optimization of single line."""
        optimizer = SelectiveAttentionOptimizer()
        report = optimizer.optimize_text("print('hello')")

        assert isinstance(report, OptimizationReport)

    def test_unicode_content(self):
        """Test optimization with unicode content."""
        code_with_unicode = """
        def función_español():
            '''Función con acentos'''
            return "🚀 unicode test"
        """

        optimizer = SelectiveAttentionOptimizer()
        report = optimizer.optimize_text(code_with_unicode)

        assert isinstance(report, OptimizationReport)

    def test_large_redundancy_window(self):
        """Test with large redundancy window."""
        optimizer = SelectiveAttentionOptimizer(redundancy_window=10)
        lines = ["line"] * 15

        clusters = optimizer._detect_redundancies(lines)
        # Should find redundancy even with large window
        assert len(clusters) > 0

    def test_attention_focus_modes(self):
        """Test different attention focus modes."""
        modes = ["auto", "high_value"]

        for mode in modes:
            optimizer = SelectiveAttentionOptimizer(attention_focus=mode)
            lines = ["short", "this is a very long line with lots of content"] * 5

            scores = optimizer._selective_attention(lines)
            assert isinstance(scores, dict)

    def test_custom_jargon_terms(self):
        """Test with custom jargon terms."""
        custom_terms = ["foo", "bar", "baz"]
        optimizer = SelectiveAttentionOptimizer(jargon_terms=custom_terms)

        code = "foo bar baz normal words"
        report = optimizer.optimize_text(code)

        # Should find the custom jargon terms
        jargon_terms = [hit.term for hit in report.jargon_hits]
        for term in custom_terms:
            assert term in jargon_terms


class TestPrettyPrintFormatting:
    """Test pretty printing formatting."""

    def test_pretty_print_empty_report(self):
        """Test pretty printing of empty report."""
        report = OptimizationReport(
            grounded_summary="",
            gravity_ranking=[],
            jargon_hits=[],
            redundancies=[],
            contextual_imports=[],
            clarity_definitions=[],
            simulation_examples=[]
        )

        output = report.pretty_print()
        assert "Selective Attention Optimization Report" in output

    def test_pretty_print_special_characters(self):
        """Test pretty printing with special characters."""
        report = OptimizationReport(
            grounded_summary="Summary with → special ← chars",
            gravity_ranking=[("test→", 0.5)],
            jargon_hits=[JargonOccurrence("→", 1, "→ special")],
            redundancies=[],
            contextual_imports=[],
            clarity_definitions=[],
            simulation_examples=[]
        )

        output = report.pretty_print()
        assert "→" in output

    def test_pretty_print_long_content(self):
        """Test pretty printing with long content."""
        long_jargon = [JargonOccurrence("term", i, f"very long line content {i}" * 10)
                      for i in range(10)]

        report = OptimizationReport(
            grounded_summary="Long summary " * 20,
            gravity_ranking=[(f"item{i}", i/10) for i in range(10)],
            jargon_hits=long_jargon,
            redundancies=[],
            contextual_imports=[f"import{i}" for i in range(10)],
            clarity_definitions=[f"definition{i}" for i in range(10)],
            simulation_examples=[f"example{i}" for i in range(10)]
        )

        output = report.pretty_print()
        assert isinstance(output, str)
        assert len(output) > 1000  # Should be substantial


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
