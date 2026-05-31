"""Structured domain knowledge for the 33 AI subject areas.

Each domain entry supplies the *real* technical substance that the
generators compose into full chapters. The goal is enterprise-grade,
non-filler content: every ``concept`` becomes the seed of a chapter, and
the supporting fields (architecture, patterns, best practices, pitfalls,
use cases, glossary, references) are woven through the document.
"""
from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Helper: a domain entry is a plain dict. We keep them in a list so order is
# deterministic, then index by slug.
# ---------------------------------------------------------------------------

_DOMAIN_LIST: list[dict[str, Any]] = [
    {
        "name": "AI Foundations",
        "tagline": "The mathematical and engineering bedrock of modern AI",
        "language": "python",
        "overview": (
            "Artificial intelligence is the discipline of building systems that perceive, "
            "reason and act to achieve goals under uncertainty. Modern AI is dominated by "
            "machine learning, in which models infer parameters from data rather than from "
            "hand-coded rules. Foundational competence spans linear algebra, probability, "
            "optimisation, information theory and the engineering practices required to turn "
            "a notebook experiment into a governed production service. This book treats AI "
            "foundations as a systems discipline: data, models, evaluation and operations are "
            "co-designed, and every modelling decision is traced to a measurable business or "
            "scientific objective."
        ),
        "concepts": [
            ("The AI/ML Landscape and Problem Framing",
             "Distinguishing supervised, unsupervised, self-supervised and reinforcement "
             "learning; mapping a business problem to a learnable objective; and deciding "
             "when not to use machine learning at all."),
            ("Linear Algebra for Machine Learning",
             "Vectors, matrices, norms, eigendecomposition and the singular value "
             "decomposition as the language of representation and dimensionality reduction."),
            ("Probability, Statistics and Bayesian Reasoning",
             "Random variables, distributions, maximum likelihood, the bias–variance "
             "decomposition and calibrated uncertainty as the foundation of trustworthy "
             "prediction."),
            ("Optimisation and Gradient Descent",
             "Loss surfaces, convexity, stochastic gradient descent, momentum, Adam and "
             "learning-rate schedules that make deep networks trainable at scale."),
            ("Data Engineering and Feature Pipelines",
             "Ingestion, validation, feature stores, leakage prevention and reproducible "
             "datasets as the highest-leverage investment in any AI program."),
            ("Model Families and Inductive Bias",
             "Linear models, trees and ensembles, kernel methods and neural networks, and "
             "how their inductive biases suit different data regimes."),
            ("Neural Networks and Backpropagation",
             "Perceptrons, activation functions, the chain rule, automatic differentiation "
             "and the universal-approximation intuition behind deep learning."),
            ("Evaluation, Metrics and Experimental Design",
             "Train/validation/test discipline, cross-validation, ROC/PR analysis, "
             "statistical significance and the perils of metric gaming."),
            ("Regularisation and Generalisation",
             "Overfitting, weight decay, dropout, early stopping and the modern view of "
             "double descent in over-parameterised models."),
            ("Representation Learning and Embeddings",
             "Learning compact, transferable representations that power transfer learning "
             "and downstream tasks across modalities."),
            ("Responsible and Trustworthy AI by Design",
             "Fairness, robustness, privacy and explainability treated as first-class "
             "requirements rather than afterthoughts."),
            ("From Notebook to Production",
             "Packaging, serving, monitoring and the operational loop that keeps models "
             "performing as data drifts."),
            ("Scaling Laws and Compute Economics",
             "How model quality scales with data, parameters and compute, and how to make "
             "rational build-versus-buy decisions."),
            ("The Modern AI Stack",
             "Frameworks, accelerators, orchestration and the reference architecture that "
             "ties data, training and inference together."),
        ],
        "architecture": (
            "A foundational AI platform separates four planes: a data plane (ingestion, "
            "validation, feature store), a training plane (experiment tracking, distributed "
            "training, model registry), a serving plane (low-latency and batch inference, "
            "feature retrieval) and a governance plane (lineage, access control, audit). "
            "Clean interfaces between planes allow teams to evolve each independently while "
            "preserving reproducibility and compliance."
        ),
        "patterns": [
            "Feature store as the single source of truth for online/offline parity",
            "Model registry with staged promotion (dev → staging → production)",
            "Champion/challenger evaluation before any production swap",
            "Reproducible pipelines pinned by data, code and environment hashes",
        ],
        "best_practices": [
            "Establish a held-out test set early and never touch it during development.",
            "Track every experiment with code, data and hyper-parameter provenance.",
            "Prefer the simplest model that meets the requirement before adding complexity.",
            "Measure calibration, not just accuracy, for decision-support systems.",
            "Automate data validation to catch schema and distribution drift before training.",
        ],
        "pitfalls": [
            "Target leakage that inflates offline metrics and collapses in production.",
            "Optimising a proxy metric that diverges from the true business objective.",
            "Ignoring class imbalance and reporting misleading accuracy.",
            "Coupling preprocessing to a single notebook, destroying reproducibility.",
        ],
        "use_cases": [
            ("Financial Services", "Credit risk scoring with calibrated probabilities and "
             "auditable feature lineage for regulators."),
            ("Healthcare", "Clinical decision support where uncertainty estimates and "
             "explainability are prerequisites for adoption."),
            ("Retail", "Demand forecasting and price elasticity modelling feeding "
             "automated replenishment."),
            ("Manufacturing", "Predictive maintenance from sensor telemetry to reduce "
             "unplanned downtime."),
        ],
        "tools": ["PyTorch", "scikit-learn", "NumPy", "MLflow", "Feast", "Ray", "ONNX"],
        "glossary": [
            ("Inductive bias", "Assumptions a model makes to generalise beyond training data."),
            ("Overfitting", "Fitting noise in the training set at the expense of generalisation."),
            ("Calibration", "Agreement between predicted probabilities and observed frequencies."),
            ("Feature store", "A system for serving consistent features to training and inference."),
        ],
        "references": [
            "Goodfellow, Bengio & Courville — Deep Learning (MIT Press)",
            "Bishop — Pattern Recognition and Machine Learning (Springer)",
            "Murphy — Probabilistic Machine Learning (MIT Press)",
            "Huyen — Designing Machine Learning Systems (O'Reilly)",
        ],
    },
    {
        "name": "Generative AI",
        "tagline": "Designing, deploying and governing systems that create content",
        "language": "python",
        "overview": (
            "Generative AI refers to models that synthesise novel content—text, images, "
            "audio, code and structured data—by learning the distribution of training data "
            "and sampling from it. The enterprise value lies not in novelty but in "
            "productivity: drafting, summarisation, code generation, synthetic data and "
            "customer interaction. This book frames generative AI as a capability that must "
            "be productised: grounded in enterprise data, guarded against harmful output, "
            "evaluated continuously and operated under clear cost and latency budgets."
        ),
        "concepts": [
            ("Generative Modelling Foundations",
             "Likelihood-based versus implicit models; autoregressive, diffusion and "
             "variational approaches and the trade-offs between fidelity and diversity."),
            ("Large Language Models as Generators",
             "Next-token prediction, sampling strategies (temperature, top-k, top-p) and the "
             "emergence of instruction following."),
            ("Diffusion Models for Images and Audio",
             "Forward/reverse diffusion, denoising objectives, latent diffusion and "
             "classifier-free guidance."),
            ("Multimodal Generation",
             "Joint text–image–audio models, cross-attention conditioning and unified "
             "tokenisation strategies."),
            ("Grounding with Enterprise Data",
             "Retrieval augmentation, tool use and structured outputs to keep generations "
             "factual and policy-compliant."),
            ("Controllability and Structured Output",
             "Constrained decoding, JSON/schema enforcement and function calling for "
             "reliable downstream integration."),
            ("Evaluation of Generative Systems",
             "Reference-based and reference-free metrics, LLM-as-judge, human preference "
             "evaluation and red-teaming."),
            ("Safety, Guardrails and Content Moderation",
             "Input/output filtering, jailbreak resistance and layered defence in depth."),
            ("Cost, Latency and Throughput Engineering",
             "Token economics, caching, batching, distillation and routing across model "
             "tiers."),
            ("Synthetic Data Generation",
             "Augmenting scarce datasets, privacy-preserving generation and avoiding model "
             "collapse from recursive training."),
            ("Enterprise Use-Case Patterns",
             "Assistants, copilots, summarisers and autonomous workflows mapped to value."),
            ("Productionising Generative Applications",
             "Prompt management, versioning, observability and continuous evaluation in CI."),
            ("Governance and Intellectual Property",
             "Provenance, watermarking, licensing and the legal landscape of generated "
             "content."),
            ("The GenAI Reference Architecture",
             "Gateways, orchestration, retrieval, guardrails and evaluation as a cohesive "
             "platform."),
        ],
        "architecture": (
            "A production generative-AI platform places a model gateway in front of one or "
            "more foundation models, with orchestration handling prompt assembly, retrieval, "
            "tool calls and guardrails. A semantic cache reduces cost and latency, an "
            "evaluation service scores responses offline and online, and an observability "
            "layer captures prompts, completions, tokens, cost and quality signals for every "
            "request."
        ),
        "patterns": [
            "Model gateway abstracting multiple providers behind one API",
            "Retrieval-augmented grounding to reduce hallucination",
            "Guardrail sandwich: validate inputs, constrain decoding, validate outputs",
            "Semantic caching keyed on normalised prompts and embeddings",
        ],
        "best_practices": [
            "Treat prompts as versioned, tested artefacts under source control.",
            "Always ground high-stakes generations in retrieved, citable sources.",
            "Define explicit cost and latency budgets per use case and route accordingly.",
            "Run an automated evaluation suite on every prompt or model change.",
        ],
        "pitfalls": [
            "Shipping ungrounded generations into high-stakes workflows.",
            "Ignoring token cost growth as adoption scales.",
            "Relying on a single provider with no fallback or routing strategy.",
            "Evaluating only with anecdotes instead of a versioned test set.",
        ],
        "use_cases": [
            ("Legal", "Contract drafting and clause extraction with citation back to source."),
            ("Software", "Code generation, refactoring and test synthesis inside the IDE."),
            ("Marketing", "Brand-safe content generation with human-in-the-loop review."),
            ("Customer Service", "Grounded assistants that resolve tickets with cited policy."),
        ],
        "tools": ["OpenAI API", "Anthropic Claude", "LangChain", "LlamaIndex", "vLLM", "Diffusers"],
        "glossary": [
            ("Autoregressive model", "A model that generates output one token at a time."),
            ("Diffusion model", "A generator that learns to reverse a noising process."),
            ("Hallucination", "Confident but unsupported or fabricated model output."),
            ("Guardrail", "A control that constrains model inputs or outputs."),
        ],
        "references": [
            "Ho et al. — Denoising Diffusion Probabilistic Models (2020)",
            "Brown et al. — Language Models are Few-Shot Learners (2020)",
            "Rombach et al. — High-Resolution Image Synthesis with Latent Diffusion (2022)",
        ],
    },
    {
        "name": "Prompt Engineering",
        "tagline": "Engineering reliable behaviour from foundation models",
        "language": "python",
        "overview": (
            "Prompt engineering is the discipline of designing inputs, context and decoding "
            "settings that steer foundation models toward reliable, useful behaviour. It "
            "spans instruction design, in-context learning, structured output, tool use and "
            "evaluation. In the enterprise, prompts are software: they are specified, "
            "versioned, tested and monitored. This book elevates prompting from folklore to "
            "an engineering practice with measurable quality, regression testing and clear "
            "separation between prompt logic, retrieved context and model configuration."
        ),
        "concepts": [
            ("Anatomy of a Prompt",
             "System, developer and user roles; instructions, context, examples and output "
             "specification as distinct, composable parts."),
            ("Zero-, One- and Few-Shot Prompting",
             "How in-context examples shape behaviour and when demonstrations beat "
             "instructions."),
            ("Chain-of-Thought and Reasoning Prompts",
             "Eliciting intermediate reasoning, self-consistency sampling and the cost/"
             "quality trade-offs of deliberate reasoning."),
            ("Structured Output and Schema Enforcement",
             "JSON mode, function/tool calling and grammar-constrained decoding for reliable "
             "integration."),
            ("Retrieval-Augmented Prompting",
             "Injecting grounded context, citation discipline and context-window budgeting."),
            ("Tool Use and Function Calling",
             "Letting models invoke functions, search and code execution within a controlled "
             "loop."),
            ("Prompt Templates and Composition",
             "Parameterised templates, partials and guardrail wrappers for reuse at scale."),
            ("Decoding Parameters and Sampling",
             "Temperature, top-p, penalties and stop sequences as levers on determinism."),
            ("Prompt Evaluation and Regression Testing",
             "Golden datasets, LLM-as-judge, rubric scoring and CI gates for prompt changes."),
            ("Defending Against Prompt Injection",
             "Untrusted-content isolation, instruction hierarchy and output validation."),
            ("Multi-Step and Agentic Prompting",
             "Planner/executor patterns, reflection and decomposition of complex tasks."),
            ("Prompt Management and Versioning",
             "Registries, A/B testing and rollback for production prompts."),
            ("Cost-Aware Prompt Design",
             "Compression, context pruning and caching to control token spend."),
            ("Patterns, Anti-Patterns and a Style Guide",
             "A reusable library of prompt patterns and the failure modes to avoid."),
        ],
        "architecture": (
            "Production prompting introduces a prompt management service that stores "
            "versioned templates, an assembly layer that merges instructions with retrieved "
            "context under a token budget, and an evaluation harness that scores candidate "
            "prompts against golden datasets before promotion. Telemetry links every "
            "completion back to the exact prompt version that produced it."
        ),
        "patterns": [
            "Instruction hierarchy: system > developer > user > retrieved content",
            "Template + slots with explicit output schema",
            "Self-consistency voting for high-stakes reasoning",
            "Critique-and-revise loops for quality improvement",
        ],
        "best_practices": [
            "Specify the output format explicitly and validate it programmatically.",
            "Keep untrusted content clearly delimited and never executed as instructions.",
            "Version prompts and gate changes behind an evaluation suite.",
            "Prefer fewer, higher-quality few-shot examples over many noisy ones.",
        ],
        "pitfalls": [
            "Treating prompts as throwaway strings with no testing or versioning.",
            "Overlong contexts that dilute attention and inflate cost.",
            "Mixing untrusted user content with trusted instructions (injection risk).",
            "Relying on temperature tweaks instead of structural prompt fixes.",
        ],
        "use_cases": [
            ("Support", "Deterministic, schema-constrained ticket triage and routing."),
            ("Analytics", "Natural-language-to-SQL with validation against a catalog."),
            ("Operations", "Runbook automation with tool calls and confirmation gates."),
            ("Education", "Socratic tutoring with rubric-based answer evaluation."),
        ],
        "tools": ["OpenAI", "Anthropic", "Guidance", "Outlines", "PromptLayer", "LangSmith"],
        "glossary": [
            ("Few-shot", "Providing examples in the prompt to steer behaviour."),
            ("Chain-of-thought", "Prompting a model to reason step by step."),
            ("Prompt injection", "An attack that smuggles instructions via input content."),
            ("Constrained decoding", "Forcing output to match a grammar or schema."),
        ],
        "references": [
            "Wei et al. — Chain-of-Thought Prompting (2022)",
            "Wang et al. — Self-Consistency Improves Chain of Thought (2022)",
            "OpenAI — Prompt Engineering Guide",
        ],
    },
    {
        "name": "LLMs",
        "tagline": "Architecture, training and serving of large language models",
        "language": "python",
        "overview": (
            "Large language models are transformer-based neural networks trained on vast text "
            "corpora to predict the next token, acquiring broad linguistic and reasoning "
            "capabilities that transfer across tasks. Understanding LLMs requires fluency in "
            "their architecture, the pre-training/alignment lifecycle, tokenisation, "
            "inference economics and the operational realities of serving them at scale. This "
            "book covers the full lifecycle from corpus curation to a governed, monitored "
            "inference endpoint."
        ),
        "concepts": [
            ("From N-grams to Neural Language Models",
             "The evolution of language modelling and why scale plus self-attention "
             "unlocked emergent capability."),
            ("Tokenisation and Vocabulary",
             "Byte-pair encoding, subword units, special tokens and their impact on cost and "
             "multilingual performance."),
            ("The Transformer Backbone of LLMs",
             "Decoder-only architectures, attention, positional encodings and layer "
             "normalisation choices."),
            ("Pre-training Objectives and Data",
             "Causal language modelling, corpus curation, deduplication and data quality at "
             "trillion-token scale."),
            ("Scaling Laws and Emergent Abilities",
             "Compute-optimal training, the Chinchilla insight and capability phase "
             "transitions."),
            ("Instruction Tuning and Alignment",
             "Supervised fine-tuning, RLHF and preference optimisation that make base models "
             "useful and safe."),
            ("Context Windows and Long-Context Techniques",
             "Position interpolation, attention variants and retrieval to extend effective "
             "context."),
            ("Inference Optimisation",
             "KV caching, speculative decoding, quantisation and continuous batching for "
             "throughput."),
            ("Serving LLMs at Scale",
             "GPU memory planning, tensor/pipeline parallelism and autoscaling inference."),
            ("Evaluation and Benchmarking",
             "Capability benchmarks, contamination, and task-specific golden sets."),
            ("Hallucination and Factuality",
             "Why models confabulate and how grounding and decoding mitigate it."),
            ("Cost and Capacity Planning",
             "Token economics, hardware sizing and build-versus-buy decisions."),
            ("Safety and Alignment in Production",
             "Layered safety, refusal behaviour and policy enforcement."),
            ("The LLM Platform Reference Architecture",
             "Gateways, registries, evaluation and observability for fleets of models."),
        ],
        "architecture": (
            "An LLM serving platform comprises a request gateway with auth and rate limiting, "
            "an inference cluster running an optimised engine (paged KV cache, continuous "
            "batching, quantised weights), a routing layer selecting model size by task, and "
            "an observability pipeline tracking latency, tokens and quality. Model artefacts "
            "flow from a registry with signed provenance into blue/green serving slots."
        ),
        "patterns": [
            "Model routing by difficulty (small model first, escalate on low confidence)",
            "Continuous batching with paged attention for GPU efficiency",
            "Speculative decoding with a small draft model",
            "Blue/green model rollout with shadow evaluation",
        ],
        "best_practices": [
            "Right-size the model to the task; do not pay for capability you don't use.",
            "Quantise and batch aggressively, validating quality impact with evals.",
            "Pin model and tokenizer versions; treat upgrades as releases.",
            "Monitor token distribution to catch prompt bloat and cost regressions.",
        ],
        "pitfalls": [
            "Assuming bigger is always better instead of measuring task fit.",
            "Underestimating KV-cache memory for long contexts.",
            "Silent tokenizer changes that break prompts and cost models.",
            "Benchmarking on contaminated datasets and over-claiming capability.",
        ],
        "use_cases": [
            ("Enterprise Search", "Answering questions over internal knowledge with citations."),
            ("Software", "Code completion and review across large repositories."),
            ("Finance", "Summarising filings and extracting structured facts."),
            ("Telecom", "Tier-1 support automation with escalation to humans."),
        ],
        "tools": ["vLLM", "TensorRT-LLM", "Hugging Face Transformers", "Ollama", "SGLang"],
        "glossary": [
            ("Token", "The atomic unit of text an LLM processes."),
            ("KV cache", "Stored key/value tensors that speed up autoregressive decoding."),
            ("Quantisation", "Reducing numeric precision to shrink memory and speed inference."),
            ("Context window", "The maximum tokens a model can attend to at once."),
        ],
        "references": [
            "Vaswani et al. — Attention Is All You Need (2017)",
            "Hoffmann et al. — Training Compute-Optimal LLMs (Chinchilla, 2022)",
            "Kwon et al. — Efficient Memory Management for LLM Serving (vLLM, 2023)",
        ],
    },
    {
        "name": "Transformers",
        "tagline": "The architecture that powers modern AI",
        "language": "python",
        "overview": (
            "The transformer is a neural architecture built on self-attention that processes "
            "sequences in parallel and models long-range dependencies without recurrence. It "
            "underpins virtually all modern foundation models across text, vision, audio and "
            "multimodal domains. Mastery requires understanding attention mathematics, "
            "positional encoding, normalisation, and the engineering optimisations that make "
            "training and inference tractable at scale."
        ),
        "concepts": [
            ("Why Self-Attention Replaced Recurrence",
             "Parallelism, long-range dependency modelling and the limitations of RNNs/LSTMs "
             "that transformers overcame."),
            ("Scaled Dot-Product Attention",
             "Queries, keys, values, the scaling factor and the softmax that produces "
             "context-aware representations."),
            ("Multi-Head Attention",
             "Projecting into multiple subspaces to attend to different relations "
             "simultaneously."),
            ("Positional Encoding",
             "Sinusoidal, learned and rotary (RoPE) encodings that inject order into a "
             "permutation-invariant operation."),
            ("Feed-Forward Networks and Activations",
             "Position-wise MLPs, GELU/SwiGLU and their role in capacity."),
            ("Residual Connections and Normalisation",
             "Pre-norm versus post-norm, LayerNorm/RMSNorm and training stability."),
            ("Encoder, Decoder and Encoder–Decoder Variants",
             "BERT-style, GPT-style and T5-style architectures and their use cases."),
            ("Efficient Attention",
             "FlashAttention, sparse and linear attention to tame quadratic cost."),
            ("Vision and Multimodal Transformers",
             "Patch embeddings, ViT and cross-modal attention."),
            ("Mixture-of-Experts Transformers",
             "Sparse routing for parameter-efficient scaling."),
            ("Training Dynamics and Stability",
             "Initialisation, warmup, gradient clipping and loss spikes."),
            ("Implementing a Transformer from Scratch",
             "A minimal, correct implementation that demystifies every component."),
            ("Profiling and Optimising Transformers",
             "Memory, FLOPs, kernel fusion and hardware-aware design."),
            ("The Transformer Design Space",
             "A map of architectural choices and their empirical trade-offs."),
        ],
        "architecture": (
            "A transformer block stacks multi-head self-attention and a position-wise "
            "feed-forward network, each wrapped in residual connections and normalisation. "
            "Decoder-only stacks add causal masking; encoder–decoder stacks add cross "
            "attention. At scale, efficient attention kernels, mixed precision and "
            "tensor parallelism turn the mathematics into a trainable system."
        ),
        "patterns": [
            "Pre-norm residual blocks for deep stability",
            "Rotary positional embeddings for length generalisation",
            "FlashAttention for memory-efficient exact attention",
            "Mixture-of-experts routing for sparse scaling",
        ],
        "best_practices": [
            "Use pre-norm and careful warmup to stabilise deep transformer training.",
            "Adopt fused attention kernels to cut memory and latency.",
            "Validate positional encoding choice against target sequence lengths.",
            "Profile FLOPs and memory before scaling parameters.",
        ],
        "pitfalls": [
            "Quadratic attention cost dominating long-sequence workloads.",
            "Numerical instability from post-norm at depth.",
            "Position encoding that fails to extrapolate beyond training length.",
            "Ignoring kernel-level efficiency and over-provisioning hardware.",
        ],
        "use_cases": [
            ("NLP", "Language understanding and generation across tasks."),
            ("Computer Vision", "Image classification and detection with ViT backbones."),
            ("Audio", "Speech recognition and synthesis with transformer encoders."),
            ("Science", "Protein structure and molecular property prediction."),
        ],
        "tools": ["PyTorch", "FlashAttention", "Triton", "xFormers", "Hugging Face"],
        "glossary": [
            ("Self-attention", "Relating positions within a single sequence."),
            ("Multi-head", "Parallel attention in multiple representation subspaces."),
            ("RoPE", "Rotary positional embedding encoding relative position."),
            ("MoE", "Mixture-of-experts; sparse activation of subnetworks."),
        ],
        "references": [
            "Vaswani et al. — Attention Is All You Need (2017)",
            "Dao et al. — FlashAttention (2022)",
            "Su et al. — RoFormer / Rotary Position Embedding (2021)",
        ],
    },
    {
        "name": "Embeddings",
        "tagline": "Dense representations that power search and retrieval",
        "language": "python",
        "overview": (
            "Embeddings map discrete objects—words, sentences, images, users, products—into "
            "continuous vector spaces where geometric proximity encodes semantic similarity. "
            "They are the connective tissue of modern AI: powering semantic search, "
            "retrieval-augmented generation, recommendation, clustering and classification. "
            "This book covers how embeddings are trained, evaluated, indexed and operated as "
            "a production capability with versioning and drift monitoring."
        ),
        "concepts": [
            ("From One-Hot to Distributed Representations",
             "Why dense vectors generalise where sparse encodings cannot."),
            ("Word, Sentence and Document Embeddings",
             "Word2Vec, GloVe, sentence transformers and pooling strategies."),
            ("Contrastive Representation Learning",
             "InfoNCE, positive/negative mining and the geometry of good embeddings."),
            ("Similarity Metrics and Normalisation",
             "Cosine, dot product and Euclidean distance and when each applies."),
            ("Multimodal and Cross-Encoder Embeddings",
             "CLIP-style joint spaces and the bi-encoder/cross-encoder trade-off."),
            ("Dimensionality, Compression and Quantisation",
             "Matryoshka embeddings, PCA and product quantisation for cost control."),
            ("Indexing for Approximate Nearest Neighbour Search",
             "HNSW, IVF and the recall/latency frontier."),
            ("Evaluating Embedding Quality",
             "Retrieval metrics (recall@k, MRR, nDCG) and benchmark suites like MTEB."),
            ("Domain Adaptation and Fine-Tuning",
             "Adapting general embeddings to specialised corpora."),
            ("Embedding Drift and Re-Indexing",
             "Detecting model changes and managing versioned vector stores."),
            ("Hybrid Search",
             "Combining lexical (BM25) and dense retrieval with fusion."),
            ("Operating an Embedding Service",
             "Batching, caching, versioning and cost at scale."),
            ("Privacy and Embedding Inversion",
             "What embeddings leak and how to mitigate it."),
            ("The Retrieval Stack Reference Architecture",
             "Embedding service, vector index and re-ranking as a pipeline."),
        ],
        "architecture": (
            "An embedding platform exposes a versioned embedding service that batches and "
            "caches encode requests, writes vectors to an ANN index (HNSW/IVF) with stored "
            "metadata, and supports hybrid retrieval that fuses lexical and dense scores "
            "before an optional cross-encoder re-ranks the top candidates."
        ),
        "patterns": [
            "Bi-encoder retrieval followed by cross-encoder re-ranking",
            "Hybrid lexical + dense fusion (reciprocal rank fusion)",
            "Matryoshka embeddings for adaptive dimensionality",
            "Versioned indexes with blue/green re-embedding",
        ],
        "best_practices": [
            "Normalise vectors and pick the distance metric the model was trained for.",
            "Pin embedding model versions and re-index atomically on change.",
            "Evaluate retrieval with recall@k and nDCG on a labelled set.",
            "Use hybrid search to recover exact-match and rare-term queries.",
        ],
        "pitfalls": [
            "Mixing vectors from different model versions in one index.",
            "Choosing the wrong similarity metric for the embedding model.",
            "Over-chunking or under-chunking documents before embedding.",
            "Ignoring drift after upgrading the embedding model.",
        ],
        "use_cases": [
            ("Search", "Semantic search across heterogeneous enterprise content."),
            ("E-commerce", "Visual and textual product similarity and recommendation."),
            ("Support", "Deduplicating and routing tickets by semantic similarity."),
            ("Compliance", "Near-duplicate detection across document repositories."),
        ],
        "tools": ["sentence-transformers", "OpenAI embeddings", "FAISS", "Cohere", "MTEB"],
        "glossary": [
            ("Embedding", "A dense vector representation of an object."),
            ("Cosine similarity", "Similarity based on the angle between vectors."),
            ("ANN", "Approximate nearest-neighbour search."),
            ("Re-ranking", "Refining retrieval order with a stronger model."),
        ],
        "references": [
            "Mikolov et al. — Word2Vec (2013)",
            "Reimers & Gurevych — Sentence-BERT (2019)",
            "Radford et al. — CLIP (2021)",
        ],
    },
    {
        "name": "Vector Databases",
        "tagline": "Storing and searching high-dimensional vectors at scale",
        "language": "python",
        "overview": (
            "Vector databases store embeddings alongside metadata and provide fast "
            "approximate nearest-neighbour search, filtering and hybrid retrieval. They are "
            "the storage backbone of retrieval-augmented generation and semantic search. This "
            "book covers indexing algorithms, consistency and scaling models, metadata "
            "filtering, and how to operate a vector store with the same rigour as any "
            "production datastore."
        ),
        "concepts": [
            ("The Case for Purpose-Built Vector Stores",
             "Why ANN, filtering and freshness demand specialised systems."),
            ("ANN Indexing Algorithms",
             "HNSW graphs, IVF, PQ and DiskANN and their recall/latency/memory profiles."),
            ("Distance Metrics and Quantisation",
             "Cosine/dot/L2 and scalar/product quantisation trade-offs."),
            ("Metadata Filtering and Hybrid Queries",
             "Pre- versus post-filtering and combining structured predicates with vectors."),
            ("Sharding, Replication and Scaling",
             "Horizontal scaling, consistency models and high availability."),
            ("Freshness, Upserts and Deletes",
             "Handling streaming updates without full re-indexing."),
            ("Hybrid and Multi-Vector Retrieval",
             "Late-interaction (ColBERT) and sparse+dense fusion."),
            ("Benchmarking Vector Databases",
             "Recall, QPS, p99 latency and cost per million vectors."),
            ("Security and Multi-Tenancy",
             "Namespace isolation, access control and encryption."),
            ("Cost and Capacity Planning",
             "Memory versus disk indexes and right-sizing infrastructure."),
            ("Operating in Production",
             "Backups, monitoring, re-indexing and disaster recovery."),
            ("Choosing a Vector Database",
             "Managed versus self-hosted and integration considerations."),
            ("Integration with the RAG Pipeline",
             "Where the vector store sits and how it is queried."),
            ("Reference Architecture and Patterns",
             "A production-grade deployment blueprint."),
        ],
        "architecture": (
            "A vector database deployment partitions collections into shards, each holding an "
            "ANN index in memory or on SSD, replicated for availability. A query coordinator "
            "fans out filtered ANN searches, merges results and applies metadata predicates. "
            "An ingestion path handles upserts and deletes with background index maintenance."
        ),
        "patterns": [
            "Namespace-per-tenant isolation",
            "Pre-filter on selective metadata, post-filter otherwise",
            "Disk-based indexes for billion-scale corpora",
            "Periodic compaction and re-indexing for freshness",
        ],
        "best_practices": [
            "Choose HNSW for low latency, IVF/PQ for memory-constrained scale.",
            "Benchmark recall and p99 latency on your real data, not synthetic.",
            "Plan re-indexing strategy before you need it.",
            "Isolate tenants by namespace and enforce access control.",
        ],
        "pitfalls": [
            "Assuming exact search; ANN trades recall for speed.",
            "Post-filtering that silently drops recall on selective queries.",
            "Underestimating memory for in-RAM HNSW at scale.",
            "No plan for embedding-model upgrades and re-indexing.",
        ],
        "use_cases": [
            ("Knowledge", "Powering RAG over millions of enterprise documents."),
            ("Media", "Visual similarity search across large catalogues."),
            ("Security", "Anomaly and similarity detection on event embeddings."),
            ("Recommendations", "Real-time candidate generation from user vectors."),
        ],
        "tools": ["Pinecone", "Weaviate", "Qdrant", "Milvus", "pgvector", "FAISS"],
        "glossary": [
            ("HNSW", "Hierarchical navigable small-world graph index."),
            ("IVF", "Inverted file index partitioning vectors into clusters."),
            ("PQ", "Product quantisation compressing vectors for memory."),
            ("Recall@k", "Fraction of true neighbours found in top-k results."),
        ],
        "references": [
            "Malkov & Yashunin — HNSW (2016)",
            "Johnson et al. — Billion-scale similarity search with GPUs / FAISS (2017)",
            "Khattab & Zaharia — ColBERT (2020)",
        ],
    },
    {
        "name": "RAG",
        "tagline": "Retrieval-augmented generation for grounded, current answers",
        "language": "python",
        "overview": (
            "Retrieval-augmented generation grounds a language model in external knowledge by "
            "retrieving relevant context at query time and conditioning generation on it. RAG "
            "reduces hallucination, enables citation, keeps answers current and lets "
            "organisations leverage proprietary data without retraining. This book covers the "
            "full RAG lifecycle: ingestion and chunking, retrieval and re-ranking, prompt "
            "assembly, evaluation and production operations."
        ),
        "concepts": [
            ("Why RAG: Grounding and Freshness",
             "The limits of parametric knowledge and the case for retrieval."),
            ("Document Ingestion and Chunking",
             "Parsing, semantic chunking, overlap and metadata extraction."),
            ("Embedding and Indexing Strategy",
             "Choosing models, dimensions and index types for the corpus."),
            ("Retrieval and Query Transformation",
             "Query rewriting, HyDE, multi-query and hybrid search."),
            ("Re-ranking and Context Selection",
             "Cross-encoders, maximal marginal relevance and context budgeting."),
            ("Prompt Assembly and Citation",
             "Grounding instructions, source attribution and refusal on low confidence."),
            ("Advanced RAG Patterns",
             "Parent-document, sentence-window, fusion and agentic retrieval."),
            ("Evaluation of RAG Systems",
             "Faithfulness, answer relevance, context precision/recall (RAGAS-style)."),
            ("Handling Tables, Images and Code",
             "Multimodal and structured-content retrieval."),
            ("Caching and Cost Optimisation",
             "Semantic caching and retrieval reuse."),
            ("Security and Access Control in RAG",
             "Row-level permissions and preventing data leakage across tenants."),
            ("Operating RAG in Production",
             "Monitoring retrieval quality, drift and feedback loops."),
            ("Failure Modes and Debugging",
             "Diagnosing retrieval versus generation failures."),
            ("The End-to-End RAG Reference Architecture",
             "A production blueprint from ingestion to answer."),
        ],
        "architecture": (
            "A RAG system has an offline ingestion pipeline (parse → chunk → embed → index) "
            "and an online query pipeline (query transform → hybrid retrieve → re-rank → "
            "assemble prompt → generate → cite). Access control filters retrieval by user "
            "permissions, and an evaluation service continuously scores faithfulness and "
            "relevance on sampled traffic."
        ),
        "patterns": [
            "Parent-document retrieval for precise chunks with broad context",
            "Hybrid retrieval with reciprocal rank fusion",
            "Cross-encoder re-ranking of top-k candidates",
            "Refuse-or-clarify when retrieval confidence is low",
        ],
        "best_practices": [
            "Tune chunking to the corpus; measure its effect on retrieval metrics.",
            "Always cite sources and enable users to verify answers.",
            "Enforce access control at retrieval time, not just at the UI.",
            "Evaluate retrieval and generation separately to localise failures.",
        ],
        "pitfalls": [
            "Naive fixed-size chunking that splits semantic units.",
            "Stuffing too much context, increasing cost and diluting relevance.",
            "Ignoring permissions and leaking restricted documents.",
            "Measuring only end answer quality without diagnosing retrieval.",
        ],
        "use_cases": [
            ("Enterprise", "Grounded internal Q&A over policies and wikis with citations."),
            ("Legal", "Case and contract research with traceable sources."),
            ("Healthcare", "Clinical guideline assistants with provenance."),
            ("Support", "Deflection bots grounded in current knowledge bases."),
        ],
        "tools": ["LangChain", "LlamaIndex", "Haystack", "RAGAS", "Cohere Rerank"],
        "glossary": [
            ("Chunking", "Splitting documents into retrievable passages."),
            ("Re-ranking", "Reordering retrieved passages by relevance."),
            ("Faithfulness", "Whether an answer is supported by retrieved context."),
            ("HyDE", "Hypothetical document embeddings for query expansion."),
        ],
        "references": [
            "Lewis et al. — Retrieval-Augmented Generation (2020)",
            "Gao et al. — Precise Zero-Shot Dense Retrieval (HyDE, 2022)",
            "Es et al. — RAGAS (2023)",
        ],
    },
    {
        "name": "GraphRAG",
        "tagline": "Knowledge-graph-grounded retrieval for global reasoning",
        "language": "python",
        "overview": (
            "GraphRAG augments retrieval-augmented generation with a knowledge graph "
            "constructed from a corpus, enabling multi-hop reasoning, community summarisation "
            "and global questions that flat vector retrieval cannot answer. By extracting "
            "entities and relationships and clustering them into hierarchical communities, "
            "GraphRAG supports both local (entity-centric) and global (theme-level) queries "
            "with traceable structure."
        ),
        "concepts": [
            ("Limits of Vector-Only RAG",
             "Why local similarity fails on global, multi-hop and aggregative questions."),
            ("Knowledge Graph Construction from Text",
             "LLM-driven entity and relationship extraction and schema design."),
            ("Entity Resolution and Deduplication",
             "Merging coreferent entities into a clean graph."),
            ("Community Detection and Summarisation",
             "Hierarchical clustering (e.g. Leiden) and map-reduce summaries."),
            ("Local versus Global Search",
             "Entity-centric retrieval versus community-level synthesis."),
            ("Graph + Vector Hybrid Retrieval",
             "Combining structural traversal with semantic similarity."),
            ("Query Routing in GraphRAG",
             "Choosing local, global or hybrid strategies per question."),
            ("Multi-Hop Reasoning over Graphs",
             "Traversing relationships to answer connected questions."),
            ("Evaluation of GraphRAG",
             "Comprehensiveness, diversity and groundedness metrics."),
            ("Cost and Indexing Trade-offs",
             "The build cost of graph extraction versus query-time value."),
            ("Incremental Graph Updates",
             "Keeping the graph fresh as the corpus changes."),
            ("Operating GraphRAG",
             "Pipelines, storage and monitoring."),
            ("Security and Provenance",
             "Source attribution through graph edges."),
            ("The GraphRAG Reference Architecture",
             "Indexing and query pipelines end to end."),
        ],
        "architecture": (
            "GraphRAG indexing extracts entities and relations from chunks, resolves "
            "duplicates, builds a graph, detects communities and pre-summarises them. At "
            "query time a router selects local search (entity neighbourhoods + linked text) "
            "or global search (map-reduce over community summaries), then synthesises a cited "
            "answer."
        ),
        "patterns": [
            "Map-reduce community summarisation for global questions",
            "Entity-neighbourhood expansion for local questions",
            "Hybrid graph traversal + vector similarity",
            "Hierarchical community summaries for scalable synthesis",
        ],
        "best_practices": [
            "Invest in entity resolution; graph quality dominates answer quality.",
            "Route global questions to community summaries, not raw chunks.",
            "Cache community summaries to amortise extraction cost.",
            "Track provenance through edges for citation.",
        ],
        "pitfalls": [
            "Skipping entity resolution and fragmenting the graph.",
            "Applying GraphRAG where simple RAG suffices, inflating cost.",
            "Stale graphs after corpus updates.",
            "Unbounded extraction cost on huge corpora.",
        ],
        "use_cases": [
            ("Research", "Literature synthesis across thousands of papers."),
            ("Intelligence", "Connecting entities across heterogeneous reports."),
            ("Enterprise", "Whole-corpus thematic questions over documentation."),
            ("Compliance", "Tracing relationships across regulatory filings."),
        ],
        "tools": ["Microsoft GraphRAG", "Neo4j", "LlamaIndex", "NetworkX", "Leiden"],
        "glossary": [
            ("Community", "A densely connected cluster of graph nodes."),
            ("Local search", "Entity-centric retrieval over a neighbourhood."),
            ("Global search", "Theme-level synthesis over community summaries."),
            ("Entity resolution", "Merging references to the same real entity."),
        ],
        "references": [
            "Edge et al. — From Local to Global: Graph RAG (Microsoft, 2024)",
            "Traag et al. — Leiden community detection (2019)",
        ],
    },
    {
        "name": "Knowledge Graphs",
        "tagline": "Modelling, storing and reasoning over connected data",
        "language": "python",
        "overview": (
            "Knowledge graphs represent entities and their relationships as nodes and edges, "
            "enabling integration of heterogeneous data, semantic querying and reasoning. "
            "They power search, recommendations, fraud detection and now ground LLM systems. "
            "This book covers ontology design, ingestion, graph databases, query languages, "
            "embeddings and the operational practices of enterprise knowledge graphs."
        ),
        "concepts": [
            ("Graphs, Triples and the Property Graph Model",
             "RDF triples versus labelled property graphs and when to use each."),
            ("Ontology and Schema Design",
             "Classes, properties, taxonomies and reusing standard vocabularies."),
            ("Entity Extraction and Linking",
             "Populating the graph from structured and unstructured sources."),
            ("Graph Query Languages",
             "Cypher, SPARQL and Gremlin for traversal and pattern matching."),
            ("Reasoning and Inference",
             "Rules, RDFS/OWL semantics and inferring implicit facts."),
            ("Knowledge Graph Embeddings",
             "TransE, RotatE and link prediction for completion."),
            ("Graph Algorithms for Insight",
             "Centrality, community detection and pathfinding."),
            ("Data Quality and Entity Resolution",
             "Deduplication, validation and provenance."),
            ("Scaling Graph Storage",
             "Partitioning, indexing and distributed graph engines."),
            ("Graphs for Grounding LLMs",
             "Serving structured context to generative systems."),
            ("Governance and Lineage",
             "Versioning, access control and auditability."),
            ("Operating Knowledge Graphs",
             "Pipelines, monitoring and lifecycle management."),
            ("Visualising Knowledge Graphs",
             "Effective exploration and analyst tooling."),
            ("The Enterprise Knowledge Graph Architecture",
             "Reference blueprint integrating sources, store and consumers."),
        ],
        "architecture": (
            "An enterprise knowledge graph ingests from databases, documents and APIs through "
            "extraction and entity-resolution pipelines into a graph store governed by an "
            "ontology. Query services expose traversal and reasoning to applications, while a "
            "governance layer tracks provenance, versions and access."
        ),
        "patterns": [
            "Canonical ontology with reused standard vocabularies",
            "Entity-resolution pipeline feeding a golden-record graph",
            "Embedding-based link prediction for completion",
            "Provenance edges for full traceability",
        ],
        "best_practices": [
            "Design the ontology with domain experts before ingesting at scale.",
            "Treat entity resolution as a first-class, monitored pipeline.",
            "Record provenance on every fact for trust and debugging.",
            "Choose the model (RDF vs property graph) to fit query needs.",
        ],
        "pitfalls": [
            "Over-engineering the ontology before validating use cases.",
            "Neglecting entity resolution and creating duplicates.",
            "Ignoring provenance, making facts untrustworthy.",
            "Picking a graph engine that cannot scale to your traversal patterns.",
        ],
        "use_cases": [
            ("Finance", "Fraud rings and beneficial-ownership analysis."),
            ("Healthcare", "Integrating clinical, genomic and literature data."),
            ("Retail", "Product knowledge graphs powering search and recommendations."),
            ("Enterprise", "360-degree views linking customers, products and events."),
        ],
        "tools": ["Neo4j", "Amazon Neptune", "RDFLib", "Apache Jena", "GraphDB"],
        "glossary": [
            ("Triple", "Subject–predicate–object statement of fact."),
            ("Ontology", "A formal model of concepts and relationships."),
            ("SPARQL", "Query language for RDF graphs."),
            ("Link prediction", "Inferring missing edges in a graph."),
        ],
        "references": [
            "Hogan et al. — Knowledge Graphs (2021)",
            "Bordes et al. — TransE (2013)",
        ],
    },
    {
        "name": "Agentic AI",
        "tagline": "Autonomous systems that plan, act and use tools",
        "language": "python",
        "overview": (
            "Agentic AI systems use language models as reasoning engines that plan, invoke "
            "tools, observe results and iterate toward goals with limited human oversight. "
            "Unlike single-shot prompting, agents maintain state, decompose tasks and act on "
            "the world. This book covers agent architectures, planning, memory, tool use, "
            "safety and the operational discipline required to deploy autonomous systems "
            "responsibly."
        ),
        "concepts": [
            ("From Chatbots to Agents",
             "The shift from single responses to goal-directed loops."),
            ("The Agent Loop: Reason, Act, Observe",
             "ReAct-style cycles and the perception–action interface."),
            ("Planning and Task Decomposition",
             "Plan-and-execute, tree-of-thought and hierarchical planning."),
            ("Tool Use and Function Calling",
             "Defining, selecting and safely invoking tools and APIs."),
            ("Memory Architectures",
             "Short-term context, long-term vector memory and episodic recall."),
            ("Reflection and Self-Correction",
             "Critique loops, verification and error recovery."),
            ("Grounding and Retrieval for Agents",
             "Bringing knowledge into the agent loop."),
            ("Human-in-the-Loop and Approvals",
             "Confirmation gates for high-impact actions."),
            ("Safety, Sandboxing and Permissions",
             "Constraining what agents can do and access."),
            ("Cost, Latency and Loop Control",
             "Budgeting steps, preventing runaway loops and caching."),
            ("Evaluating Agents",
             "Task success, trajectory quality and robustness benchmarks."),
            ("Agent Frameworks and Patterns",
             "Comparing frameworks and reusable design patterns."),
            ("Observability for Agents",
             "Tracing reasoning, tool calls and outcomes."),
            ("The Agentic Reference Architecture",
             "Orchestrator, tools, memory and guardrails as a platform."),
        ],
        "architecture": (
            "An agent runtime hosts a reasoning model, a tool registry with typed schemas, a "
            "memory store (short-term context plus long-term vector memory), and a controller "
            "enforcing step budgets, permissions and human approvals. Every step is traced "
            "for observability and replay."
        ),
        "patterns": [
            "ReAct: interleave reasoning and tool actions",
            "Plan-and-execute with a separate planner and executor",
            "Reflection loop to critique and revise outputs",
            "Approval gate before irreversible actions",
        ],
        "best_practices": [
            "Constrain tools with typed schemas and least-privilege permissions.",
            "Cap loop steps and cost to prevent runaway behaviour.",
            "Require human approval for irreversible or high-impact actions.",
            "Trace every reasoning step and tool call for debugging and audit.",
        ],
        "pitfalls": [
            "Unbounded loops that burn cost without converging.",
            "Granting broad tool permissions that enable harmful actions.",
            "No observability, making failures impossible to diagnose.",
            "Over-automating tasks that need human judgement.",
        ],
        "use_cases": [
            ("Software", "Autonomous coding agents that plan, edit and test."),
            ("Operations", "Incident triage agents that gather context and act."),
            ("Research", "Agents that browse, synthesise and report."),
            ("Back office", "Workflow automation across enterprise systems."),
        ],
        "tools": ["LangGraph", "AutoGen", "CrewAI", "OpenAI Agents", "Claude tools"],
        "glossary": [
            ("Agent", "An LLM-driven system that plans and acts toward goals."),
            ("ReAct", "Reasoning and acting interleaved in a loop."),
            ("Tool", "An external function or API an agent can call."),
            ("Reflection", "Self-critique to improve outputs."),
        ],
        "references": [
            "Yao et al. — ReAct (2022)",
            "Shinn et al. — Reflexion (2023)",
            "Wang et al. — A Survey on LLM-based Agents (2023)",
        ],
    },
    {
        "name": "Multi-Agent Systems",
        "tagline": "Coordinating teams of specialised AI agents",
        "language": "python",
        "overview": (
            "Multi-agent systems decompose complex goals across specialised agents that "
            "communicate, coordinate and sometimes debate to produce better outcomes than a "
            "single agent. They introduce challenges of orchestration, communication "
            "protocols, conflict resolution and emergent behaviour. This book covers "
            "topologies, coordination patterns, shared memory, evaluation and the operational "
            "risks of multi-agent autonomy."
        ),
        "concepts": [
            ("Why Multiple Agents",
             "Specialisation, parallelism and separation of concerns."),
            ("Agent Roles and Topologies",
             "Hierarchical, sequential, network and market-based organisations."),
            ("Communication Protocols",
             "Message passing, shared blackboards and structured handoffs."),
            ("Orchestration and Routing",
             "Supervisors, routers and dynamic task allocation."),
            ("Shared Memory and State",
             "Coordinating context across agents safely."),
            ("Debate and Consensus",
             "Multi-agent debate, voting and critique for quality."),
            ("Conflict Resolution",
             "Handling disagreement and contradictory actions."),
            ("Tool and Resource Contention",
             "Coordinating access to shared external systems."),
            ("Emergent Behaviour and Risk",
             "Unintended dynamics and how to contain them."),
            ("Evaluating Multi-Agent Systems",
             "End-to-end task success and per-agent contribution."),
            ("Cost Control at Team Scale",
             "Budgeting across many concurrent agents."),
            ("Frameworks and Patterns",
             "Comparing orchestration frameworks."),
            ("Observability Across Agents",
             "Tracing distributed agent interactions."),
            ("The Multi-Agent Reference Architecture",
             "Supervisor, workers, shared memory and guardrails."),
        ],
        "architecture": (
            "A multi-agent platform uses a supervisor/orchestrator that routes subtasks to "
            "specialised worker agents, a shared state store for coordination, a message bus "
            "for structured communication, and global guardrails enforcing budgets and "
            "permissions. Distributed tracing stitches together cross-agent trajectories."
        ),
        "patterns": [
            "Supervisor–worker hierarchy",
            "Sequential pipeline of specialised agents",
            "Debate-and-judge for high-stakes decisions",
            "Blackboard for shared coordination state",
        ],
        "best_practices": [
            "Give each agent a narrow, well-specified role.",
            "Use structured messages and explicit handoff contracts.",
            "Enforce global budgets to prevent multiplicative cost blow-ups.",
            "Trace cross-agent interactions for debugging.",
        ],
        "pitfalls": [
            "Agents talking in circles without convergence.",
            "Combinatorial cost growth across many agents.",
            "Unclear ownership leading to duplicated or conflicting actions.",
            "Emergent failures that are hard to reproduce.",
        ],
        "use_cases": [
            ("Software", "Planner, coder, reviewer and tester agents collaborating."),
            ("Research", "Specialised retrieval, analysis and writing agents."),
            ("Operations", "Coordinated agents across monitoring and remediation."),
            ("Simulation", "Agent-based modelling of markets and organisations."),
        ],
        "tools": ["AutoGen", "CrewAI", "LangGraph", "MetaGPT"],
        "glossary": [
            ("Supervisor", "An agent that routes work to others."),
            ("Blackboard", "Shared memory for agent coordination."),
            ("Topology", "The communication structure among agents."),
            ("Debate", "Agents arguing to improve answer quality."),
        ],
        "references": [
            "Wu et al. — AutoGen (2023)",
            "Du et al. — Improving Factuality via Multi-Agent Debate (2023)",
        ],
    },
    {
        "name": "MCP",
        "tagline": "The Model Context Protocol for tool and data integration",
        "language": "typescript",
        "overview": (
            "The Model Context Protocol (MCP) is an open standard that connects AI "
            "applications to external tools, data sources and prompts through a uniform "
            "client–server interface. By standardising how models access context, MCP "
            "replaces bespoke integrations with reusable servers, improving security, "
            "portability and governance. This book covers the protocol, server and client "
            "implementation, transports, security and enterprise deployment."
        ),
        "concepts": [
            ("The Integration Problem MCP Solves",
             "Fragmented, bespoke tool integrations versus a shared protocol."),
            ("MCP Architecture: Hosts, Clients and Servers",
             "Roles and responsibilities in the protocol."),
            ("Primitives: Tools, Resources and Prompts",
             "The three capabilities MCP servers expose."),
            ("Transports: stdio and Streamable HTTP",
             "Local and remote communication mechanisms."),
            ("Building an MCP Server",
             "Implementing tools, resources and prompts with the SDK."),
            ("Building an MCP Client/Host",
             "Discovering and invoking server capabilities."),
            ("Capability Negotiation and Schemas",
             "Typed inputs/outputs and discovery."),
            ("Security and Authorisation",
             "OAuth, consent, sandboxing and least privilege."),
            ("Sampling and Elicitation",
             "Servers requesting model completions and user input."),
            ("Enterprise Deployment of MCP",
             "Registries, governance and centralised management."),
            ("Observability and Auditing",
             "Logging tool calls for compliance."),
            ("MCP and Agent Frameworks",
             "Using MCP servers as the tool layer for agents."),
            ("Testing and Versioning MCP Servers",
             "Contract testing and compatibility."),
            ("Reference Architecture and Patterns",
             "A governed enterprise MCP deployment."),
        ],
        "architecture": (
            "An MCP host (e.g. an IDE or assistant) runs MCP clients that connect to MCP "
            "servers exposing tools, resources and prompts over stdio or Streamable HTTP. An "
            "enterprise deployment adds a server registry, OAuth-based authorisation, a "
            "policy/consent layer and centralised audit logging of all tool invocations."
        ),
        "patterns": [
            "One server per capability domain (files, db, tickets)",
            "OAuth-protected remote servers with scoped consent",
            "Server registry for discovery and governance",
            "Audit log of every tool invocation",
        ],
        "best_practices": [
            "Expose least-privilege tools with strict input schemas.",
            "Require explicit user consent for sensitive actions.",
            "Centralise auditing of all MCP tool calls.",
            "Version server contracts and test compatibility.",
        ],
        "pitfalls": [
            "Over-broad tools that expose dangerous capabilities.",
            "Skipping authorisation on remote servers.",
            "No audit trail for tool invocations.",
            "Breaking schema changes without versioning.",
        ],
        "use_cases": [
            ("Developer Tools", "IDEs accessing repos, docs and build systems uniformly."),
            ("Enterprise", "Governed access to internal databases and ticketing."),
            ("Assistants", "Connecting LLM apps to live business data."),
            ("Automation", "Reusable tool servers across many agents."),
        ],
        "tools": ["MCP TypeScript SDK", "MCP Python SDK", "Claude Desktop", "Cursor"],
        "glossary": [
            ("MCP server", "A process exposing tools, resources and prompts."),
            ("Resource", "Read-only context a server provides."),
            ("Tool", "An action a server lets the model invoke."),
            ("Transport", "The channel (stdio/HTTP) for MCP messages."),
        ],
        "references": [
            "Anthropic — Model Context Protocol Specification",
            "modelcontextprotocol.io — Documentation and SDKs",
        ],
    },
    {
        "name": "Cursor IDE",
        "tagline": "AI-native software development with Cursor",
        "language": "typescript",
        "overview": (
            "Cursor is an AI-native code editor that integrates large language models "
            "directly into the development workflow through inline completion, chat, "
            "codebase-aware retrieval and autonomous agents. It changes how engineers write, "
            "review and refactor code. This book covers effective use of Cursor's features, "
            "rules and context management, agent workflows, MCP integration and team-scale "
            "adoption with governance."
        ),
        "concepts": [
            ("The AI-Native IDE Paradigm",
             "How embedding LLMs in the editor changes the development loop."),
            ("Inline Completion and Tab",
             "Predictive multi-line edits and accept/reject workflows."),
            ("Chat and Codebase-Aware Context",
             "Asking questions grounded in the repository."),
            ("Agent Mode and Autonomous Edits",
             "Delegating multi-file tasks to the agent."),
            ("Context Management with @ References",
             "Pointing the model at files, symbols and docs."),
            ("Rules and Project Conventions",
             "Encoding standards so AI output matches your codebase."),
            ("MCP Integration in Cursor",
             "Connecting external tools and data to the editor."),
            ("Reviewing and Verifying AI Changes",
             "Diff review, testing and trust calibration."),
            ("Refactoring and Migration Workflows",
             "Large-scale, AI-assisted code transformations."),
            ("Debugging with AI Assistance",
             "Explaining errors and proposing fixes."),
            ("Prompting Patterns for Code",
             "Effective instructions for reliable code generation."),
            ("Team Adoption and Governance",
             "Standards, privacy and rollout across an org."),
            ("Productivity Measurement",
             "Evaluating impact without gaming metrics."),
            ("An Effective Cursor Workflow",
             "A reference end-to-end development loop."),
        ],
        "architecture": (
            "Cursor combines a local editor with a context engine that retrieves relevant "
            "code, a model layer (completion and chat/agent models), and integrations such as "
            "MCP servers and the terminal. Project rules and @-references shape the context "
            "assembled for each request, and an agent loop can plan and apply multi-file "
            "edits with review."
        ),
        "patterns": [
            "Rules files to encode conventions for consistent output",
            "@-reference context selection for precise grounding",
            "Agent for scoped multi-file tasks, review every diff",
            "MCP servers to bring external data into the editor",
        ],
        "best_practices": [
            "Write clear rules so generated code matches your standards.",
            "Scope agent tasks narrowly and review all diffs and tests.",
            "Provide precise context via @-references instead of vague prompts.",
            "Keep secrets out of context and configure privacy settings.",
        ],
        "pitfalls": [
            "Accepting large AI changes without review or tests.",
            "Vague prompts producing plausible but wrong edits.",
            "Leaking secrets into model context.",
            "Over-reliance that erodes code understanding.",
        ],
        "use_cases": [
            ("Engineering", "Feature development with AI pair programming."),
            ("Maintenance", "Large refactors and dependency migrations."),
            ("Onboarding", "Explaining unfamiliar codebases to new hires."),
            ("Platform", "Standardising AI workflows across teams."),
        ],
        "tools": ["Cursor", "MCP", "Git", "Language servers"],
        "glossary": [
            ("Agent mode", "Autonomous multi-step editing in Cursor."),
            ("Rules", "Project conventions that guide AI output."),
            ("@-reference", "A way to attach specific context to a prompt."),
            ("Tab", "Inline predictive code completion."),
        ],
        "references": [
            "Cursor Documentation — docs.cursor.com",
            "Anthropic & OpenAI — model documentation",
        ],
    },
    {
        "name": "Claude",
        "tagline": "Building with Anthropic's Claude models",
        "language": "python",
        "overview": (
            "Claude is Anthropic's family of large language models designed with a focus on "
            "helpfulness, honesty and harmlessness, trained using Constitutional AI. Claude "
            "excels at long-context reasoning, tool use, coding and structured output. This "
            "book covers the Claude API, prompting best practices, tool use, the Messages "
            "format, vision, long-context strategies and production deployment patterns."
        ),
        "concepts": [
            ("The Claude Model Family",
             "Capability tiers and choosing the right model for cost/quality."),
            ("The Messages API",
             "Roles, system prompts and conversation structure."),
            ("Prompting Claude Effectively",
             "XML tags, explicitness and Claude-specific best practices."),
            ("Tool Use with Claude",
             "Defining tools, the tool-use loop and structured results."),
            ("Long-Context Strategies",
             "Leveraging large context windows and prompt caching."),
            ("Vision and Multimodal Inputs",
             "Reasoning over images and documents."),
            ("Structured Output and JSON",
             "Reliable schema-conformant responses."),
            ("Constitutional AI and Safety",
             "How Claude is aligned and how to work with its guardrails."),
            ("Streaming and Latency",
             "Streaming responses and optimising perceived speed."),
            ("Prompt Caching and Cost",
             "Reducing cost on repeated context."),
            ("Agents and Computer Use",
             "Building autonomous workflows with Claude."),
            ("Evaluation and Iteration",
             "Testing prompts and measuring quality."),
            ("Production Deployment",
             "Reliability, retries and error handling."),
            ("Reference Patterns with Claude",
             "End-to-end application blueprints."),
        ],
        "architecture": (
            "A Claude-based application calls the Messages API through a gateway that manages "
            "auth, retries, streaming and prompt caching. Tool use runs a loop where Claude "
            "requests a tool, the application executes it and returns results, and Claude "
            "synthesises a final answer. Observability captures tokens, latency and cost."
        ),
        "patterns": [
            "XML-tagged prompts for clarity and parsing",
            "Tool-use loop with typed tool definitions",
            "Prompt caching for large static context",
            "Streaming for responsive UX",
        ],
        "best_practices": [
            "Use XML tags to structure instructions and inputs for Claude.",
            "Be explicit about desired format and reasoning.",
            "Cache large stable context to cut cost and latency.",
            "Handle the tool-use loop and errors robustly.",
        ],
        "pitfalls": [
            "Vague prompts that under-specify the task.",
            "Ignoring prompt caching and overpaying for repeated context.",
            "Not handling tool-use turns correctly.",
            "Skipping retries and rate-limit handling.",
        ],
        "use_cases": [
            ("Software", "Coding assistants and autonomous engineering agents."),
            ("Knowledge", "Long-document analysis and grounded Q&A."),
            ("Customer", "Safe, helpful support assistants."),
            ("Analysis", "Structured extraction from complex documents."),
        ],
        "tools": ["Anthropic SDK", "Claude API", "MCP", "AWS Bedrock", "Google Vertex"],
        "glossary": [
            ("Messages API", "Claude's conversation interface."),
            ("Constitutional AI", "Alignment via a set of guiding principles."),
            ("Prompt caching", "Reusing processed context to save cost."),
            ("Tool use", "Letting Claude call external functions."),
        ],
        "references": [
            "Anthropic — Claude Documentation",
            "Bai et al. — Constitutional AI (2022)",
        ],
    },
    {
        "name": "OpenAI",
        "tagline": "Building with the OpenAI platform",
        "language": "python",
        "overview": (
            "OpenAI provides a comprehensive platform of foundation models and APIs for text, "
            "vision, audio, embeddings and image generation, along with tools for function "
            "calling, structured output and agents. This book covers the API surface, "
            "prompting, function calling, structured outputs, embeddings, the Assistants/"
            "Responses paradigm, fine-tuning and production best practices."
        ),
        "concepts": [
            ("The OpenAI Platform Overview",
             "Models, modalities and choosing the right endpoint."),
            ("Chat Completions and the Responses API",
             "Core text-generation interfaces and their evolution."),
            ("Function Calling and Tools",
             "Letting models call functions and use built-in tools."),
            ("Structured Outputs",
             "JSON schema enforcement for reliable integration."),
            ("Embeddings and Retrieval",
             "Using OpenAI embeddings for search and RAG."),
            ("Vision and Audio",
             "Multimodal inputs, speech-to-text and text-to-speech."),
            ("Image Generation",
             "Creating and editing images programmatically."),
            ("Fine-Tuning OpenAI Models",
             "When and how to fine-tune for style and accuracy."),
            ("Assistants and Agents",
             "Stateful, tool-using application patterns."),
            ("Batch, Streaming and Cost Control",
             "Throughput and token economics."),
            ("Safety, Moderation and Policy",
             "Content moderation and usage policies."),
            ("Reliability and Error Handling",
             "Retries, rate limits and idempotency."),
            ("Evaluation and Iteration",
             "Testing prompts and model upgrades."),
            ("Reference Application Patterns",
             "End-to-end blueprints on the platform."),
        ],
        "architecture": (
            "An OpenAI-based system routes requests through a gateway handling auth, retries "
            "and rate limits, uses function calling for tool integration and structured "
            "outputs for reliable parsing, and stores embeddings in a vector index for RAG. "
            "Telemetry tracks tokens, latency and cost across endpoints."
        ),
        "patterns": [
            "Function calling for tool integration",
            "Structured outputs with JSON schema",
            "Embeddings + vector store for retrieval",
            "Streaming responses for UX",
        ],
        "best_practices": [
            "Use structured outputs to guarantee parseable responses.",
            "Implement retries with backoff and idempotency keys.",
            "Right-size models per task to control cost.",
            "Add moderation on user-generated content.",
        ],
        "pitfalls": [
            "Parsing free-form text instead of using structured outputs.",
            "No rate-limit handling under load.",
            "Overusing the largest model unnecessarily.",
            "Skipping moderation in user-facing apps.",
        ],
        "use_cases": [
            ("Productivity", "Assistants, summarisation and drafting."),
            ("Search", "Semantic search and RAG with embeddings."),
            ("Media", "Image and audio generation pipelines."),
            ("Automation", "Tool-using agents over business systems."),
        ],
        "tools": ["OpenAI Python SDK", "OpenAI Node SDK", "Azure OpenAI"],
        "glossary": [
            ("Function calling", "Models returning structured tool calls."),
            ("Structured output", "Schema-enforced JSON responses."),
            ("Responses API", "OpenAI's unified generation interface."),
            ("Moderation", "Classifying content against policy."),
        ],
        "references": [
            "OpenAI — Platform Documentation",
            "OpenAI — Function Calling and Structured Outputs guides",
        ],
    },
    {
        "name": "Gemini",
        "tagline": "Building with Google's Gemini models",
        "language": "python",
        "overview": (
            "Gemini is Google's family of natively multimodal foundation models supporting "
            "text, images, audio, video and code with very long context windows. Available "
            "through the Gemini API and Vertex AI, Gemini supports function calling, grounding "
            "with Google Search and structured output. This book covers the API, multimodal "
            "prompting, long-context use, grounding, function calling and enterprise "
            "deployment on Vertex AI."
        ),
        "concepts": [
            ("The Gemini Model Family",
             "Capability tiers and native multimodality."),
            ("Gemini API and Vertex AI",
             "Consumer and enterprise access paths."),
            ("Multimodal Prompting",
             "Combining text, image, audio and video inputs."),
            ("Very Long Context",
             "Reasoning over large documents and media."),
            ("Function Calling and Tools",
             "Tool integration and structured actions."),
            ("Grounding with Google Search",
             "Reducing hallucination with live grounding."),
            ("Structured Output",
             "Schema-constrained responses."),
            ("Code and Reasoning",
             "Programming and analytical tasks."),
            ("Safety Settings and Filters",
             "Configuring content safety."),
            ("Embeddings and Retrieval",
             "Gemini embeddings for search and RAG."),
            ("Cost, Quotas and Latency",
             "Operating efficiently."),
            ("Vertex AI MLOps Integration",
             "Deploying within Google Cloud."),
            ("Evaluation and Iteration",
             "Testing and improving prompts."),
            ("Reference Patterns with Gemini",
             "End-to-end application blueprints."),
        ],
        "architecture": (
            "A Gemini application accesses models via the Gemini API or Vertex AI, supplies "
            "multimodal inputs, optionally grounds responses with Google Search, and uses "
            "function calling for tools. On Vertex AI it integrates with managed MLOps, IAM "
            "and monitoring for enterprise governance."
        ),
        "patterns": [
            "Native multimodal prompts (text + media)",
            "Search grounding for factuality",
            "Function calling for tool use",
            "Vertex AI deployment for enterprise governance",
        ],
        "best_practices": [
            "Exploit long context but manage cost on large inputs.",
            "Enable grounding for fact-sensitive tasks.",
            "Configure safety settings to your policy.",
            "Use Vertex AI for enterprise IAM and monitoring.",
        ],
        "pitfalls": [
            "Sending huge contexts without cost awareness.",
            "Ignoring grounding for factual queries.",
            "Misconfigured safety filters blocking valid use.",
            "Skipping Vertex governance in regulated settings.",
        ],
        "use_cases": [
            ("Media", "Video and audio understanding at scale."),
            ("Documents", "Long-document and multimodal analysis."),
            ("Search", "Grounded answers with citations."),
            ("Enterprise", "Governed deployment on Google Cloud."),
        ],
        "tools": ["google-genai SDK", "Vertex AI", "Google Cloud"],
        "glossary": [
            ("Multimodal", "Handling multiple input types natively."),
            ("Grounding", "Anchoring answers in retrieved/search results."),
            ("Vertex AI", "Google Cloud's managed ML platform."),
            ("Long context", "Very large input windows."),
        ],
        "references": [
            "Google — Gemini API Documentation",
            "Google Cloud — Vertex AI Documentation",
        ],
    },
    {
        "name": "Anthropic",
        "tagline": "Anthropic's research, safety approach and platform",
        "language": "python",
        "overview": (
            "Anthropic is an AI safety company building Claude and pioneering techniques such "
            "as Constitutional AI, interpretability research and responsible scaling "
            "policies. Understanding Anthropic's approach informs how to build safely with "
            "frontier models. This book covers Anthropic's research directions, the Claude "
            "platform, safety methodology, the Model Context Protocol and enterprise "
            "deployment through cloud partners."
        ),
        "concepts": [
            ("Anthropic's Mission and Safety Philosophy",
             "AI safety as a core engineering and research discipline."),
            ("Constitutional AI",
             "Aligning models with a set of principles rather than only human labels."),
            ("Responsible Scaling Policy",
             "Capability thresholds and safety commitments."),
            ("Mechanistic Interpretability",
             "Understanding model internals and features."),
            ("The Claude Platform",
             "Models, API and capabilities overview."),
            ("Tool Use and Agents",
             "Building autonomous workflows safely."),
            ("The Model Context Protocol",
             "Anthropic's open standard for tool/data integration."),
            ("Prompt Engineering for Claude",
             "Anthropic's recommended practices."),
            ("Enterprise Deployment",
             "Bedrock, Vertex and direct API."),
            ("Red-Teaming and Evaluation",
             "Stress-testing models for safety."),
            ("Usage Policies and Governance",
             "Responsible deployment requirements."),
            ("Research-Informed Engineering",
             "Applying safety research to products."),
            ("Long-Context and Caching",
             "Operating efficiently with Claude."),
            ("Reference Architectures",
             "Safe, governed Claude applications."),
        ],
        "architecture": (
            "Building with Anthropic combines the Claude platform (Messages API, tool use, "
            "prompt caching) with safety practices (red-teaming, usage policy enforcement) "
            "and MCP for governed tool integration. Enterprise deployments run via Bedrock or "
            "Vertex with full IAM, logging and audit."
        ),
        "patterns": [
            "Constitutional-style guardrails for output policy",
            "MCP for governed tool/data access",
            "Red-team evaluation before deployment",
            "Cloud-partner deployment for compliance",
        ],
        "best_practices": [
            "Adopt layered safety and red-team before launch.",
            "Use MCP for auditable tool integration.",
            "Follow usage policies and document risk assessments.",
            "Deploy via governed cloud partners for regulated workloads.",
        ],
        "pitfalls": [
            "Treating safety as a launch checkbox rather than a process.",
            "Unaudited tool access from autonomous agents.",
            "Ignoring usage-policy constraints.",
            "Skipping red-teaming on high-risk applications.",
        ],
        "use_cases": [
            ("Enterprise", "Safe, governed assistants and agents."),
            ("Regulated", "Compliant deployment in finance and healthcare."),
            ("Developer", "Coding agents via Claude and MCP."),
            ("Research", "Applying interpretability and safety insights."),
        ],
        "tools": ["Anthropic SDK", "MCP", "AWS Bedrock", "Google Vertex"],
        "glossary": [
            ("Constitutional AI", "Principle-based model alignment."),
            ("RSP", "Responsible Scaling Policy."),
            ("Interpretability", "Understanding model internals."),
            ("Red-teaming", "Adversarial testing for safety."),
        ],
        "references": [
            "Bai et al. — Constitutional AI (2022)",
            "Anthropic — Responsible Scaling Policy",
        ],
    },
    {
        "name": "Fine Tuning",
        "tagline": "Adapting foundation models to your domain",
        "language": "python",
        "overview": (
            "Fine-tuning adapts a pre-trained model to a specific task, domain or style by "
            "continuing training on curated data. It can improve accuracy, reduce prompt "
            "length and instil consistent behaviour, but it carries cost, data and "
            "maintenance burdens. This book covers when to fine-tune versus prompt or "
            "retrieve, data preparation, full and parameter-efficient methods, evaluation and "
            "production lifecycle management."
        ),
        "concepts": [
            ("When to Fine-Tune (and When Not To)",
             "Trade-offs versus prompting and retrieval."),
            ("Data Curation for Fine-Tuning",
             "Quality, formatting, deduplication and labelling."),
            ("Supervised Fine-Tuning",
             "Instruction and task-specific SFT."),
            ("Full Fine-Tuning versus Parameter-Efficient",
             "Cost, memory and quality trade-offs."),
            ("Catastrophic Forgetting",
             "Preserving general capability while specialising."),
            ("Hyper-parameters and Training Dynamics",
             "Learning rate, epochs and batch size."),
            ("Evaluation of Fine-Tuned Models",
             "Held-out tasks and regression suites."),
            ("Distillation",
             "Compressing capability into smaller models."),
            ("Domain Adaptation",
             "Continued pre-training on domain corpora."),
            ("Serving Fine-Tuned Models",
             "Adapters, merging and routing."),
            ("Cost and ROI Analysis",
             "Justifying the fine-tuning investment."),
            ("Lifecycle and Re-training",
             "Maintaining models as data evolves."),
            ("Governance and Provenance",
             "Tracking data and model lineage."),
            ("The Fine-Tuning Reference Pipeline",
             "End-to-end blueprint."),
        ],
        "architecture": (
            "A fine-tuning pipeline curates and validates data, runs SFT or PEFT on tracked "
            "infrastructure, evaluates against held-out and regression suites, registers the "
            "resulting artefact with provenance, and promotes it through champion/challenger "
            "evaluation into adapter-based serving."
        ),
        "patterns": [
            "Prompt → retrieve → fine-tune escalation ladder",
            "PEFT adapters for cheap, swappable specialisation",
            "Champion/challenger before promotion",
            "Regression suite to catch capability loss",
        ],
        "best_practices": [
            "Exhaust prompting and retrieval before fine-tuning.",
            "Invest disproportionately in data quality.",
            "Always evaluate for catastrophic forgetting.",
            "Track data and model provenance for governance.",
        ],
        "pitfalls": [
            "Fine-tuning to fix problems better solved by retrieval.",
            "Small, noisy datasets that overfit.",
            "Forgetting general capability after narrow tuning.",
            "No re-training plan as the domain drifts.",
        ],
        "use_cases": [
            ("Enterprise", "Consistent brand voice and structured outputs."),
            ("Healthcare", "Domain-specialised clinical language tasks."),
            ("Legal", "Jurisdiction-specific drafting and extraction."),
            ("Support", "Task-specific classification and routing."),
        ],
        "tools": ["Hugging Face PEFT", "TRL", "Axolotl", "OpenAI fine-tuning"],
        "glossary": [
            ("SFT", "Supervised fine-tuning."),
            ("Distillation", "Training a small model to mimic a larger one."),
            ("Catastrophic forgetting", "Loss of prior capability after tuning."),
            ("Adapter", "A small trainable module added to a frozen model."),
        ],
        "references": [
            "Howard & Ruder — ULMFiT (2018)",
            "Ouyang et al. — InstructGPT (2022)",
        ],
    },
    {
        "name": "LoRA",
        "tagline": "Low-Rank Adaptation for efficient fine-tuning",
        "language": "python",
        "overview": (
            "Low-Rank Adaptation (LoRA) fine-tunes large models by injecting small trainable "
            "low-rank matrices into frozen weights, dramatically reducing trainable "
            "parameters, memory and storage while retaining quality. LoRA and its variants "
            "(QLoRA, DoRA) made fine-tuning accessible on modest hardware. This book covers "
            "the mathematics, implementation, quantised training, adapter management and "
            "serving."
        ),
        "concepts": [
            ("The Idea Behind Low-Rank Adaptation",
             "Why weight updates are approximately low-rank."),
            ("LoRA Mathematics",
             "Decomposing ΔW into low-rank A·B and the scaling factor."),
            ("Choosing Rank and Target Modules",
             "Where to apply LoRA and how rank affects capacity."),
            ("Implementing LoRA with PEFT",
             "Practical training with the Hugging Face stack."),
            ("QLoRA: Quantised LoRA",
             "4-bit base weights for memory-efficient training."),
            ("DoRA and LoRA Variants",
             "Weight-decomposed and other improvements."),
            ("Hyper-parameters for LoRA",
             "Rank, alpha, dropout and learning rate."),
            ("Merging and Unmerging Adapters",
             "Folding LoRA into base weights for serving."),
            ("Multi-Adapter Serving",
             "Hot-swapping adapters per request."),
            ("Evaluation of LoRA Models",
             "Quality versus full fine-tuning."),
            ("Storage and Distribution",
             "Tiny adapters as portable artefacts."),
            ("Limitations and When to Avoid",
             "Cases where full tuning is warranted."),
            ("Operating LoRA in Production",
             "Registry, routing and lifecycle."),
            ("The LoRA Reference Pipeline",
             "End-to-end blueprint."),
        ],
        "architecture": (
            "LoRA training freezes base weights and trains low-rank adapters, optionally over "
            "a 4-bit quantised base (QLoRA). Adapters are registered as small artefacts and "
            "either merged for single-model serving or hot-swapped at inference to serve many "
            "specialisations from one base model."
        ),
        "patterns": [
            "QLoRA for single-GPU fine-tuning of large models",
            "Adapter registry with metadata and provenance",
            "Multi-adapter hot-swap serving",
            "Merge adapters for latency-critical deployment",
        ],
        "best_practices": [
            "Start with modest rank and tune alpha accordingly.",
            "Target attention projections first, expand if needed.",
            "Use QLoRA to fit large models on limited GPUs.",
            "Track adapters as versioned artefacts.",
        ],
        "pitfalls": [
            "Over-high rank negating efficiency gains.",
            "Mismatched alpha/rank scaling hurting quality.",
            "Merging adapters then losing the ability to swap.",
            "Ignoring base-model version compatibility.",
        ],
        "use_cases": [
            ("SMB", "Affordable domain fine-tuning on single GPUs."),
            ("Platform", "Serving many tenants via per-tenant adapters."),
            ("Research", "Rapid experimentation with cheap adapters."),
            ("Edge", "Compact specialisations for constrained devices."),
        ],
        "tools": ["PEFT", "bitsandbytes", "TRL", "vLLM (LoRA serving)"],
        "glossary": [
            ("LoRA", "Low-rank adaptation of frozen weights."),
            ("QLoRA", "LoRA over a quantised base model."),
            ("Rank", "The dimensionality of the low-rank update."),
            ("Adapter", "Trainable module added to a frozen model."),
        ],
        "references": [
            "Hu et al. — LoRA (2021)",
            "Dettmers et al. — QLoRA (2023)",
        ],
    },
    {
        "name": "PEFT",
        "tagline": "Parameter-efficient fine-tuning methods",
        "language": "python",
        "overview": (
            "Parameter-efficient fine-tuning (PEFT) adapts large models by training a small "
            "fraction of parameters—via adapters, prefixes, prompts or low-rank updates—"
            "achieving near full-fine-tuning quality at a fraction of the cost and storage. "
            "This book surveys the PEFT family, their trade-offs, implementation, and how to "
            "choose and operate them in production."
        ),
        "concepts": [
            ("The Case for Parameter Efficiency",
             "Cost, storage and multi-task motivations."),
            ("Adapter Modules",
             "Bottleneck adapters inserted between layers."),
            ("LoRA and Low-Rank Methods",
             "Low-rank weight updates as PEFT."),
            ("Prefix and Prompt Tuning",
             "Learning soft prompts and prefixes."),
            ("(IA)³ and Scaling Methods",
             "Learned scaling of activations."),
            ("BitFit and Sparse Tuning",
             "Tuning only biases or sparse subsets."),
            ("Comparing PEFT Methods",
             "Quality, cost and applicability trade-offs."),
            ("Implementing PEFT",
             "The Hugging Face PEFT library in practice."),
            ("Multi-Task and Modular PEFT",
             "Composing and routing adapters."),
            ("Evaluation and Selection",
             "Choosing the right method per task."),
            ("Serving PEFT Models",
             "Adapter management and routing."),
            ("Limitations",
             "When full fine-tuning is justified."),
            ("Governance and Lifecycle",
             "Tracking modular artefacts."),
            ("The PEFT Reference Pipeline",
             "End-to-end blueprint."),
        ],
        "architecture": (
            "A PEFT platform keeps a frozen base model and a library of small trainable "
            "modules (adapters, LoRA, soft prompts). A training service produces modules, a "
            "registry versions them, and a serving layer composes or routes modules per task "
            "or tenant on a shared base model."
        ),
        "patterns": [
            "Frozen base + modular adapters per task",
            "Adapter composition for multi-task serving",
            "Registry-driven adapter lifecycle",
            "Method selection by task and budget",
        ],
        "best_practices": [
            "Match the PEFT method to the task and budget.",
            "Share a frozen base across many specialisations.",
            "Benchmark PEFT against full tuning on a held-out set.",
            "Version and govern modules as artefacts.",
        ],
        "pitfalls": [
            "Choosing a method without benchmarking fit.",
            "Adapter sprawl without governance.",
            "Assuming PEFT always matches full tuning.",
            "Base-model/version incompatibility.",
        ],
        "use_cases": [
            ("Platform", "Many specialisations on one base model."),
            ("Cost-sensitive", "Cheap adaptation at scale."),
            ("Multi-task", "Composable task modules."),
            ("Research", "Rapid method comparison."),
        ],
        "tools": ["Hugging Face PEFT", "TRL", "OpenDelta"],
        "glossary": [
            ("PEFT", "Parameter-efficient fine-tuning."),
            ("Adapter", "Small trainable module in a frozen model."),
            ("Prompt tuning", "Learning soft prompt embeddings."),
            ("(IA)³", "Learned activation scaling method."),
        ],
        "references": [
            "Houlsby et al. — Adapters (2019)",
            "Li & Liang — Prefix-Tuning (2021)",
            "Liu et al. — (IA)³ / T-Few (2022)",
        ],
    },
    {
        "name": "RLHF",
        "tagline": "Aligning models with human feedback",
        "language": "python",
        "overview": (
            "Reinforcement Learning from Human Feedback (RLHF) aligns language models with "
            "human preferences by training a reward model from comparisons and optimising the "
            "policy against it, typically with PPO. RLHF and newer methods like DPO turned "
            "capable base models into helpful, harmless assistants. This book covers "
            "preference data, reward modelling, policy optimisation, DPO and the practical "
            "challenges of alignment."
        ),
        "concepts": [
            ("Why Alignment Needs Human Feedback",
             "The gap between next-token prediction and helpful behaviour."),
            ("The RLHF Pipeline",
             "SFT → reward model → RL policy optimisation."),
            ("Collecting Preference Data",
             "Comparisons, annotation quality and guidelines."),
            ("Reward Modelling",
             "Training a model to score responses."),
            ("Policy Optimisation with PPO",
             "Optimising against the reward with KL control."),
            ("KL Penalties and Reward Hacking",
             "Preventing the policy from drifting or gaming."),
            ("Direct Preference Optimisation (DPO)",
             "Skipping the reward model with a direct loss."),
            ("RLAIF and Constitutional Methods",
             "Using AI feedback to scale alignment."),
            ("Evaluation of Aligned Models",
             "Helpfulness, harmlessness and honesty."),
            ("Safety and Red-Teaming",
             "Stress-testing aligned behaviour."),
            ("Cost and Infrastructure",
             "The expense of RLHF at scale."),
            ("Limitations and Open Problems",
             "Reward misspecification and over-optimisation."),
            ("Operating Alignment Pipelines",
             "Data, training and evaluation loops."),
            ("The Alignment Reference Pipeline",
             "End-to-end blueprint."),
        ],
        "architecture": (
            "An RLHF pipeline starts from a supervised fine-tuned model, collects human "
            "preference comparisons to train a reward model, then optimises the policy with "
            "PPO under a KL penalty to the reference model. DPO variants replace the reward/RL "
            "stages with a direct preference loss. Evaluation gates every stage."
        ),
        "patterns": [
            "SFT → RM → PPO classic pipeline",
            "DPO for simpler, stable alignment",
            "KL penalty to anchor to the reference policy",
            "RLAIF to scale feedback with AI judges",
        ],
        "best_practices": [
            "Invest in clear annotation guidelines and quality control.",
            "Use KL penalties to prevent reward hacking.",
            "Consider DPO for stability and simplicity.",
            "Evaluate helpfulness, harmlessness and honesty jointly.",
        ],
        "pitfalls": [
            "Reward hacking from misspecified reward models.",
            "Over-optimisation degrading general capability.",
            "Noisy preference data undermining the reward model.",
            "Ignoring safety regressions during alignment.",
        ],
        "use_cases": [
            ("Assistants", "Turning base models into helpful chat assistants."),
            ("Safety", "Reducing harmful and dishonest outputs."),
            ("Enterprise", "Aligning models to organisational policy."),
            ("Research", "Studying preference optimisation."),
        ],
        "tools": ["TRL", "trlx", "DeepSpeed", "Hugging Face"],
        "glossary": [
            ("Reward model", "A model scoring response quality."),
            ("PPO", "Proximal policy optimisation."),
            ("DPO", "Direct preference optimisation."),
            ("Reward hacking", "Exploiting flaws in the reward signal."),
        ],
        "references": [
            "Christiano et al. — Deep RL from Human Preferences (2017)",
            "Ouyang et al. — InstructGPT (2022)",
            "Rafailov et al. — Direct Preference Optimization (2023)",
        ],
    },
    {
        "name": "AI Security",
        "tagline": "Securing AI systems against adversarial threats",
        "language": "python",
        "overview": (
            "AI security addresses the unique attack surface of machine-learning systems: "
            "prompt injection, data poisoning, model extraction, evasion, jailbreaks and "
            "supply-chain risks. As AI becomes embedded in critical workflows, defending it "
            "requires extending traditional security with ML-specific controls. This book "
            "covers the AI threat landscape, the OWASP LLM Top 10, defensive architecture and "
            "secure development practices."
        ),
        "concepts": [
            ("The AI Threat Landscape",
             "How ML expands the attack surface."),
            ("Prompt Injection and Jailbreaks",
             "Direct and indirect injection and defences."),
            ("Data Poisoning",
             "Corrupting training data and detection."),
            ("Model Extraction and Inversion",
             "Stealing models and reconstructing data."),
            ("Adversarial Examples and Evasion",
             "Crafted inputs that fool models."),
            ("Sensitive Data and Privacy Leakage",
             "Preventing PII exposure in outputs."),
            ("Supply-Chain and Model Provenance",
             "Trusting weights, datasets and dependencies."),
            ("Insecure Output Handling",
             "Treating model output as untrusted input."),
            ("Guardrails and Defence in Depth",
             "Layered input/output controls."),
            ("Agent and Tool Security",
             "Sandboxing and least privilege for autonomy."),
            ("Red-Teaming AI Systems",
             "Adversarial testing methodology."),
            ("Monitoring and Incident Response",
             "Detecting and responding to AI attacks."),
            ("Compliance and Standards",
             "OWASP LLM Top 10, NIST and MITRE ATLAS."),
            ("The Secure AI Reference Architecture",
             "End-to-end defensive blueprint."),
        ],
        "architecture": (
            "A secure AI architecture wraps models with input validation and injection "
            "filtering, constrained decoding, output validation and content moderation, all "
            "behind a gateway enforcing auth, rate limits and tenant isolation. Tool use is "
            "sandboxed with least privilege, and every interaction is logged for detection and "
            "response, mapped to frameworks like the OWASP LLM Top 10 and MITRE ATLAS."
        ),
        "patterns": [
            "Guardrail sandwich: validate input, constrain decode, validate output",
            "Untrusted-content isolation to block indirect injection",
            "Least-privilege, sandboxed tool execution",
            "Defence-in-depth with monitoring and response",
        ],
        "best_practices": [
            "Treat all model output as untrusted before acting on it.",
            "Isolate untrusted content from trusted instructions.",
            "Sandbox tools and enforce least privilege for agents.",
            "Red-team continuously and map findings to OWASP/ATLAS.",
        ],
        "pitfalls": [
            "Trusting LLM output directly in downstream systems.",
            "Mixing untrusted content into instructions (injection).",
            "Granting agents broad, unsandboxed capabilities.",
            "No logging or detection for AI-specific attacks.",
        ],
        "use_cases": [
            ("Finance", "Securing customer-facing AI against fraud and abuse."),
            ("Healthcare", "Preventing PII leakage in clinical assistants."),
            ("Enterprise", "Protecting internal RAG from data exfiltration."),
            ("Platform", "Hardening agent and tool ecosystems."),
        ],
        "tools": ["OWASP LLM Top 10", "MITRE ATLAS", "Guardrails AI", "Rebuff", "NeMo Guardrails"],
        "glossary": [
            ("Prompt injection", "Smuggling instructions via input."),
            ("Data poisoning", "Corrupting training data to alter behaviour."),
            ("Model extraction", "Stealing a model via queries."),
            ("Jailbreak", "Bypassing a model's safety controls."),
        ],
        "references": [
            "OWASP — Top 10 for LLM Applications",
            "MITRE — ATLAS Threat Matrix",
            "NIST — AI Risk Management Framework",
        ],
    },
    {
        "name": "Responsible AI",
        "tagline": "Fair, transparent and accountable AI systems",
        "language": "python",
        "overview": (
            "Responsible AI is the practice of designing, building and operating AI systems "
            "that are fair, transparent, accountable, privacy-preserving and safe. It "
            "translates ethical principles into concrete engineering controls and "
            "organisational processes. This book covers fairness metrics, explainability, "
            "privacy techniques, human oversight, documentation and the operationalisation of "
            "responsible AI across the lifecycle."
        ),
        "concepts": [
            ("Principles of Responsible AI",
             "Fairness, transparency, accountability, privacy and safety."),
            ("Fairness and Bias",
             "Sources of bias and group/individual fairness metrics."),
            ("Measuring and Mitigating Bias",
             "Pre-, in- and post-processing mitigation."),
            ("Explainability and Interpretability",
             "SHAP, LIME, attention and model cards."),
            ("Privacy-Preserving AI",
             "Differential privacy, federated learning and anonymisation."),
            ("Human Oversight and Contestability",
             "Human-in-the-loop and appeal mechanisms."),
            ("Transparency and Documentation",
             "Model cards, datasheets and disclosures."),
            ("Robustness and Reliability",
             "Stability under distribution shift."),
            ("Environmental and Social Impact",
             "Compute footprint and societal effects."),
            ("Responsible Generative AI",
             "Harm reduction in generative systems."),
            ("Operationalising Responsible AI",
             "Review boards, checklists and gates."),
            ("Standards and Regulation",
             "NIST AI RMF, ISO/IEC 42001, EU AI Act."),
            ("Measuring Responsible AI Maturity",
             "Assessing and improving organisational practice."),
            ("The Responsible AI Reference Framework",
             "End-to-end governance integration."),
        ],
        "architecture": (
            "Responsible AI is operationalised as gates across the lifecycle: a design review "
            "assesses risk and intended use, data and model evaluation measure fairness and "
            "robustness, documentation (model cards, datasheets) is produced automatically, "
            "and production monitoring tracks fairness drift with human oversight and appeal "
            "paths."
        ),
        "patterns": [
            "Lifecycle gates for risk, fairness and documentation",
            "Automated model cards and datasheets",
            "Fairness monitoring in production",
            "Human-in-the-loop for high-impact decisions",
        ],
        "best_practices": [
            "Define intended use and out-of-scope use explicitly.",
            "Measure fairness with metrics appropriate to the context.",
            "Document models and data with cards and datasheets.",
            "Provide human oversight and contestability for impactful decisions.",
        ],
        "pitfalls": [
            "Treating fairness as a single metric for all contexts.",
            "Bolting on explainability after deployment.",
            "No monitoring for fairness drift in production.",
            "Undocumented models with unclear intended use.",
        ],
        "use_cases": [
            ("Lending", "Fair, explainable and contestable credit decisions."),
            ("Hiring", "Bias-audited candidate screening with oversight."),
            ("Healthcare", "Equitable, transparent clinical support."),
            ("Public sector", "Accountable, auditable automated decisions."),
        ],
        "tools": ["Fairlearn", "AIF360", "SHAP", "LIME", "Model Card Toolkit"],
        "glossary": [
            ("Demographic parity", "Equal positive rates across groups."),
            ("SHAP", "Shapley-based feature attribution."),
            ("Differential privacy", "Formal privacy guarantee via noise."),
            ("Model card", "Standardised model documentation."),
        ],
        "references": [
            "Mitchell et al. — Model Cards (2019)",
            "NIST — AI Risk Management Framework",
            "ISO/IEC 42001 — AI Management System",
        ],
    },
    {
        "name": "AI Governance",
        "tagline": "Policy, risk and compliance for enterprise AI",
        "language": "python",
        "overview": (
            "AI governance establishes the policies, processes, roles and controls that ensure "
            "AI is developed and used responsibly, legally and in alignment with organisational "
            "values. It spans risk management, regulatory compliance, model inventories, "
            "approval workflows and audit. This book covers governance frameworks, the EU AI "
            "Act and NIST AI RMF, operating models and the tooling that makes governance "
            "scalable."
        ),
        "concepts": [
            ("Why AI Governance",
             "Managing risk, trust and compliance at scale."),
            ("Governance Frameworks",
             "NIST AI RMF, ISO/IEC 42001 and OECD principles."),
            ("Regulatory Landscape",
             "EU AI Act risk tiers and global regulation."),
            ("AI Risk Management",
             "Identifying, assessing and mitigating AI risks."),
            ("Model Inventory and Registry",
             "Cataloguing all AI systems and their risk."),
            ("Approval and Review Workflows",
             "Stage gates from proposal to production."),
            ("Roles and Operating Models",
             "Committees, owners and lines of defence."),
            ("Policy and Standards",
             "Internal policies translating principles to rules."),
            ("Third-Party and Vendor AI Risk",
             "Governing externally sourced models."),
            ("Audit, Evidence and Traceability",
             "Demonstrating compliance to regulators."),
            ("Monitoring and Continuous Assurance",
             "Ongoing oversight of deployed AI."),
            ("Governance Tooling",
             "Platforms automating inventory and controls."),
            ("Measuring Governance Maturity",
             "Assessment and improvement."),
            ("The AI Governance Operating Model",
             "End-to-end reference framework."),
        ],
        "architecture": (
            "An AI governance operating model centres on a model inventory/registry capturing "
            "every system with risk classification, linked to stage-gate approval workflows, "
            "policy controls, evidence capture and continuous monitoring. A governance "
            "platform automates intake, risk scoring, documentation and audit trails across "
            "the three lines of defence."
        ),
        "patterns": [
            "Risk-tiered controls aligned to the EU AI Act",
            "Central model inventory with risk classification",
            "Stage-gate approvals from intake to production",
            "Three lines of defence operating model",
        ],
        "best_practices": [
            "Maintain a complete, current inventory of AI systems.",
            "Classify systems by risk and scale controls accordingly.",
            "Automate evidence capture for auditability.",
            "Align controls to recognised frameworks (NIST, ISO, EU AI Act).",
        ],
        "pitfalls": [
            "Shadow AI not captured in any inventory.",
            "One-size-fits-all controls regardless of risk.",
            "Manual, unauditable governance that does not scale.",
            "Governance disconnected from engineering reality.",
        ],
        "use_cases": [
            ("Banking", "Model risk management under regulatory scrutiny."),
            ("Insurance", "Governing pricing and underwriting models."),
            ("Public sector", "Accountable, lawful automated decisions."),
            ("Enterprise", "Scaling AI adoption with managed risk."),
        ],
        "tools": ["NIST AI RMF", "ISO/IEC 42001", "Model registries", "GRC platforms"],
        "glossary": [
            ("Model inventory", "A catalogue of all AI systems."),
            ("Risk tier", "A classification driving control intensity."),
            ("Three lines of defence", "An operating model for risk ownership."),
            ("EU AI Act", "EU regulation classifying AI by risk."),
        ],
        "references": [
            "NIST — AI Risk Management Framework",
            "EU — Artificial Intelligence Act",
            "ISO/IEC 42001 — AI Management System",
        ],
    },
    {
        "name": "LLMOps",
        "tagline": "Operating large language model applications in production",
        "language": "python",
        "overview": (
            "LLMOps extends MLOps to the unique demands of large language model applications: "
            "prompt management, retrieval pipelines, evaluation of non-deterministic output, "
            "cost and latency control, guardrails and continuous improvement from feedback. "
            "This book covers the LLMOps lifecycle, evaluation, observability, deployment "
            "patterns and the platform that operationalises generative applications."
        ),
        "concepts": [
            ("From MLOps to LLMOps",
             "What changes when the model is a foundation model."),
            ("Prompt and Context Management",
             "Versioning prompts, templates and retrieval config."),
            ("Evaluation of Non-Deterministic Systems",
             "Offline evals, LLM-as-judge and online experiments."),
            ("Observability for LLM Apps",
             "Tracing prompts, completions, tokens and quality."),
            ("Cost and Latency Engineering",
             "Caching, routing, batching and budgets."),
            ("Guardrails and Safety Operations",
             "Operationalising input/output controls."),
            ("Deployment Patterns",
             "Gateways, canaries and model routing."),
            ("Feedback Loops and Continuous Improvement",
             "Capturing signals and closing the loop."),
            ("Retrieval Pipeline Operations",
             "Monitoring and maintaining RAG."),
            ("Model and Provider Management",
             "Multi-provider routing and upgrades."),
            ("Testing in CI/CD",
             "Eval gates for prompt and model changes."),
            ("Incident Response for LLM Apps",
             "Handling regressions and outages."),
            ("Cost Governance and FinOps",
             "Controlling generative spend."),
            ("The LLMOps Reference Platform",
             "End-to-end operational blueprint."),
        ],
        "architecture": (
            "An LLMOps platform comprises a model gateway (auth, routing, caching, rate "
            "limits), a prompt registry, a retrieval service, a guardrail layer, an "
            "evaluation service running offline and online, and an observability pipeline "
            "feeding cost, latency and quality dashboards plus a feedback store that drives "
            "continuous improvement."
        ),
        "patterns": [
            "Eval gates in CI for every prompt/model change",
            "Model gateway with caching and routing",
            "Online A/B and shadow evaluation",
            "Feedback loop from production to dataset",
        ],
        "best_practices": [
            "Gate prompt and model changes behind automated evals.",
            "Trace every request end to end with cost and quality.",
            "Set and enforce cost/latency budgets per use case.",
            "Capture user feedback and feed it back into evaluation.",
        ],
        "pitfalls": [
            "Shipping prompt changes with no evaluation.",
            "No tracing, making regressions invisible.",
            "Runaway cost from unmonitored token growth.",
            "Treating LLM apps like deterministic services.",
        ],
        "use_cases": [
            ("SaaS", "Operating AI features with quality and cost control."),
            ("Enterprise", "Governed internal assistants at scale."),
            ("Support", "Continuously improving deflection bots."),
            ("Platform", "Shared LLM gateway for many teams."),
        ],
        "tools": ["LangSmith", "Langfuse", "Helicone", "Arize Phoenix", "Ragas"],
        "glossary": [
            ("LLM-as-judge", "Using an LLM to score outputs."),
            ("Eval gate", "A CI check on quality before release."),
            ("Model gateway", "A proxy abstracting model providers."),
            ("Shadow deployment", "Running a new version on live traffic silently."),
        ],
        "references": [
            "Chip Huyen — Building LLM applications for production",
            "LangSmith / Langfuse — Documentation",
        ],
    },
    {
        "name": "MLOps",
        "tagline": "Reliable, automated machine-learning operations",
        "language": "python",
        "overview": (
            "MLOps applies DevOps principles to machine learning, automating the lifecycle "
            "from data and training through deployment, monitoring and retraining. It brings "
            "reproducibility, continuous delivery and reliability to ML systems. This book "
            "covers pipelines, the feature store, model registry, CI/CD for ML, monitoring, "
            "drift detection and the platform that ties them together."
        ),
        "concepts": [
            ("The MLOps Maturity Model",
             "From manual notebooks to fully automated pipelines."),
            ("Reproducible Data and Pipelines",
             "Versioning data, code and environments."),
            ("Feature Stores",
             "Online/offline parity and feature reuse."),
            ("Experiment Tracking and Registry",
             "Recording runs and managing model versions."),
            ("Training Pipelines and Orchestration",
             "Automated, scheduled and event-driven training."),
            ("CI/CD for Machine Learning",
             "Testing, packaging and deploying models."),
            ("Model Serving",
             "Online, batch and streaming inference patterns."),
            ("Monitoring and Drift Detection",
             "Data, concept and performance drift."),
            ("Automated Retraining",
             "Triggers and guardrails for retraining."),
            ("Testing ML Systems",
             "Data, model and integration tests."),
            ("Governance and Lineage",
             "Traceability and compliance."),
            ("Cost and Resource Management",
             "Efficient use of compute."),
            ("Platform and Team Topologies",
             "Building an ML platform team."),
            ("The MLOps Reference Architecture",
             "End-to-end operational blueprint."),
        ],
        "architecture": (
            "An MLOps platform connects a feature store, an experiment-tracking and model "
            "registry, orchestrated training pipelines, CI/CD that tests and promotes models, "
            "and serving infrastructure with monitoring for drift and performance that can "
            "trigger automated retraining—all under lineage and governance."
        ),
        "patterns": [
            "Feature store for online/offline parity",
            "Model registry with staged promotion",
            "Champion/challenger and shadow deployment",
            "Drift-triggered automated retraining",
        ],
        "best_practices": [
            "Version data, code and environments together.",
            "Automate testing and promotion through CI/CD.",
            "Monitor drift and tie it to retraining triggers.",
            "Maintain lineage from data to deployed model.",
        ],
        "pitfalls": [
            "Training/serving skew from inconsistent features.",
            "Manual, irreproducible deployment.",
            "No drift monitoring, leading to silent decay.",
            "Models in production with no lineage.",
        ],
        "use_cases": [
            ("Retail", "Automated demand-forecast retraining."),
            ("Finance", "Governed, monitored risk models."),
            ("Ads", "High-throughput online prediction."),
            ("Manufacturing", "Edge model deployment and monitoring."),
        ],
        "tools": ["MLflow", "Kubeflow", "Airflow", "Feast", "Seldon", "Evidently"],
        "glossary": [
            ("Feature store", "System for consistent feature serving."),
            ("Model registry", "Catalogue of versioned models."),
            ("Concept drift", "Change in the input–output relationship."),
            ("Training/serving skew", "Mismatch between train and inference data."),
        ],
        "references": [
            "Sculley et al. — Hidden Technical Debt in ML Systems (2015)",
            "Google — MLOps: Continuous delivery for ML",
        ],
    },
    {
        "name": "AIOps",
        "tagline": "AI for IT operations and observability",
        "language": "python",
        "overview": (
            "AIOps applies machine learning and analytics to IT operations data—metrics, "
            "logs, traces and events—to automate detection, correlation, root-cause analysis "
            "and remediation. It helps operations teams cope with the scale and complexity of "
            "modern systems. This book covers anomaly detection, event correlation, "
            "root-cause analysis, predictive operations and the AIOps platform."
        ),
        "concepts": [
            ("The Case for AIOps",
             "Operational data scale beyond human capacity."),
            ("Observability Data Foundations",
             "Metrics, logs, traces and events."),
            ("Anomaly Detection",
             "Statistical and ML methods for outliers."),
            ("Event Correlation and Noise Reduction",
             "Grouping related alerts to reduce fatigue."),
            ("Root-Cause Analysis",
             "Causal inference and topology-aware diagnosis."),
            ("Predictive Operations",
             "Forecasting capacity and failures."),
            ("Automated Remediation",
             "Closed-loop and guarded auto-remediation."),
            ("Log Analytics with NLP",
             "Parsing and clustering unstructured logs."),
            ("LLMs in AIOps",
             "Incident summarisation and assistant copilots."),
            ("Alerting and SLO Management",
             "Reducing noise and protecting reliability."),
            ("Integration with ITSM and Incident Response",
             "Connecting detection to action."),
            ("Evaluation and Trust",
             "Measuring precision/recall of operations ML."),
            ("Operating an AIOps Platform",
             "Data pipelines and model lifecycle."),
            ("The AIOps Reference Architecture",
             "End-to-end operational blueprint."),
        ],
        "architecture": (
            "An AIOps platform ingests metrics, logs, traces and events into a unified data "
            "lake, applies anomaly detection and correlation to reduce noise, performs "
            "topology-aware root-cause analysis, and triggers guarded automated remediation or "
            "enriched incidents in the ITSM/incident system, increasingly with LLM-based "
            "summarisation."
        ),
        "patterns": [
            "Multi-signal anomaly detection",
            "Alert correlation to a single incident",
            "Topology-aware root-cause analysis",
            "Guarded closed-loop remediation",
        ],
        "best_practices": [
            "Unify observability signals before applying ML.",
            "Tune for precision to avoid alert fatigue.",
            "Keep humans in the loop for risky remediation.",
            "Measure model precision/recall against incidents.",
        ],
        "pitfalls": [
            "Anomaly detectors that flood teams with false positives.",
            "Auto-remediation without safeguards causing outages.",
            "Siloed signals preventing correlation.",
            "No feedback loop to improve detection.",
        ],
        "use_cases": [
            ("SRE", "Noise reduction and faster incident resolution."),
            ("Cloud", "Capacity forecasting and cost anomalies."),
            ("Networks", "Fault detection across topology."),
            ("Enterprise IT", "Predictive maintenance of services."),
        ],
        "tools": ["Prometheus", "Elastic", "Dynatrace", "Datadog", "Moogsoft"],
        "glossary": [
            ("Anomaly detection", "Identifying unusual behaviour."),
            ("Correlation", "Grouping related events/alerts."),
            ("RCA", "Root-cause analysis."),
            ("SLO", "Service-level objective."),
        ],
        "references": [
            "Gartner — AIOps Market Guide",
            "Google SRE — Site Reliability Engineering",
        ],
    },
    {
        "name": "AgentOps",
        "tagline": "Operating autonomous agents in production",
        "language": "python",
        "overview": (
            "AgentOps is the emerging discipline of deploying, monitoring, evaluating and "
            "governing autonomous AI agents in production. Agents add statefulness, tool use, "
            "multi-step trajectories and emergent behaviour that traditional ops cannot "
            "handle. This book covers agent observability, trajectory evaluation, cost and "
            "safety control, human oversight and the AgentOps platform."
        ),
        "concepts": [
            ("Why Agents Need New Operations",
             "Statefulness, autonomy and emergent risk."),
            ("Agent Observability and Tracing",
             "Capturing reasoning, tool calls and outcomes."),
            ("Trajectory Evaluation",
             "Scoring multi-step behaviour, not just final answers."),
            ("Cost and Loop Control",
             "Budgets, step limits and runaway prevention."),
            ("Safety and Permission Management",
             "Sandboxing and least privilege at scale."),
            ("Human-in-the-Loop Operations",
             "Approvals, escalation and intervention."),
            ("Memory and State Management",
             "Operating long-lived agent memory."),
            ("Tool Reliability and Contracts",
             "Monitoring and versioning agent tools."),
            ("Testing and Simulation",
             "Replaying and stress-testing agents."),
            ("Incident Response for Agents",
             "Diagnosing and containing agent failures."),
            ("Multi-Agent Operations",
             "Coordinating and observing agent teams."),
            ("Governance of Autonomous Systems",
             "Policy and audit for agents."),
            ("Continuous Improvement",
             "Learning from production trajectories."),
            ("The AgentOps Reference Platform",
             "End-to-end operational blueprint."),
        ],
        "architecture": (
            "An AgentOps platform traces every agent step (reasoning, tool call, observation) "
            "to an observability store, enforces budgets and permissions through a controller, "
            "evaluates trajectories offline and online, routes high-impact actions to human "
            "approval, and feeds production traces back into testing and improvement."
        ),
        "patterns": [
            "Full trajectory tracing and replay",
            "Step/cost budgets with circuit breakers",
            "Human approval gates for risky actions",
            "Trajectory-level evaluation and scoring",
        ],
        "best_practices": [
            "Trace and replay every agent trajectory.",
            "Enforce hard budgets and circuit breakers.",
            "Evaluate trajectories, not just final outputs.",
            "Gate irreversible actions behind human approval.",
        ],
        "pitfalls": [
            "No trajectory visibility, making failures opaque.",
            "Unbounded loops and cost.",
            "Over-broad permissions enabling harm.",
            "Evaluating only final answers, missing process errors.",
        ],
        "use_cases": [
            ("Engineering", "Operating autonomous coding agents."),
            ("Operations", "Incident and workflow automation agents."),
            ("Customer", "Autonomous resolution with oversight."),
            ("Platform", "Shared agent runtime governance."),
        ],
        "tools": ["LangSmith", "Langfuse", "AgentOps.ai", "Arize", "OpenTelemetry"],
        "glossary": [
            ("Trajectory", "The sequence of an agent's steps."),
            ("Circuit breaker", "A control that halts runaway behaviour."),
            ("Tool contract", "A typed agreement for a tool interface."),
            ("Replay", "Re-running a recorded trajectory."),
        ],
        "references": [
            "Industry practice — emerging AgentOps tooling",
            "OpenTelemetry — GenAI semantic conventions",
        ],
    },
    {
        "name": "AI Architecture",
        "tagline": "Designing enterprise AI systems and platforms",
        "language": "python",
        "overview": (
            "AI architecture is the discipline of designing the systems, platforms and "
            "integration patterns that deliver AI capabilities reliably, securely and "
            "economically at enterprise scale. It bridges data, models, applications and "
            "operations under quality attributes such as scalability, latency, security and "
            "cost. This book covers reference architectures, patterns, trade-off analysis and "
            "the architect's role in AI programs."
        ),
        "concepts": [
            ("The Role of the AI Architect",
             "Bridging strategy, engineering and operations."),
            ("Quality Attributes for AI Systems",
             "Latency, scalability, cost, security and reliability."),
            ("Reference Architectures",
             "RAG, agents, training and inference blueprints."),
            ("The Model Gateway Pattern",
             "Abstracting providers and centralising control."),
            ("Data Architecture for AI",
             "Lakes, feature stores and vector stores."),
            ("Inference Architecture",
             "Online, batch and streaming serving."),
            ("Integration Patterns",
             "APIs, events and orchestration."),
            ("Scalability and Performance",
             "Caching, batching and capacity planning."),
            ("Security and Multi-Tenancy",
             "Isolation, access control and guardrails."),
            ("Cost Architecture and FinOps",
             "Designing for economic efficiency."),
            ("Build versus Buy",
             "Foundation models, platforms and components."),
            ("Architecture Decision Records",
             "Capturing and justifying decisions."),
            ("Migration and Modernisation",
             "Evolving toward AI-native systems."),
            ("The Enterprise AI Platform Architecture",
             "A cohesive end-to-end blueprint."),
        ],
        "architecture": (
            "An enterprise AI platform layers a data foundation (lake, feature store, vector "
            "store), a model layer (training, registry, gateway to internal and external "
            "models), an application layer (RAG, agents, copilots) and a cross-cutting "
            "operations and governance plane (observability, security, cost, compliance). "
            "Clean contracts between layers enable independent evolution."
        ),
        "patterns": [
            "Model gateway abstraction",
            "Layered data/model/application/ops architecture",
            "Strangler-fig migration to AI-native systems",
            "Architecture decision records for traceability",
        ],
        "best_practices": [
            "Design to explicit quality attributes and budgets.",
            "Centralise model access behind a gateway.",
            "Record architecture decisions and their rationale.",
            "Separate concerns into clean, evolvable layers.",
        ],
        "pitfalls": [
            "Point-to-point model integrations that sprawl.",
            "Ignoring cost as a first-class quality attribute.",
            "No clear ownership of cross-cutting concerns.",
            "Big-bang rewrites instead of incremental migration.",
        ],
        "use_cases": [
            ("Enterprise", "Shared AI platform for many product teams."),
            ("Finance", "Governed, low-latency inference at scale."),
            ("Retail", "Unified data and model platform."),
            ("Telecom", "High-throughput AI services."),
        ],
        "tools": ["C4 model", "ArchiMate", "Kubernetes", "Cloud platforms"],
        "glossary": [
            ("Quality attribute", "A non-functional requirement like latency."),
            ("Model gateway", "A proxy centralising model access."),
            ("ADR", "Architecture decision record."),
            ("Strangler fig", "Incremental migration pattern."),
        ],
        "references": [
            "Bass, Clements & Kazman — Software Architecture in Practice",
            "Google / AWS / Azure — AI architecture reference guides",
        ],
    },
    {
        "name": "AI Testing",
        "tagline": "Quality assurance for AI and ML systems",
        "language": "python",
        "overview": (
            "AI testing extends software quality assurance to systems whose behaviour is "
            "learned and probabilistic. It covers data validation, model testing, behavioural "
            "and metamorphic testing, evaluation of generative output and adversarial "
            "robustness. This book covers a comprehensive testing strategy for AI, from unit "
            "tests on data to red-teaming of LLM applications, integrated into CI/CD."
        ),
        "concepts": [
            ("Why Testing AI Is Different",
             "Non-determinism, data dependence and emergent behaviour."),
            ("Data Validation and Testing",
             "Schema, distribution and integrity checks."),
            ("Model Testing",
             "Performance, slices and invariants."),
            ("Behavioural Testing",
             "Capability tests (CheckList-style) for NLP."),
            ("Metamorphic Testing",
             "Relations that should hold under input transforms."),
            ("Evaluating Generative Output",
             "Reference-based, reference-free and LLM-as-judge."),
            ("Golden Datasets and Regression",
             "Curated test sets and change gates."),
            ("Adversarial and Robustness Testing",
             "Stress-testing under perturbation and attack."),
            ("Fairness and Bias Testing",
             "Slice-based fairness checks."),
            ("Property-Based Testing for ML",
             "Generating diverse test cases."),
            ("Testing RAG and Agents",
             "Component and end-to-end evaluation."),
            ("Testing in CI/CD",
             "Automated quality gates."),
            ("Test Data Management",
             "Curating and versioning test data."),
            ("The AI Testing Reference Strategy",
             "A layered, end-to-end testing approach."),
        ],
        "architecture": (
            "An AI testing strategy layers data tests (schema/distribution), model tests "
            "(metrics, slices, invariants, metamorphic), application tests (RAG/agent "
            "evaluation) and adversarial/red-team testing, all wired into CI/CD as quality "
            "gates with versioned golden datasets and tracked results."
        ),
        "patterns": [
            "Layered testing: data → model → application → adversarial",
            "Golden dataset regression gates in CI",
            "Metamorphic relations for oracle-free testing",
            "Slice-based evaluation for fairness and robustness",
        ],
        "best_practices": [
            "Test data quality before model quality.",
            "Use slices to find where models fail.",
            "Gate releases with golden-dataset regression.",
            "Red-team generative apps before launch.",
        ],
        "pitfalls": [
            "Testing only aggregate accuracy, hiding slice failures.",
            "No regression suite for prompt/model changes.",
            "Ignoring data quality in tests.",
            "Treating non-deterministic output with brittle exact-match tests.",
        ],
        "use_cases": [
            ("Enterprise", "Quality gates for AI features."),
            ("Safety-critical", "Robustness and adversarial assurance."),
            ("RAG", "Faithfulness and relevance testing."),
            ("Agents", "Trajectory and task-success testing."),
        ],
        "tools": ["Great Expectations", "pytest", "CheckList", "DeepEval", "Ragas"],
        "glossary": [
            ("Metamorphic testing", "Testing via input–output relations."),
            ("Golden dataset", "A curated reference test set."),
            ("Slice", "A subset of data for targeted evaluation."),
            ("LLM-as-judge", "Using an LLM to grade outputs."),
        ],
        "references": [
            "Ribeiro et al. — CheckList (2020)",
            "Great Expectations — Data testing framework",
        ],
    },
    {
        "name": "AI Observability",
        "tagline": "Monitoring, tracing and debugging AI in production",
        "language": "python",
        "overview": (
            "AI observability provides the visibility needed to understand, debug and improve "
            "AI systems in production: tracking inputs, outputs, quality, drift, cost and "
            "latency, and tracing complex pipelines. It is the feedback loop that keeps AI "
            "trustworthy. This book covers metrics, tracing, evaluation in production, drift "
            "detection and the observability platform for ML and LLM systems."
        ),
        "concepts": [
            ("The Pillars of AI Observability",
             "Metrics, traces, logs and evaluations."),
            ("Instrumenting AI Pipelines",
             "Capturing inputs, outputs and metadata."),
            ("Tracing LLM and Agent Pipelines",
             "Span-based tracing across steps and tools."),
            ("Quality Monitoring",
             "Online evaluation and feedback signals."),
            ("Drift Detection",
             "Data, prediction and embedding drift."),
            ("Performance Monitoring",
             "Latency, throughput and errors."),
            ("Cost and Token Monitoring",
             "Tracking and attributing spend."),
            ("Root-Cause Analysis",
             "Localising failures in complex pipelines."),
            ("Embedding and Vector Observability",
             "Monitoring retrieval quality."),
            ("Alerting and SLOs for AI",
             "Defining and protecting quality SLOs."),
            ("Feedback Capture",
             "Explicit and implicit user feedback."),
            ("Standards and OpenTelemetry",
             "GenAI semantic conventions."),
            ("Building an Observability Platform",
             "Pipelines and dashboards."),
            ("The AI Observability Reference Architecture",
             "End-to-end blueprint."),
        ],
        "architecture": (
            "An AI observability platform instruments pipelines with tracing (often "
            "OpenTelemetry GenAI conventions), streams inputs/outputs/metadata to a store, "
            "runs online evaluations for quality, computes drift on data and embeddings, and "
            "surfaces cost, latency and quality on dashboards with SLO-based alerting and a "
            "feedback store."
        ),
        "patterns": [
            "Span-based tracing of LLM/agent pipelines",
            "Online evaluation sampling for quality",
            "Drift detection on inputs and embeddings",
            "SLO-based alerting on quality and latency",
        ],
        "best_practices": [
            "Instrument every stage with traces and metadata.",
            "Sample production traffic for online evaluation.",
            "Monitor drift on inputs, outputs and embeddings.",
            "Define quality SLOs and alert on them.",
        ],
        "pitfalls": [
            "Logging requests but not quality.",
            "No tracing across multi-step pipelines.",
            "Ignoring drift until accuracy collapses.",
            "No feedback capture to close the loop.",
        ],
        "use_cases": [
            ("SaaS", "Monitoring AI feature quality and cost."),
            ("Enterprise", "Debugging RAG and agent failures."),
            ("Finance", "Drift monitoring for governed models."),
            ("Platform", "Shared observability for AI teams."),
        ],
        "tools": ["Arize Phoenix", "Langfuse", "OpenTelemetry", "Evidently", "WhyLabs"],
        "glossary": [
            ("Trace", "A record of a request's path through a system."),
            ("Drift", "Change in data or model behaviour over time."),
            ("SLO", "Service-level objective."),
            ("Span", "A unit of work within a trace."),
        ],
        "references": [
            "OpenTelemetry — GenAI Observability conventions",
            "Arize / Evidently — Documentation",
        ],
    },
    {
        "name": "AI Product Management",
        "tagline": "Building successful AI-powered products",
        "language": "python",
        "overview": (
            "AI product management is the practice of identifying, building and scaling "
            "products powered by AI, balancing user value, technical feasibility, "
            "probabilistic behaviour, cost and risk. It demands new skills: framing problems "
            "for ML, designing for uncertainty, measuring quality and managing the data "
            "flywheel. This book covers AI product discovery, design, metrics, go-to-market "
            "and responsible scaling."
        ),
        "concepts": [
            ("What Makes AI Products Different",
             "Probabilistic behaviour, data dependence and trust."),
            ("Opportunity Identification",
             "Finding high-value, AI-suited problems."),
            ("Feasibility and Build-versus-Buy",
             "Assessing technical and data feasibility."),
            ("Designing for Uncertainty",
             "UX patterns for probabilistic systems."),
            ("Defining Success Metrics",
             "Quality, engagement and business outcomes."),
            ("The Data Flywheel",
             "Designing products that improve with use."),
            ("Prototyping and Validation",
             "De-risking with rapid experiments."),
            ("Managing Quality and Trust",
             "Setting expectations and handling errors gracefully."),
            ("Cost and Unit Economics",
             "Token and inference costs in the business model."),
            ("Responsible AI Product Decisions",
             "Fairness, safety and disclosure in products."),
            ("Go-to-Market for AI",
             "Positioning, pricing and adoption."),
            ("Roadmapping AI Products",
             "Sequencing capability and risk."),
            ("Cross-Functional AI Teams",
             "Working with research, engineering and design."),
            ("The AI Product Lifecycle",
             "A reference framework from discovery to scale."),
        ],
        "architecture": (
            "AI product delivery is organised as a discovery-to-scale lifecycle: opportunity "
            "and feasibility assessment, prototyping with offline evaluation, MVP launch with "
            "quality and cost guardrails, instrumentation for the data flywheel, and "
            "responsible scaling—aligned across product, design, engineering and research."
        ),
        "patterns": [
            "Data flywheel designed into the product",
            "Graceful degradation and human fallback UX",
            "Offline eval before online experiment before launch",
            "Unit economics modelling for inference cost",
        ],
        "best_practices": [
            "Frame problems as measurable ML objectives tied to value.",
            "Design UX that sets expectations and handles errors.",
            "Instrument feedback to power a data flywheel.",
            "Model inference cost in the business case.",
        ],
        "pitfalls": [
            "Building AI features with no clear user value.",
            "UX that hides uncertainty and erodes trust on error.",
            "Ignoring inference cost in unit economics.",
            "No feedback loop, so the product never improves.",
        ],
        "use_cases": [
            ("SaaS", "Embedding AI copilots into products."),
            ("Consumer", "Assistant and personalisation features."),
            ("Enterprise", "Productising internal AI capabilities."),
            ("Platform", "AI APIs and developer products."),
        ],
        "tools": ["Amplitude", "Mixpanel", "LangSmith", "Experimentation platforms"],
        "glossary": [
            ("Data flywheel", "Usage generating data that improves the product."),
            ("Unit economics", "Per-unit cost and revenue of a product."),
            ("Graceful degradation", "Falling back gracefully on failure."),
            ("Offline eval", "Pre-launch quality evaluation."),
        ],
        "references": [
            "Cagan — Inspired",
            "Google PAIR — People + AI Guidebook",
        ],
    },
]


# Build lookup structures -----------------------------------------------------

def _slugify(name: str) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


for _entry in _DOMAIN_LIST:
    _entry["slug"] = _slugify(_entry["name"])

DOMAINS: dict[str, dict[str, Any]] = {e["slug"]: e for e in _DOMAIN_LIST}
CATEGORIES: list[dict[str, str]] = [
    {"name": e["name"], "slug": e["slug"], "tagline": e["tagline"]} for e in _DOMAIN_LIST
]


def get_domain(slug: str) -> dict[str, Any]:
    return DOMAINS[slug]
