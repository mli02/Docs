# The Master Plan: Building an AI Platform From Scratch

A complete roadmap to building an AI inference platform and RL training infrastructure—from GPU kernels to Kubernetes operators—using C++, Rust, Go, and CUDA.

---

## The Vision

By the end of this journey, you will have built:

```
┌─────────────────────────────────────────────────────────────────────┐
│                              Your Stack                             │
├─────────────────────────────────────────────────────────────────────┤
│  EnvRuntime     │ RL environment execution at scale                 │
│  TaskForge      │ Task generation and verification                  │
│  WorldGen       │ Synthetic data generation with rules              │
│  Launchpad      │ PaaS that deploys everything to Kubernetes        │
│  ModelHub       │ ML platform with traffic management & A/B testing │
│  TinyInfer      │ Inference engine running your custom CUDA kernels │
│  VectorForge    │ Vector database for embeddings and RAG            │
│  TinyKV         │ Distributed KV store with Raft consensus          │
│  MiniDB         │ SQL database engine for structured data           │
│  TinyKernels    │ GPU compute primitives (GEMM, attention, etc.)    │
└─────────────────────────────────────────────────────────────────────┘
```

This is not a toy. Each component teaches fundamental systems concepts while building toward a working, integrated platform.

---

## Prerequisites

Before starting, work through the foundational reading:

| Book | Chapters | Focus |
|------|----------|-------|
| **CSAPP** | 1-6 | How programs execute |
| **OSTEP** | Parts 1-2 | Processes, memory, concurrency |

You don't need to finish these completely before starting—but you should be actively reading them during Phase 1.

---

## Build Order Overview

```
Phase 1: TinyKernels
              │
Phase 2: TinyInfer ─────┬───── VectorForge
              │         │           │
Phase 3:     └─────────┬┘           │
                       │            │
              TinyKV ──┴────────────┘
                       │
Phase 4:          ModelHub
                       │
Phase 5:          Launchpad
                       │
Phase 6:          WorldGen
                       │
Phase 7:        InterfaceGen
                       │
Phase 8:          TaskForge
                       │
Phase 9:          EnvRuntime
```

---

## Phase 1: TinyKernels (GPU Primitives)

**Language:** CUDA/C++

**Goal:** Build the computational foundation—optimized GPU kernels for ML workloads.

### Step 1.1: GPU Fundamentals

| Topic | Deliverable |
|-------|-------------|
| Environment setup, first kernels | Vector add, matrix transpose |
| Memory coalescing, shared memory | Benchmark showing 10x improvement |
| Tiled matrix multiply | GEMM with shared memory tiling |
| Parallel primitives | Reduction, prefix scan |
| Histogram, sorting | Radix sort on GPU |
| Profiling deep dive | Nsight Compute analysis of all kernels |

**Milestone:** Can explain why your tiled GEMM is faster than naive, with profiler data to prove it.

**Reading:** "CUDA by Example" + CUDA Programming Guide chapters 1-6

### Step 1.2: GEMM Mastery

| Topic | Deliverable |
|-------|-------------|
| GEMM interface design | Clean API, test harness, cuBLAS comparison |
| Register tiling | Each thread computes 4x4 or 8x8 output tile |
| Double buffering | Hide memory latency with prefetching |
| Vectorized loads | float4 loads, bank conflict elimination |
| Auto-tuning | Find optimal tile sizes per GPU |
| Tensor Cores | WMMA API, mixed precision |

**Milestone:** GEMM achieving 70%+ of cuBLAS performance. You can explain every optimization.

**Reading:** CUTLASS source code, "Programming Massively Parallel Processors" chapters 4-8

### Step 1.3: Attention & Fusion

| Topic | Deliverable |
|-------|-------------|
| Standard attention | Naive Q @ K.T @ V, memory analysis |
| Online softmax | Numerically stable, single-pass |
| FlashAttention v1 | Tiled attention, O(n) memory |
| FlashAttention v2 | Improved parallelism |
| Fused activations | ReLU, GELU, SiLU with bias fusion |
| Fused normalization | LayerNorm, RMSNorm |

**Milestone:** FlashAttention within 2x of official implementation. Fused kernels 3x faster than separate ops.

**Reading:** FlashAttention paper, FlashAttention-2 paper

