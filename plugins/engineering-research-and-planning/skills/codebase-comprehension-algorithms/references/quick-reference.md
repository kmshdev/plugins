# Quick reference

### 1. Graph Construction & Edge Weighting (CRITICAL)

- [`graph-filter-omnipresent-utilities-before-clustering`](./graph-filter-omnipresent-utilities-before-clustering.md) — Drop the loggers and base classes BEFORE clustering (20-40 MoJoFM points)
- [`graph-pick-edge-type-by-question-asked`](./graph-pick-edge-type-by-question-asked.md) — Call, import, co-change, bipartite — the question determines the graph
- [`graph-collapse-sccs-before-clustering`](./graph-collapse-sccs-before-clustering.md) — Tarjan SCC condensation makes cycles explicit and stabilises every algorithm
- [`graph-weight-edges-by-information-content`](./graph-weight-edges-by-information-content.md) — IDF / PMI / Jaccard on edges suppresses noise (2-5× MoJoFM)
- [`graph-bipartite-file-term-for-joint-structure`](./graph-bipartite-file-term-for-joint-structure.md) — When DI / dynamic dispatch hides the call graph
- [`graph-combine-signals-in-multilayer-graphs`](./graph-combine-signals-in-multilayer-graphs.md) — Mucha 2010 multilayer modularity over normalised α-weighted layers

### 2. Community Detection & Clustering (CRITICAL)

- [`clust-leiden-not-louvain`](./clust-leiden-not-louvain.md) — Louvain produces disconnected communities on 5-25% of nodes (Traag 2019)
- [`clust-infomap-mdl-on-random-walks`](./clust-infomap-mdl-on-random-walks.md) — MDL on random walks; the right tool for flow-meaningful graphs
- [`clust-stochastic-block-model`](./clust-stochastic-block-model.md) — Bayesian, hierarchical, learns K from data; handles non-assortative structure
- [`clust-mcl-markov-clustering`](./clust-mcl-markov-clustering.md) — Flow simulation; dominant in bioinformatics; robust to noise
- [`clust-walktrap-short-random-walks`](./clust-walktrap-short-random-walks.md) — Random-walk distance + hierarchical agglomerative
- [`clust-spectral-laplacian-fiedler`](./clust-spectral-laplacian-fiedler.md) — Optimal k-way normalised cut via Laplacian eigenvectors
- [`clust-hdbscan-density-based`](./clust-hdbscan-density-based.md) — When clustering on file embeddings, not graphs

### 3. Validation & Quality Metrics (CRITICAL)

- [`valid-mojofm-as-software-clustering-distance`](./valid-mojofm-as-software-clustering-distance.md) — The SAR gold-standard distance metric (Wen-Tzerpos 2004)
- [`valid-adjusted-rand-index-and-nmi`](./valid-adjusted-rand-index-and-nmi.md) — Chance-corrected cross-algorithm comparison
- [`valid-be-aware-of-resolution-limit`](./valid-be-aware-of-resolution-limit.md) — Modularity can't see clusters smaller than √(2m) (Fortunato-Barthélemy PNAS 2007)
- [`valid-consensus-clustering-for-stability`](./valid-consensus-clustering-for-stability.md) — A single-run answer is unreliable; consensus across runs is the right answer
- [`valid-cochange-prediction-as-ground-truth-proxy`](./valid-cochange-prediction-as-ground-truth-proxy.md) — Temporal held-out co-change replaces missing ground truth
- [`valid-ablate-each-input-signal`](./valid-ablate-each-input-signal.md) — Leave-one-out; reveals which input actually drives the result

### 4. Identifier & Lexical Preprocessing (HIGH)

- [`lex-split-identifiers-with-samurai`](./lex-split-identifiers-with-samurai.md) — 87% precision vs 60% for naive camelCase (Enslen MSR 2009)
- [`lex-build-programming-language-stop-words`](./lex-build-programming-language-stop-words.md) — Three-layer: keywords + generic + IDF-driven
- [`lex-expand-abbreviations-with-context`](./lex-expand-abbreviations-with-context.md) — usr → user, ctx → context (Lawrie GenTest 2011)
- [`lex-tf-idf-and-bm25-on-identifiers`](./lex-tf-idf-and-bm25-on-identifiers.md) — Raw counts are dominated by common terms; TF-IDF / BM25 fix it
- [`lex-stem-versus-subword-tokenization`](./lex-stem-versus-subword-tokenization.md) — Porter stemmer for clustering, BPE for embeddings
- [`lex-extract-verb-object-pattern-from-method-names`](./lex-extract-verb-object-pattern-from-method-names.md) — getUserById → (verb=get, object=user); compound concept signal

