# des-contracts

Shared contracts for the Digital Earth Sweden agentic workflow. One package, multiple consumers. Every repo in the portfolio that needs to agree on a data shape, an analyzer interface, or a retrieval config pins this package instead of duplicating definitions.

Per the [`agentic_workflow` rollout plan](https://github.com/TobiasEdman/agentic_workflow/blob/main/docs/rollout_plan.md) Wave 3. Addresses the "C6 shared contracts layer" finding from the cross-repo improvements report — three independent lenses (imint, ecosystem-pair, leo+sdl) recommended extracting a package exactly like this.

## What's inside

| Module | Purpose | Consumers |
|---|---|---|
| `des_contracts.schema` | 23-class unified LULC schema (NMD + LPIS + SKS) with SJV-code mappings | ImintEngine, space-data-lab, vhr-lab (future), leo-constellation (future) |
| `des_contracts.analyzer` | `Analyzer` protocol + registry format | leo-constellation, space-data-lab, ImintEngine |
| `des_contracts.kg` | JSON Schema for Swedish-space-ecosystem KG exports (`kg_core`, `kg_views`) | swedish-space-ecosystem-v2, swedish-space-ecosystem-viz, future consumers |
| `des_contracts.rag` | Canonical embedding model + chunking config | des-agent, des-chatbot |
| `des_contracts.registry` | Registry format for cataloguing analyzers across repos | leo-constellation, space-data-lab, ImintEngine |

## Why a separate package

From the repo-improvements analysis:

- The **23-class schema** has gone through v1..v5 inside ImintEngine without a migration mechanism; extracting it enables versioning
- **JSON Schema for KG exports** lets viz consumers reject bad payloads at load time (currently fails only at runtime in JS)
- **Embedding model config** diverged between des-agent (`nomic-embed-text`, 768-dim) and des-chatbot (`all-MiniLM-L6-v2`, 384-dim) — a shared canonical manifest forces the choice to be explicit
- **Analyzer base class** enables graduation from leo-constellation / space-data-lab → ImintEngine with a stable API

## Install

```bash
# From PyPI (future)
pip install des-contracts

# From git for now
pip install 'git+https://github.com/TobiasEdman/des-contracts.git@v0.1.0#egg=des-contracts'
```

## Versioning

- **Semver.** `v0.x.y` during extraction phase. `v1.0.0` when all Tier A consumers have migrated.
- **Breaking changes bump major.** Adding a new class, renaming a field, changing embedding dim → major bump.
- **Additive changes bump minor.** New Analyzer capability flag, new optional schema metadata → minor bump.
- **Fixes bump patch.**

Consumers pin tight: `des-contracts>=0.1,<0.2` during `0.x`, `>=1,<2` from `1.0` onward.

## Consumer quickstart

```python
# 23-class schema + SJV-code mapping
from des_contracts.schema import UNIFIED_CLASSES, SJV_TO_UNIFIED

# Analyzer base (subclass or implement the Protocol)
from des_contracts.analyzer import Analyzer, AnalyzerResult

# JSON Schema for KG exports
from des_contracts.kg import KG_CORE_SCHEMA, KG_VIEWS_SCHEMA

# Canonical embedding config
from des_contracts.rag import EMBEDDING_CONFIG
```

## Development

```bash
git clone https://github.com/TobiasEdman/des-contracts
cd des-contracts
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## License

Proprietary — RISE Research Institutes of Sweden. Will reconsider at `v1.0` based on adoption outside the internal portfolio.