### Step 1.4: Framework Integration

| Topic | Deliverable |
|-------|-------------|
| PyTorch custom ops | torch.autograd.Function wrappers |
| Backward passes | Gradient computation for GEMM, attention |
| NCCL basics | All-reduce, broadcast |
| Tensor parallelism | Split GEMM across GPUs |
| JAX integration | Custom primitives |
| Documentation & release | Clean API, benchmarks |

**Milestone:** Drop-in replacements for `torch.nn.functional.linear` and `F.scaled_dot_product_attention` using your kernels.

### Phase 1 Checkpoint

By now you have:
- [x] Deep understanding of GPU architecture
- [x] TinyKernels library with GEMM, attention, fused ops
- [x] PyTorch and JAX integration
- [x] Multi-GPU support

**You can now write ML kernels. This is rare and valuable.**

### Production Integration: GPU Kernels

| Your Code | Production Alternative | When to Use Each |
|-----------|----------------------|------------------|
| TinyKernels GEMM | cuBLAS | Use cuBLAS for standard ops, your kernels for custom/fused ops |
| TinyKernels Attention | FlashAttention (official) | Contribute optimizations upstream, use official for production |
| Custom fused kernels | Triton | Prototype in Triton, port to CUDA if perf-critical |

**What to keep:** Custom fused kernels for novel architectures, quantization schemes, or ops not covered by libraries.

**Abstraction pattern:**
```cpp
// Backend interface allows swapping implementations
class GemmBackend {
public:
    virtual void gemm(const Tensor& A, const Tensor& B, Tensor& C) = 0;
};

class CublasBackend : public GemmBackend { /* uses cuBLAS */ };
class TinyKernelsBackend : public GemmBackend { /* your kernels */ };
class TritonBackend : public GemmBackend { /* Triton JIT */ };
```

---

## Phase 2: TinyInfer + VectorForge (Parallel Track)

These can be built in parallel since they only share TinyKernels.

### TinyInfer - Inference Engine

**Language:** C++

**Goal:** Use TinyKernels to build an inference engine.

#### Step 2.1: Core Engine

| Topic | Deliverable |
|-------|-------------|
| Tensor library | Memory management, views, broadcasting |
| ONNX parser | Load model graphs |
| Graph representation | IR for optimization |
| Graph optimizations | Constant folding, op fusion |
| Runtime execution | Memory planning, kernel dispatch |
| Integration with TinyKernels | GEMM, attention using your kernels |

**Milestone:** Can load and run GPT-2 or LLaMA-7B using your kernels.

**Key Integration:**
```cpp
// TinyInfer uses TinyKernels
#include "tinykernels/gemm.cuh"
#include "tinykernels/attention.cuh"

class LinearOp : public Operator {
    void forward(const Tensor& input, Tensor& output) override {
        tinykernels::gemm(input, weights_, output);
    }
};
```

#### Step 2.2: Production Features

| Topic | Deliverable |
|-------|-------------|
| Quantization | INT8/INT4 inference |
| KV cache | Efficient autoregressive generation |
| Batching | Dynamic batching, continuous batching |
| Speculative decoding | Draft model acceleration |
| Server interface | gRPC/HTTP API |
| Benchmarks & docs | Throughput/latency numbers, deployment guide |

**Milestone:** Inference server matching vLLM/TensorRT-LLM performance within 2x.

---

### VectorForge - Vector Database

**Language:** Rust

**Goal:** High-performance similarity search for RAG.

#### Step 2.3: Core Vector Storage

| Topic | Deliverable |
|-------|-------------|
| Vector storage | Memory-mapped vectors, basic I/O |
| Brute-force search | SIMD-optimized distance functions |
| HNSW index | Hierarchical navigable small world |
| Filtering | Metadata filters with vector search |
| Persistence | WAL, snapshots |
| gRPC API | Insert, search, delete |

**Milestone:** 1M vectors, <10ms p99 search latency.

#### Step 2.4: Distribution

| Topic | Deliverable |
|-------|-------------|
| Sharding | Partition vectors across nodes |
| Replication | Replicate shards for availability |
| Distributed search | Query routing, result merging |
| Cluster management | Node discovery, rebalancing |
| Consistency | Read-your-writes, eventual consistency |
| Production hardening | Monitoring, graceful degradation |