### 5. Software-Specific Architecture Recovery (HIGH)

- [`arch-bunch-with-mq-fitness`](./arch-bunch-with-mq-fitness.md) — MQ fitness function + search; better than Q-maximization on code
- [`arch-acdc-subgraph-patterns`](./arch-acdc-subgraph-patterns.md) — Subsystem and skeleton patterns; matches architect intuition
- [`arch-limbo-information-bottleneck`](./arch-limbo-information-bottleneck.md) — Tishby's IB applied to software (Andritsos-Tzerpos 2005)
- [`arch-reflexion-model`](./arch-reflexion-model.md) — Compare hypothesized vs actual; the underused gem from Murphy-Notkin 1995
- [`arch-dsm-partitioning`](./arch-dsm-partitioning.md) — Design Structure Matrix; 60-year-old engineering technique

### 6. Topic Modelling on Source Code (HIGH)

- [`topic-lda-on-source-code`](./topic-lda-on-source-code.md) — Probabilistic per-file topic distributions over identifier+comment text
- [`topic-lsi-svd-on-term-document`](./topic-lsi-svd-on-term-document.md) — Deterministic SVD-based semantic embeddings (Maletic-Marcus 2001)
- [`topic-nmf-non-negative-factorization`](./topic-nmf-non-negative-factorization.md) — Parts-based additive topics, fully reproducible
- [`topic-hdp-for-nonparametric-topic-count`](./topic-hdp-for-nonparametric-topic-count.md) — Hierarchical Dirichlet Process — learns K from data
- [`topic-pick-topic-count-by-coherence-not-perplexity`](./topic-pick-topic-count-by-coherence-not-perplexity.md) — Perplexity is anti-correlated with human topic quality

### 7. Evolutionary Coupling & Co-Change Mining (HIGH)

- [`evol-mine-cochange-with-lift-and-confidence`](./evol-mine-cochange-with-lift-and-confidence.md) — Lift > 2 is the cutoff; raw co-change count is noise
- [`evol-filter-large-commits`](./evol-filter-large-commits.md) — A 200-file commit produces 20K spurious pair-counts; filter aggressively
- [`evol-temporal-decay-on-edge-weights`](./evol-temporal-decay-on-edge-weights.md) — Exponential decay with 6-month half-life
- [`evol-logical-coupling-as-architectural-signal`](./evol-logical-coupling-as-architectural-signal.md) — 30-50% of strongest coupling is invisible to static analysis (Gall 1998)

### 8. Information-Theoretic Methods (MEDIUM-HIGH)

- [`info-normalized-compression-distance`](./info-normalized-compression-distance.md) — Cluster without feature engineering; gzip-based universal similarity
- [`info-mutual-information-as-coupling`](./info-mutual-information-as-coupling.md) — Catches non-linear / conditional coupling that lift misses
- [`info-mdl-for-model-selection`](./info-mdl-for-model-selection.md) — Principled K selection; Occam's razor as a code length
- [`info-naturalness-of-code-as-quality-signal`](./info-naturalness-of-code-as-quality-signal.md) — Hindle 2012 — code is 30-50% more predictable than English; bugs spike entropy

### 9. Centrality, Hierarchy & Labelling (MEDIUM)

- [`rank-pagerank-for-module-importance`](./rank-pagerank-for-module-importance.md) — Architectural spine via PageRank on the reversed dependency graph
- [`rank-hits-hubs-and-authorities`](./rank-hits-hubs-and-authorities.md) — Orchestrators vs implementations (Kleinberg 1999)
- [`rank-betweenness-centrality-for-bottlenecks`](./rank-betweenness-centrality-for-bottlenecks.md) — Bridges between domains; god-class detection
- [`rank-textrank-for-cluster-labels`](./rank-textrank-for-cluster-labels.md) — Multi-word keyphrases as cluster labels (Mihalcea-Tarau 2004, YAKE 2020)
