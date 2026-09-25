---
name: codebase-comprehension-algorithms
description: Choose and validate algorithms for clustering a codebase into features or architectural modules.
---
# Community Codebase Comprehension And Domain Mapping Algorithms Best Practices

A practitioner-oriented reference of the **algorithms that work for mapping a codebase into understandable feature/business domains**. Most of these techniques live in the Software Architecture Recovery and Mining Software Repositories literatures and are invisible to working engineers — yet they're the right tools for the job a coding agent is asked to do every day: *"what does this codebase do, and where?"*

The 47 rules are organized by **execution-lifecycle impact**: a wrong decision early in the pipeline (which graph to build, which identifiers to keep) propagates through everything downstream. The three CRITICAL categories (`graph-`, `clust-`, `valid-`) are the ones a wrong call cannot be recovered from later. Read them first.

**Scope**: proven algorithms with peer-reviewed citations or canonical books — Newman *Networks*, Leskovec-Rajaraman-Ullman *Mining of Massive Datasets*, Ganter-Wille *Formal Concept Analysis*, plus 40+ ICSE / FSE / TSE / PNAS / JMLR papers. No tutorial sites, no Stack Overflow, no marketing posts. Deliberately deferred to a future version: GNN/CodeBERT/code2vec (not "proven over decades" yet) and refactoring-recipe stuff (covered by sibling skills like `react-refactor` and `typescript-refactor`).

## When to Apply

Use these rules when:

- Onboarding an agent into an unfamiliar codebase: "explain what this codebase does, by domain"
- Producing an architecture map: "what are the main subsystems and how do they connect?"
- Locating a feature: "which files implement payments / authentication / search?"
- Reviewing a refactor: "did this change respect the architectural boundaries?"
- Detecting architectural debt: "what files have surprising coupling?"
- Validating an existing decomposition: "does the README's architecture match the code?"
- Picking algorithms for any of the above — the user wants something that's *proven*, not vibes

## Rule Categories By Priority

| # | Category | Prefix | Impact | What it does |
|---|----------|--------|--------|--------------|
| 1 | Graph Construction & Edge Weighting | `graph-` | CRITICAL | Which graph to build; omnipresent filter; cycle handling; multilayer |
| 2 | Community Detection & Clustering | `clust-` | CRITICAL | Leiden, Infomap, SBM, MCL, Walktrap, spectral, HDBSCAN |
| 3 | Validation & Quality Metrics | `valid-` | CRITICAL | MoJoFM, ARI/NMI, resolution limit, consensus, co-change prediction, ablation |
| 4 | Identifier & Lexical Preprocessing | `lex-` | HIGH | Samurai splitting, abbreviation expansion, TF-IDF/BM25, stemming, V-O parsing |
| 5 | Software-Specific Architecture Recovery | `arch-` | HIGH | Bunch + MQ, ACDC, Limbo, Reflexion, DSM |
| 6 | Topic Modelling on Source Code | `topic-` | HIGH | LDA, LSI/SVD, NMF, HDP, coherence-based K selection |
| 7 | Evolutionary Coupling & Co-Change Mining | `evol-` | HIGH | Lift / confidence / support, large-commit filter, temporal decay, logical coupling |
| 8 | Information-Theoretic Methods | `info-` | MEDIUM-HIGH | Normalized Compression Distance, Mutual Information, MDL, code naturalness |
| 9 | Centrality, Hierarchy & Labelling | `rank-` | MEDIUM | PageRank, HITS, betweenness, TextRank/YAKE labels |

## Reference routing

Use the category table above to choose a topic. Open [the rule index](references/quick-reference.md) only to locate the specific rule, then read that rule’s reference file.

## How to Use

Start with the question the agent is trying to answer:

- **"What are the main domains in this codebase?"** → `graph-` (pick a graph) → `clust-` (Leiden / Infomap / SBM) → `topic-` (label them) → `valid-` (sanity-check stability and ablate)
- **"Which files implement feature X?"** → `topic-lda-on-source-code` for theme location; `rank-pagerank-for-module-importance` with X's files as seed for personalized PageRank
- **"Where is the architectural spine?"** → `rank-pagerank-for-module-importance` + `rank-hits-hubs-and-authorities` on the dependency graph
- **"Does the README's architecture match the code?"** → `arch-reflexion-model` is purpose-built for this
- **"What's the *real* coupling here (beyond static dependencies)?"** → `evol-logical-coupling-as-architectural-signal` and `evol-mine-cochange-with-lift-and-confidence`
- **"How do I cluster without designing features?"** → `info-normalized-compression-distance`
- **"How big are the clusters supposed to be?"** → `valid-be-aware-of-resolution-limit` and `topic-hdp-for-nonparametric-topic-count`
- **"How do I know my decomposition is right?"** → the entire `valid-` category; multi-proxy evaluation is mandatory

The skill's worldview: **build the right graph first** (and filter omnipresent files), **pick an algorithm matching the graph and the question**, **use a code-specific preprocessing pipeline** (Samurai + stop-words + stemming + TF-IDF) where lexical signals matter, and **always validate** — MoJoFM if you have expert ground truth, consensus + co-change prediction + ablation if you don't.

Code examples are in Python because the reference implementations (networkx, igraph, leidenalg, scikit-learn, gensim, graph-tool, hdbscan) all live there. The reasoning generalises to any language.

## Reference Files

| File | Description |
|------|-------------|
| [references/_sections.md](references/_sections.md) | Category definitions and ordering |
| [assets/templates/_template.md](assets/templates/_template.md) | Template for new rules |
| [compiled guide](references/compiled-guide.md) | Auto-built TOC navigation |

## Related Skills

- `computer-science-algorithms` — Algorithm-and-data-structure reference (this skill cross-references it for MinHash/LSH, Aho-Corasick, etc.)
- `complexity-optimizer` — Static analysis for hot paths the rules here identify
- `design-to-react-algorithms` — Companion skill for design-to-code structural recovery