**Milestone:** 3-node cluster handling 10M vectors.

**Key Integration:**
```rust
// VectorForge uses TinyInfer for embedding
impl VectorForge {
    pub async fn insert_text(&self, id: &str, text: &str) -> Result<()> {
        let embedding = self.embedder.embed(text).await?; // Calls TinyInfer
        self.insert_vector(id, &embedding).await
    }
}
```

### Phase 2 Checkpoint

By now you have:
- [x] TinyKernels (GPU primitives)
- [x] TinyInfer (inference engine using TinyKernels)
- [x] VectorForge (vector DB for RAG)

**You can now run RAG pipelines entirely on your own stack.**

### Production Integration: Inference & Vector Search

**TinyInfer alternatives:**

| Your Code | Production Alternative | When to Use Each |
|-----------|----------------------|------------------|
| TinyInfer | vLLM | Use vLLM for production LLM serving, contribute your optimizations |
| TinyInfer | TensorRT-LLM | Maximum NVIDIA optimization, less flexibility |
| TinyInfer | llama.cpp | CPU/edge deployment, quantization focus |

**VectorForge alternatives:**

| Your Code | Production Alternative | When to Use Each |
|-----------|----------------------|------------------|
| VectorForge | Qdrant | Rust-based, great filtering, self-hosted or cloud |
| VectorForge | Milvus | Scalable, GPU-accelerated search |
| VectorForge | Pinecone | Fully managed, zero ops |
| VectorForge | pgvector | PostgreSQL extension, simpler deployment |

**What to keep:** Your understanding of HNSW internals, SIMD optimization, and distributed search patterns.

**Abstraction pattern:**
```rust
// VectorStore trait allows swapping backends
#[async_trait]
pub trait VectorStore {
    async fn insert(&self, id: &str, vector: &[f32], metadata: Value) -> Result<()>;
    async fn search(&self, vector: &[f32], top_k: usize, filter: Option<Filter>) -> Result<Vec<SearchResult>>;
    async fn delete(&self, id: &str) -> Result<()>;
}

// Your implementation
pub struct VectorForge { /* your HNSW */ }

// Production wrappers
pub struct QdrantClient { /* calls Qdrant API */ }
pub struct PgVectorClient { /* uses PostgreSQL */ }

impl VectorStore for VectorForge { ... }
impl VectorStore for QdrantClient { ... }
impl VectorStore for PgVectorClient { ... }
```

**Inference abstraction:**
```go
// InferenceBackend allows swapping engines
type InferenceBackend interface {
    Generate(ctx context.Context, prompt string, params GenerateParams) (string, error)
    Embed(ctx context.Context, text string) ([]float32, error)
}

type TinyInferClient struct { /* your engine */ }
type VLLMClient struct { /* calls vLLM */ }
type OpenAIClient struct { /* calls OpenAI API */ }
```

---

## Phase 3: TinyKV (Distributed Consensus)

**Language:** Rust

**Goal:** Raft consensus, distributed coordination.

### Step 3.1: Core Consensus

| Topic | Deliverable |
|-------|-------------|
| Single-node KV | Log-structured storage, basic API |
| Raft leader election | Timeouts, voting |
| Raft log replication | AppendEntries, consistency |
| Raft persistence | Log persistence, snapshots |
| Linearizable reads | Read index, lease reads |
| Transactions | Simple distributed transactions |

**Milestone:** 3-node cluster surviving leader failures.

### Step 3.2: Advanced Features

| Topic | Deliverable |
|-------|-------------|
| MVCC storage | Multi-version concurrency control |
| Distributed transactions | 2PC coordinator |
| Watch/subscribe | Real-time config updates |
| Range queries | Efficient key range scans |
| Performance tuning | Batching, pipelining |
| Client library | Go, Rust, Python clients |

**Milestone:** Can replace etcd for basic coordination use cases.

**Key Integration:**
```go
// ModelHub uses TinyKV for config
type ModelHub struct {
    configStore *tinykv.Client
}

func (m *ModelHub) GetModelConfig(id string) (*ModelConfig, error) {
    data, err := m.configStore.Get("/models/" + id + "/config")
    // Strongly consistent read from TinyKV
}
```

