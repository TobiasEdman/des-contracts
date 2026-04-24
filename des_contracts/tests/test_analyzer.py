"""Tests for the Analyzer protocol and result dataclasses."""
from des_contracts.analyzer import (
    Analyzer,
    AnalyzerInput,
    AnalyzerResult,
    AnalyzerStatus,
)


def test_status_enum_values():
    assert AnalyzerStatus.CANDIDATE.value == "candidate"
    assert AnalyzerStatus.STABLE.value == "stable"
    assert AnalyzerStatus.DEPRECATED.value == "deprecated"
    assert AnalyzerStatus.REMOVED.value == "removed"


def test_analyzer_input_defaults():
    inp = AnalyzerInput()
    assert inp.aoi is None
    assert inp.temporal_range is None
    assert inp.data == {}
    assert inp.config == {}


def test_analyzer_result_defaults():
    r = AnalyzerResult(analyzer_name="x", analyzer_version="0.1.0")
    assert r.status == "success"
    assert r.error is None
    assert r.data == {}
    assert r.metrics == {}
    assert r.metadata == {}


class _ConformingAnalyzer:
    name = "test"
    version = "0.1.0"
    supports_throttle = False
    precision_modes = ["fp32"]

    def configure(self, config):
        self._config = config

    def run(self, input):
        return AnalyzerResult(
            analyzer_name=self.name,
            analyzer_version=self.version,
            data={"hits": 42},
        )

    def to_yaml_template(self):
        return "threshold: 0.5\n"


def test_runtime_protocol_check_accepts_conforming_class():
    assert isinstance(_ConformingAnalyzer(), Analyzer)


def test_runtime_protocol_rejects_missing_method():
    class Incomplete:
        name = "x"
        version = "0.1.0"
        supports_throttle = False
        precision_modes = ["fp32"]

        def configure(self, config):
            pass
        # Missing: run, to_yaml_template

    assert not isinstance(Incomplete(), Analyzer)