### Production Integration: Distributed KV

| Your Code | Production Alternative | When to Use Each |
|-----------|----------------------|------------------|
| TinyKV | etcd | Kubernetes standard, battle-tested, great tooling |
| TinyKV | Consul | Service mesh integration, health checks |
| TinyKV | FoundationDB | Massive scale, ACID transactions |
| TinyKV | Redis (with Raft) | Simpler ops, less consistency guarantees |

**What to keep:** Deep understanding of Raft, consensus protocols, and distributed systems debugging.

**Abstraction pattern:**
```go
// ConfigStore interface allows swapping backends
type ConfigStore interface {
    Get(key string) ([]byte, error)
    Put(key string, value []byte) error
    Delete(key string) error
    Watch(prefix string) <-chan WatchEvent
}

type TinyKVClient struct { /* your implementation */ }
type EtcdClient struct { /* uses etcd */ }
type ConsulClient struct { /* uses Consul */ }

// ModelHub doesn't care which backend
type ModelHub struct {
    config ConfigStore  // Can be TinyKV, etcd, or Consul
}
```

---

## Phase 4: ModelHub (ML Platform)

**Language:** Go

**Goal:** Orchestrate TinyInfer and VectorForge.

### Step 4.1: Core Platform

| Topic | Deliverable |
|-------|-------------|
| Model registry | Store model metadata in TinyKV/MiniDB |
| Deployment API | Create/update/delete model deployments |
| Traffic routing | Route requests to TinyInfer instances |
| A/B testing | Split traffic between model versions |
| Canary deployments | Gradual rollouts |
| Observability | Metrics, logging, tracing |

**Milestone:** Deploy models, route traffic, run A/B tests.

**Key Integration:**
```go
// ModelHub routes to TinyInfer
func (m *ModelHub) Infer(ctx context.Context, req *InferRequest) (*InferResponse, error) {
    // Get routing config from TinyKV
    routing := m.getRouting(req.ModelID)

    // Select backend (A/B test, canary, etc.)
    backend := routing.SelectBackend(req)

    // Call TinyInfer
    return m.tinyInferClient.Infer(ctx, backend, req)
}

// ModelHub integrates RAG with VectorForge
func (m *ModelHub) RAG(ctx context.Context, req *RAGRequest) (*RAGResponse, error) {
    // Search VectorForge
    contexts := m.vectorForge.Search(req.Query, req.TopK)

    // Augment and call TinyInfer
    augmented := m.buildPrompt(req.Query, contexts)
    return m.tinyInferClient.Generate(ctx, augmented)
}
```

---

## Phase 5: Launchpad (Kubernetes Deployment)

**Language:** Go

**Goal:** Kubernetes operators for the full stack.

### Step 5.1: Operators

| Topic | Deliverable |
|-------|-------------|
| K8s operator basics | Custom resources, controllers |
| TinyInfer operator | Deploy/scale inference pods |
| VectorForge operator | Stateful set management |
| TinyKV operator | Raft cluster lifecycle |
| ModelHub operator | Full stack deployment |
| End-to-end demo | Complete RAG pipeline on K8s |

**Milestone:** Single `kubectl apply` deploys entire AI platform.

```yaml
apiVersion: platform.dev/v1
kind: AIStack
metadata:
  name: production
spec:
  tinykv:
    replicas: 3
  vectorforge:
    replicas: 2
    storage: 100Gi
  tinyinfer:
    replicas: 5
    model: llama-7b
    gpu: nvidia-a100
  modelhub:
    replicas: 3
```

### Phase 5 Checkpoint

By now you have:
- [x] TinyKernels (GPU primitives)
- [x] TinyInfer (inference engine)
- [x] VectorForge (vector database)
- [x] TinyKV (distributed KV with Raft)
- [x] ModelHub (ML platform)
- [x] Launchpad/Operators (Kubernetes deployment)

**You have built an AI inference platform from scratch.**

### Production Integration: ML Platform & Orchestration

**ModelHub alternatives:**

| Your Code | Production Alternative | When to Use Each |
|-----------|----------------------|------------------|
| ModelHub | KServe | Standard K8s model serving, good ecosystem |
| ModelHub | Seldon Core | Enterprise features, A/B testing |
| ModelHub | BentoML | Simpler deployment, good DX |
| ModelHub | Ray Serve | Python-native, good for ML teams |

**What to keep:** ModelHub is actually worth keeping—it's your orchestration layer that ties everything together. The alternatives are less flexible for custom RL training workflows.

**Launchpad alternatives:**

| Your Code | Production Alternative | When to Use Each |
|-----------|----------------------|------------------|
| Custom operators | Helm charts | Simpler deployment, less automation |
| Custom operators | Existing operators | Use vLLM operator, Qdrant operator, etc. |

**Recommended hybrid approach:**
```yaml
# Use production services for commodity infrastructure
apiVersion: platform.dev/v1
kind: AIStack
spec:
  # Production services (swap in for your implementations)
  vectorStore:
    type: qdrant  # Instead of VectorForge
    endpoint: qdrant.svc.cluster.local:6334

  kvStore:
    type: etcd  # Instead of TinyKV
    endpoints: ["etcd-0:2379", "etcd-1:2379", "etcd-2:2379"]

  inference:
    type: vllm  # Instead of TinyInfer
    model: meta-llama/Llama-2-7b

  # Keep your orchestration layer
  modelHub:
    type: custom  # Your ModelHub
    replicas: 3

  # Keep your RL environment infrastructure (Phases 6-9)
  envRuntime:
    type: custom  # Your EnvRuntime
    replicas: 10
```

---

## Phase 6: WorldGen (Synthetic Data Generation)

**Language:** Rust

**Goal:** Generate realistic, internally consistent world data for RL environments.

### Why This Is Your Differentiator

Phases 6-9 (WorldGen, InterfaceGen, TaskForge, EnvRuntime) are where you build **unique value**:

| Component | Why It's Hard to Buy |
|-----------|---------------------|
| WorldGen | No off-the-shelf solution for generating consistent synthetic worlds |
| InterfaceGen | Custom to your environment needs |
| TaskForge | Task generation with verifiers is novel |
| EnvRuntime | Integration with your specific stack |

**This is where startups are raising money.** The infrastructure in Phases 1-5 is commoditized. RL environment generation is the frontier.

### The Challenge

From industry research on RL environment startups:

| Challenge | Why It's Hard |
|-----------|---------------|
| **Realistic data** | Vibe-coding a website is easy; generating coherent users, realistic timestamps, logical entity relationships is hard |
| **Connected environments** | Real workflows span multiple apps (email + calendar + ticketing) with shared underlying data |
| **Multiple interfaces** | Same environment needs web UI, MCP/tools, and API interfaces |
| **Robust verifiers** | Knowing if an agent completed a task correctly requires ground truth |
| **Scale vs cost** | Large environments enable complex tasks but cost more; small ones are cheap but limited |

### Step 6.1: Core Generation

| Topic | Deliverable |
|-------|-------------|
| Entity schemas | Define users, orgs, permissions, relationships |
| "Rules of the world" | Constraints that keep data consistent |
| Temporal consistency | Realistic timestamps, event ordering |
| Cross-entity relationships | Tickets reference users, emails reference meetings |
| Seed data expansion | Human seeds → synthetic expansion |
| Integration with MiniDB | Store world state in your database |

**Milestone:** Generate 10K realistic users with 100K tickets, emails, and calendar events that are internally consistent.

**Key Concept - Rules of the World:**
```rust
// WorldGen rules ensure consistency
let world = WorldGen::new()
    .add_entity::<User>(UserConfig {
        roles: vec!["customer", "agent", "manager"],
        distribution: [0.8, 0.15, 0.05],
    })
    .add_entity::<Ticket>(TicketConfig {
        states: vec!["open", "in_progress", "escalated", "resolved"],
        sla_rules: SLARules::default(),
    })
    .add_rule(|world| {
        // Tickets created by customers, assigned to agents/managers
        world.tickets.iter().all(|t| {
            world.users[t.created_by].role == "customer" &&
            world.users[t.assigned_to].role != "customer"
        })
    })
    .add_rule(|world| {
        // Escalated tickets have manager involvement
        world.tickets.iter()
            .filter(|t| t.state == "escalated")
            .all(|t| t.comments.iter().any(|c|
                world.users[c.author].role == "manager"
            ))
    })
    .generate(scale: 10_000);
```

---

## Phase 7: InterfaceGen (Multi-Interface Environments)

**Language:** Rust + TypeScript

**Goal:** Same data, multiple ways to interact (web, MCP, API).

### Step 7.1: Interface Generation

| Topic | Deliverable |
|-------|-------------|
| Schema-driven generation | Define interface from entity schemas |
| Web UI generation | React components from schemas |
| MCP tool generation | Tool definitions from schemas |
| REST API generation | OpenAPI from schemas |
| Shared data layer | All interfaces read/write same state |
| Interface consistency | Same action via web = same result via MCP |

**Milestone:** Single schema generates web UI + MCP tools + REST API, all operating on shared state.

**Architecture:**
```
┌─────────────────────────────────────────┐
│              Entity Schema              │
│  (users, tickets, emails, calendar)     │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │  Web UI │ │   MCP   │ │   API   │
   │ (React) │ │ (Tools) │ │ (REST)  │
   └────┬────┘ └────┬────┘ └────┬────┘
        │           │           │
        └───────────┼───────────┘
                    ▼
        ┌─────────────────────┐
        │   Shared Data Layer │
        │  (MiniDB + TinyKV)  │
        └─────────────────────┘
```

---

## Phase 8: TaskForge (Task Generation & Verification)

**Language:** Rust

**Goal:** Generate tasks and verify agent completions.

### Step 8.1: Task Engine

| Topic | Deliverable |
|-------|-------------|
| Task templates | Define task structures (goal, constraints, expected outcome) |
| Task generation from world state | "Given this world, what tasks make sense?" |
| Ground truth computation | Know the correct answer before agent tries |
| Verifier implementation | Did the agent achieve the goal? |
| Complexity calibration | Simple (mechanistic) vs complex (reasoning-heavy) |
| Cross-interface tasks | Tasks requiring web AND MCP (teaching interface selection) |

**Milestone:** Generate 1000 tasks with verifiers, ranging from simple to complex.

**Task Complexity Spectrum:**
```
Level 1 - Mechanistic:
  "Change the status of ticket #1234 to 'resolved'"
  → Simple action, teaches tool usage

Level 2 - Multi-step:
  "Find all tickets from user X and add a comment to each"
  → Requires search + iteration

Level 3 - Reasoning:
  "Identify tickets likely to breach SLA and prioritize by business impact"
  → Requires understanding SLA rules, computing deadlines, reasoning about priority

Level 4 - Cross-app:
  "Schedule a meeting with the ticket assignee based on their calendar availability"
  → Requires ticketing system + calendar integration

Level 5 - Cross-interface:
  "Export the report via API, then verify it appears correctly on the web dashboard"
  → Teaches when to use which interface
```

---

## Phase 9: EnvRuntime (Hosted Execution)

**Language:** Go

**Goal:** Run environments at scale with proper isolation.

### Step 9.1: Runtime

| Topic | Deliverable |
|-------|-------------|
| Environment containerization | Docker images for environments |
| State snapshotting | Save/restore environment state |
| Episode management | Reset, run, collect trajectories |
| Parallel execution | Run 100s of episodes concurrently |
| Observability | Logging, metrics, action traces |
| Integration with Launchpad | K8s operators for environment clusters |

**Milestone:** Run 1000 parallel episodes, collect trajectories for training.

**Episode Flow:**
```go
// EnvRuntime manages episode lifecycle
func (r *Runtime) RunEpisode(env Environment, agent Agent, task Task) *Trajectory {
    // Snapshot initial state
    snapshot := env.Snapshot()

    trajectory := &Trajectory{Task: task}

    for step := 0; step < maxSteps; step++ {
        // Agent observes and acts
        observation := env.Observe()
        action := agent.Act(observation)  // Calls TinyInfer

        // Environment executes action
        result := env.Step(action)
        trajectory.Add(observation, action, result)

        // Check task completion
        if task.Verifier.Check(env.State()) {
            trajectory.Success = true
            break
        }
    }

    // Restore for next episode
    env.Restore(snapshot)

    return trajectory
}
```

### Final Checkpoint

By now you have:
- [x] TinyKernels (GPU primitives)
- [x] TinyInfer (inference engine)
- [x] VectorForge (vector database)
- [x] TinyKV (distributed KV with Raft)
- [x] ModelHub (ML platform)
- [x] Launchpad (Kubernetes deployment)
- [x] WorldGen (synthetic data with rules)
- [x] InterfaceGen (web + MCP + API from schemas)
- [x] TaskForge (task generation and verification)
- [x] EnvRuntime (hosted execution at scale)

**You can run models AND generate training data for them.**

The complete loop:
```
WorldGen → generates realistic world data
     ↓
InterfaceGen → creates environment interfaces
     ↓
TaskForge → generates tasks with verifiers
     ↓
EnvRuntime → runs agent episodes
     ↓
Trajectories → training data for RL
     ↓
Train model → (external, or future work)
     ↓
TinyInfer → serves the improved model
     ↓
ModelHub → deploys to production
```

### Production Strategy Summary

| Component | Build for Learning | Production Recommendation |
|-----------|-------------------|--------------------------|
| TinyKernels | ✅ Yes | Keep for custom ops, use cuBLAS/FlashAttention for standard |
| TinyInfer | ✅ Yes | Use vLLM/TensorRT-LLM, contribute optimizations upstream |
| VectorForge | ✅ Yes | Use Qdrant/Milvus/pgvector |
| TinyKV | ✅ Yes | Use etcd/Consul |
| MiniDB | ✅ Yes | Use PostgreSQL |
| ModelHub | ✅ Yes | **Keep** - your orchestration layer |
| Launchpad | ✅ Yes | **Keep** - customized for your stack |
| WorldGen | ✅ Yes | **Keep** - your differentiator |
| InterfaceGen | ✅ Yes | **Keep** - your differentiator |
| TaskForge | ✅ Yes | **Keep** - your differentiator |
| EnvRuntime | ✅ Yes | **Keep** - your differentiator |

**The pattern:**
- Phases 1-3: Build to learn, swap for production
- Phases 4-5: Build to learn, consider keeping
- Phases 6-9: Build to keep - this is your unique value

---

## Optional: MiniDB (Anytime After Phase 2)

MiniDB (C++ SQL database) is valuable but not on the critical path. Add it when you want:

- Structured model registry with SQL queries
- Audit logging with complex queries
- User/tenant management

It can replace TinyKV for some use cases, or complement it (TinyKV for coordination, MiniDB for structured data).

**Production alternative:** PostgreSQL, CockroachDB, or managed services like Supabase/PlanetScale. Build MiniDB to understand storage engines, B+ trees, and query execution—then use PostgreSQL in production.

---

## Integration Architecture

### Data Flow

```
User Request
     │
     ▼
┌─────────┐     ┌─────────┐
│ModelHub │────►│ TinyKV  │  (routing config, feature flags)
└────┬────┘     └─────────┘
     │
     ▼
┌──────────┐    ┌─────────────┐
│TinyInfer │───►│ TinyKernels │  (GPU compute)
└────┬─────┘    └─────────────┘
     │
     ▼ (for RAG)
┌───────────┐
│VectorForge│  (embedding search)
└───────────┘
```

### API Contracts

Define these early so components can develop in parallel:

**TinyKernels → TinyInfer:**
```cpp
namespace tinykernels {
    void gemm(const float* A, const float* B, float* C,
              int M, int N, int K, cudaStream_t stream);

    void flash_attention(const float* Q, const float* K, const float* V,
                         float* O, int batch, int heads, int seq_len, int dim,
                         cudaStream_t stream);
}
```

**TinyInfer → ModelHub (gRPC):**
```protobuf
service InferenceService {
    rpc Infer(InferRequest) returns (InferResponse);
    rpc Generate(GenerateRequest) returns (stream GenerateResponse);
    rpc Embed(EmbedRequest) returns (EmbedResponse);
}
```

**VectorForge → ModelHub (gRPC):**
```protobuf
service VectorService {
    rpc Insert(InsertRequest) returns (InsertResponse);
    rpc Search(SearchRequest) returns (SearchResponse);
    rpc Delete(DeleteRequest) returns (DeleteResponse);
}
```

**TinyKV → Everyone (gRPC):**
```protobuf
service KVService {
    rpc Get(GetRequest) returns (GetResponse);
    rpc Put(PutRequest) returns (PutResponse);
    rpc Delete(DeleteRequest) returns (DeleteResponse);
    rpc Watch(WatchRequest) returns (stream WatchResponse);
}
```

**EnvRuntime → Training (gRPC):**
```protobuf
service EnvironmentService {
    rpc CreateEnvironment(CreateEnvRequest) returns (Environment);
    rpc RunEpisode(EpisodeRequest) returns (Trajectory);
    rpc RunBatch(BatchRequest) returns (stream Trajectory);
}
```

---

## Parallel Workstreams

Some components can be built in parallel:

```
Phase 1:       TinyKernels (must be first)
                    │
Phase 2:   ┌────────┴────────┐
           ▼                 ▼
       TinyInfer        VectorForge
           │                 │
Phase 3:   └────────┬────────┘
                    ▼
                 TinyKV
                    │
Phase 4:        ModelHub
                    │
Phase 5:        Launchpad
                    │
Phase 6-9:  ┌───────┴───────┐
            ▼               ▼
        WorldGen      InterfaceGen
            │               │
            └───────┬───────┘
                    ▼
               TaskForge
                    │
                    ▼
               EnvRuntime
```

With a team, TinyInfer and VectorForge can be built simultaneously since they only share TinyKernels.

---

## Skills Acquired

By the end, you will have deep experience in:

| Area | Projects | Skills |
|------|----------|--------|
| **GPU Programming** | TinyKernels | CUDA, memory hierarchy, Tensor Cores, profiling |
| **C++** | TinyInfer, MiniDB | RAII, templates, performance optimization |
| **Rust** | VectorForge, TinyKV, WorldGen, TaskForge | Ownership, async, distributed systems |
| **Go** | ModelHub, Launchpad, EnvRuntime | Concurrency, K8s operators, production systems |
| **Distributed Systems** | TinyKV, VectorForge | Raft, replication, consistency |
| **ML Systems** | All of them | Inference, embeddings, RAG, model serving |
| **Infrastructure** | Launchpad | Kubernetes, operators, deployment |
| **RL Infrastructure** | WorldGen, TaskForge, EnvRuntime | Synthetic data, environments, training loops |

---

## Milestones & Demos

Plan demos to validate progress:

| Phase | Demo |
|-------|------|
| 1 | "Here's my GEMM beating naive by 50x, here's the profiler data" |
| 1 | "Here's FlashAttention in PyTorch using my kernels" |
| 2 | "Here's LLaMA-7B running on my inference engine" |
| 2 | "Here's 1M vectors searchable in <10ms" |
| 3 | "Here's a 3-node Raft cluster surviving failures" |
| 5 | "Here's a complete RAG pipeline on Kubernetes, all my code" |
| 9 | "Here's an agent training on environments I generated" |

---

## Reading Schedule

Interleave reading with building:

| Phase | Primary Reading |
|-------|-----------------|
| 1 | CUDA by Example, PMPP, CUTLASS code, FlashAttention papers |
| 2 (TinyInfer) | Effective C++, LLVM/MLIR for optimization |
| 2 (VectorForge) | Rust Atomics, async Rust, HNSW paper |
| 3 | Raft paper, DDIA |
| 4-5 | K8s operator patterns, SRE book |
| 6-9 | RL environment papers, synthetic data generation |

---

## Getting Unstuck

When blocked:

1. **Read reference implementations** - CUTLASS, etcd, Qdrant, vLLM
2. **Simplify** - Cut scope, get something working, iterate
3. **Profile** - Data beats intuition
4. **Ask** - GPU MODE Discord, Reddit, Stack Overflow
5. **Skip and return** - Some concepts click after you've built more

---

## The Honest Truth

This is ambitious. You won't finish everything perfectly.

**What matters:**
- Depth over breadth—it's better to deeply understand GEMM than superficially build everything
- Working code over perfect code—ship, then iterate
- Integration over isolation—the value is in connecting the pieces

**What you'll actually learn:**
- How computers actually work, from transistors to Kubernetes
- How to debug anything
- How to read and understand complex codebases
- How to design systems that work

By the end, you won't just be a "cracked developer"—you'll be someone who can build AI infrastructure from scratch.

---

*Generated: January 2026*
