# Becoming Cracked at AI Infrastructure

A comprehensive guide to mastering the systems that power modern AI - inference engines, vector databases, and ML platforms.

---

## Table of Contents

1. [Why AI Infrastructure](#why-ai-infrastructure)
2. [The AI Infra Stack](#the-ai-infra-stack)
3. [Core Mental Models](#core-mental-models)
4. [Books & Papers: The Foundation](#books--papers-the-foundation)
5. [The Three-Language Path](#the-three-language-path)
6. [Project 1: Vector Database (Rust)](#project-1-vector-database-rust)
7. [Project 2: Inference Engine (C++)](#project-2-inference-engine-c)
8. [Project 3: ML Platform (Go)](#project-3-ml-platform-go)
9. [How The Projects Connect](#how-the-projects-connect)
10. [Tools & Technologies](#tools--technologies)
11. [Learning Resources](#learning-resources)
12. [18-Month Schedule](#18-month-schedule)
13. [Career Paths](#career-paths)

---

## Why AI Infrastructure

AI infrastructure is the systems layer that makes machine learning work at scale. While data scientists build models, AI infrastructure engineers build the systems that:

- **Train models** on thousands of GPUs
- **Serve models** with millisecond latency
- **Store and search** billions of vectors
- **Manage** the lifecycle of models in production
- **Optimize** inference to run on any hardware

This is where systems programming meets machine learning. You don't need to be an ML researcher, but you need to understand enough ML to build systems that serve it well.

**Who's hiring:**
- Big Tech: Google (TensorFlow, TPUs), Meta (PyTorch), OpenAI, Anthropic
- AI-native companies: Hugging Face, Weights & Biases, Anyscale, Modal
- Vector DB companies: Pinecone, Weaviate, Qdrant, Chroma
- Every company deploying LLMs

**Why these three languages:**
- **C++**: The language of inference engines, GPU kernels, and performance-critical paths
- **Rust**: Rising fast for vector databases, tokenizers, and safe systems code
- **Go**: The language of ML platforms, orchestration, and Kubernetes-native tooling

---

## The AI Infra Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           User Applications                              │
│                    Chat, Search, Recommendations, Agents                 │
├─────────────────────────────────────────────────────────────────────────┤
│                           ML Platform Layer                              │
│         Model Registry │ Experiment Tracking │ Feature Store            │
│              Deployment │ A/B Testing │ Monitoring                      │
│                              (Go, Python)                                │
├─────────────────────────────────────────────────────────────────────────┤
│                          Model Serving Layer                             │
│           Inference Servers │ Batching │ Caching │ Routing              │
│                         (C++, Rust, Python)                              │
├─────────────────────────────────────────────────────────────────────────┤
│                          Inference Runtime                               │
│        Graph Execution │ Operator Kernels │ Memory Management           │
│              Quantization │ Optimization │ Hardware Abstraction          │
│                              (C++, CUDA)                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                          Vector Storage                                  │
│          Embedding Store │ ANN Search │ Filtering │ Replication         │
│                              (Rust, C++)                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                          Training Infra                                  │
│       Distributed Training │ Checkpointing │ Data Loading               │
│                          (Python, C++, CUDA)                             │
├─────────────────────────────────────────────────────────────────────────┤
│                            Hardware                                      │
│                    GPUs │ TPUs │ CPUs │ Custom ASICs                    │
└─────────────────────────────────────────────────────────────────────────┘
```

This track focuses on three key layers:
1. **Vector Storage** (Rust) - Where embeddings live and are searched
2. **Inference Runtime** (C++) - Where models execute
3. **ML Platform** (Go) - Where models are managed and served

---

## Core Mental Models

### 1. Embeddings Are the Universal Interface

Modern AI compresses meaning into vectors. Text, images, audio, code - everything becomes a point in high-dimensional space.

```
"The cat sat on the mat" → [0.12, -0.34, 0.56, ..., 0.78]  # 768 or 1536 dimensions
[image of cat]           → [0.15, -0.31, 0.52, ..., 0.81]  # Similar vectors!
```

**Implications:**
- Similarity = distance in vector space (cosine, euclidean, dot product)
- Search becomes "find nearest neighbors"
- This is why vector databases are essential infrastructure

### 2. Inference Is Just Matrix Math (Mostly)

Neural networks are compositions of:
- Matrix multiplications (attention, linear layers)
- Element-wise operations (activations, normalization)
- Reductions (softmax, pooling)

```
# Simplified transformer attention
Q, K, V = input @ W_q, input @ W_k, input @ W_v  # MatMul
scores = Q @ K.T / sqrt(d)                        # MatMul + scale
weights = softmax(scores)                         # Reduction
output = weights @ V                              # MatMul
```

**Implications:**
- Optimize MatMul, optimize everything (BLAS, cuBLAS, custom kernels)
- Memory bandwidth often matters more than compute
- Batching amortizes overhead

### 3. The Memory Hierarchy Dominates

```
Register:     ~1 cycle      ~KB
L1 Cache:     ~4 cycles     ~64KB
L2 Cache:     ~12 cycles    ~256KB
L3 Cache:     ~40 cycles    ~MB
RAM:          ~200 cycles   ~GB
GPU HBM:      ~300 cycles   ~GB (but massive bandwidth)
SSD:          ~10K cycles   ~TB
Network:      ~1M cycles    ~∞
```

**Implications:**
- Keep hot data close (KV cache, embedding cache)
- Batch to amortize memory transfers
- Quantization shrinks memory footprint (INT8 = 4x smaller than FP32)

### 4. Latency vs Throughput Trade-offs

| Optimize for | Strategy |
|--------------|----------|
| **Latency** (real-time) | Small batches, speculative execution, caching |
| **Throughput** (batch) | Large batches, continuous batching, queuing |

Most systems need both: low p50 latency AND high throughput.

### 5. Approximate Is Usually Good Enough

Exact nearest neighbor search is O(n). Approximate (ANN) is O(log n) or O(1).

```
Exact:       Compare query to all 1 billion vectors
HNSW:        Navigate a graph, compare ~100-1000 vectors
Quantized:   Compress vectors, compare even faster
```

**Recall@10 of 0.95** means you find 95% of the true top-10. Usually acceptable.

### 6. Models Are Graphs, Execution Is Scheduling

A neural network is a directed acyclic graph (DAG) of operations:

```
Input → Embedding → [Attention → FFN] × N → Output
```

Execution is:
1. Memory allocation (where do tensors live?)
2. Operator scheduling (what runs when?)
3. Kernel dispatch (which implementation?)

Optimizations: operator fusion, memory planning, parallel execution.

### 7. Quantization: Trade Precision for Speed

```
FP32:  32 bits, full precision
FP16:  16 bits, 2x memory savings, ~same accuracy
INT8:   8 bits, 4x memory savings, <1% accuracy loss
INT4:   4 bits, 8x memory savings, ~1-3% accuracy loss
```

LLMs at INT4 can run on consumer GPUs. This is why llama.cpp exists.

---

## Books & Papers: The Foundation

### Machine Learning Fundamentals

| Resource | Focus | When |
|----------|-------|------|
| **"Deep Learning"** by Goodfellow, Bengio, Courville | ML foundations | First, for context |
| **"Attention Is All You Need"** (paper) | Transformers | Essential |
| **"Neural Networks and Deep Learning"** (online, Nielsen) | Intuition | Good intro |
| **Fast.ai courses** | Practical ML | If new to ML |

### Systems for ML

| Resource | Focus | When |
|----------|-------|------|
| **"Machine Learning Systems"** by Chip Huyen | ML systems design | Essential |
| **"Efficient Deep Learning"** (MIT course) | Optimization, quantization | After basics |
| **MLSys Conference Papers** | Research frontier | Ongoing |

### Infrastructure

| Resource | Focus | When |
|----------|-------|------|
| **"Designing Data-Intensive Applications"** | Distributed systems | Essential |
| **"Database Internals"** by Petrov | Storage engines | For vector DB |
| **"Computer Systems: A Programmer's Perspective"** | Systems fundamentals | Early |

### Key Papers

| Paper | Topic |
|-------|-------|
| **"Efficient Estimation of Word Representations"** (Word2Vec) | Embeddings origin |
| **"Billion-scale similarity search with GPUs"** (FAISS) | ANN search |
| **"Efficient and Robust Approximate Nearest Neighbor Search"** (HNSW) | Graph-based ANN |
| **"Megatron-LM"** | Distributed training |
| **"FlashAttention"** | Efficient attention |
| **"LLM.int8()"** | Quantization |
| **"Continuous Batching"** (Orca) | Inference optimization |
| **"PagedAttention"** (vLLM) | Memory-efficient serving |

---

## The Three-Language Path

This track uses all three languages, each for what it does best:

```
Month 1-6:    Rust     → Vector Database (VectorForge)
Month 7-12:   C++      → Inference Engine (TinyInfer)
Month 13-18:  Go       → ML Platform (ModelHub)
```

**Why this order:**

1. **Rust first**: Vector databases are the "hello world" of AI infra. You'll learn embeddings, similarity search, and storage - concepts used everywhere. Rust's safety helps when building complex data structures.

2. **C++ second**: Now you understand what embeddings are and how they're used. C++ lets you build the inference engine that *produces* those embeddings. Harder, but you have context.

3. **Go third**: With storage and inference understood, you build the platform that orchestrates everything. Go's simplicity lets you focus on the MLOps patterns.

By the end, you'll have built the full stack.

---

## Project 1: Vector Database (Rust)

**Project Name:** VectorForge

**What you're building:** A vector similarity search engine like Qdrant, Milvus, or Pinecone.

### Why This Project

Vector databases are essential for:
- Semantic search
- Retrieval-Augmented Generation (RAG)
- Recommendation systems
- Similarity matching

They combine classic database concepts (storage, indexing, queries) with ML-specific needs (high-dimensional vectors, approximate search).

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        VectorForge                               │
├─────────────────────────────────────────────────────────────────┤
│  REST API            │  gRPC API           │  Python Client     │
├─────────────────────────────────────────────────────────────────┤
│                      Query Engine                                │
│  Vector Search       │  Filtering          │  Hybrid Search     │
├─────────────────────────────────────────────────────────────────┤
│                      Index Layer                                 │
│  HNSW Index          │  IVF Index          │  Flat Index        │
├─────────────────────────────────────────────────────────────────┤
│                      Storage Layer                               │
│  Vector Storage      │  Payload Storage    │  WAL               │
├─────────────────────────────────────────────────────────────────┤
│                      Cluster Layer                               │
│  Sharding            │  Replication        │  Consensus         │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 1: Vector Storage (Month 1)

**Build:** Efficient storage for high-dimensional vectors

**Features:**
- Memory-mapped vector storage
- SIMD-accelerated distance calculations (cosine, euclidean, dot)
- Basic CRUD operations
- Point queries (get vector by ID)

**Core Types:**

```rust
use std::simd::f32x8;

#[derive(Clone, Copy)]
pub enum Distance {
    Cosine,
    Euclidean,
    DotProduct,
}

pub struct VectorStorage {
    vectors: memmap2::MmapMut,  // Memory-mapped file
    dimensions: usize,
    count: usize,
}

impl VectorStorage {
    pub fn new(path: &Path, dimensions: usize) -> Result<Self>;

    pub fn insert(&mut self, id: u64, vector: &[f32]) -> Result<()>;
    pub fn get(&self, id: u64) -> Option<&[f32]>;
    pub fn delete(&mut self, id: u64) -> Result<bool>;

    // SIMD-accelerated distance
    pub fn distance(&self, a: &[f32], b: &[f32], metric: Distance) -> f32;

    // Brute-force search (baseline)
    pub fn search_brute(&self, query: &[f32], k: usize) -> Vec<(u64, f32)>;
}

// SIMD dot product
#[inline]
fn dot_product_simd(a: &[f32], b: &[f32]) -> f32 {
    let chunks = a.len() / 8;
    let mut sum = f32x8::splat(0.0);

    for i in 0..chunks {
        let va = f32x8::from_slice(&a[i * 8..]);
        let vb = f32x8::from_slice(&b[i * 8..]);
        sum += va * vb;
    }

    sum.reduce_sum() + a[chunks * 8..].iter()
        .zip(&b[chunks * 8..])
        .map(|(x, y)| x * y)
        .sum::<f32>()
}
```

**Skills:** Memory mapping, SIMD, binary file formats

---

### Phase 2: HNSW Index (Month 2)

**Build:** Hierarchical Navigable Small World graph for fast ANN search

**Features:**
- Multi-layer graph structure
- Configurable M (connections per node) and ef (search width)
- Incremental insertion
- Concurrent search

**Core Types:**

```rust
pub struct HnswConfig {
    pub m: usize,              // Max connections per layer
    pub m_max_0: usize,        // Max connections at layer 0
    pub ef_construction: usize, // Search width during construction
    pub ml: f64,               // Level multiplier
}

pub struct HnswIndex {
    config: HnswConfig,
    layers: Vec<GraphLayer>,
    entry_point: Option<NodeId>,
    max_level: usize,
}

struct GraphLayer {
    // Adjacency list for each node
    neighbors: Vec<Vec<NodeId>>,
}

impl HnswIndex {
    pub fn new(config: HnswConfig) -> Self;

    // Insert a vector, returns node ID
    pub fn insert(&mut self, id: u64, vector: &[f32]) -> NodeId;

    // Search for k nearest neighbors
    pub fn search(&self, query: &[f32], k: usize, ef: usize) -> Vec<(u64, f32)>;

    // Internal: select level for new node
    fn random_level(&self) -> usize;

    // Internal: search a single layer
    fn search_layer(
        &self,
        query: &[f32],
        entry_points: Vec<NodeId>,
        ef: usize,
        layer: usize,
    ) -> BinaryHeap<(OrderedFloat<f32>, NodeId)>;
}
```

**Algorithm sketch:**

```rust
fn search(&self, query: &[f32], k: usize, ef: usize) -> Vec<(u64, f32)> {
    let mut current_nearest = vec![self.entry_point.unwrap()];

    // Traverse from top layer down to layer 1
    for layer in (1..=self.max_level).rev() {
        current_nearest = self.search_layer(query, current_nearest, 1, layer);
    }

    // Search layer 0 with ef candidates
    let candidates = self.search_layer(query, current_nearest, ef, 0);

    // Return top k
    candidates.into_iter().take(k).collect()
}
```

**Reading:**
- "Efficient and Robust Approximate Nearest Neighbor Search Using HNSW" paper
- Qdrant's HNSW implementation

---

### Phase 3: Filtering & Payloads (Month 3)

**Build:** Metadata storage and filtered search

**Features:**
- Arbitrary JSON payloads per vector
- Indexed fields for fast filtering
- Pre-filtering and post-filtering strategies
- Range, equality, and set membership filters

**Core Types:**

```rust
use serde_json::Value;

pub struct Payload {
    pub fields: HashMap<String, Value>,
}

pub enum Filter {
    Equals { field: String, value: Value },
    Range { field: String, gte: Option<f64>, lte: Option<f64> },
    In { field: String, values: Vec<Value> },
    And(Vec<Filter>),
    Or(Vec<Filter>),
    Not(Box<Filter>),
}

pub struct PayloadIndex {
    // Inverted index for equality
    keyword_index: HashMap<String, HashMap<Value, RoaringBitmap>>,
    // Range index (B-tree style)
    numeric_index: HashMap<String, BTreeMap<OrderedFloat<f64>, RoaringBitmap>>,
}

impl PayloadIndex {
    pub fn filter(&self, filter: &Filter) -> RoaringBitmap;
}

// Search with filter
impl VectorForge {
    pub fn search(
        &self,
        query: &[f32],
        k: usize,
        filter: Option<Filter>,
    ) -> Vec<SearchResult> {
        let allowed_ids = filter.map(|f| self.payload_index.filter(&f));

        // Strategy 1: Pre-filter (if filter is selective)
        // Strategy 2: Post-filter (if filter is broad)
        // Strategy 3: ACORN-style filtered HNSW
    }
}
```

**Skills:** Inverted indexes, bitmap operations, query optimization

---

### Phase 4: Persistence & WAL (Month 4)

**Build:** Durability and crash recovery

**Features:**
- Write-ahead log for durability
- Periodic snapshots
- Crash recovery
- Compaction

**Core Types:**

```rust
pub enum WalEntry {
    InsertVector { id: u64, vector: Vec<f32>, payload: Option<Payload> },
    UpdatePayload { id: u64, payload: Payload },
    DeleteVector { id: u64 },
    Checkpoint { snapshot_id: u64 },
}

pub struct Wal {
    file: File,
    current_lsn: u64,
}

impl Wal {
    pub fn append(&mut self, entry: &WalEntry) -> Result<u64>;
    pub fn sync(&self) -> Result<()>;
    pub fn replay(&self) -> impl Iterator<Item = WalEntry>;
}

pub struct SnapshotManager {
    snapshot_dir: PathBuf,
}

impl SnapshotManager {
    pub fn create_snapshot(&self, collection: &Collection) -> Result<u64>;
    pub fn load_latest(&self) -> Result<Collection>;
    pub fn cleanup_old(&self, keep: usize) -> Result<()>;
}
```

---

### Phase 5: API & Collections (Month 5)

**Build:** REST/gRPC API and multi-collection support

**Features:**
- Collection management (create, delete, configure)
- Batch operations
- Scroll/pagination
- gRPC for performance, REST for ease

**Endpoints:**

```
# Collections
PUT    /collections/{name}          Create collection
DELETE /collections/{name}          Delete collection
GET    /collections/{name}          Get collection info

# Vectors
PUT    /collections/{name}/points   Upsert vectors
POST   /collections/{name}/search   Search vectors
GET    /collections/{name}/points/{id}  Get vector
DELETE /collections/{name}/points   Delete vectors

# Scroll
POST   /collections/{name}/scroll   Iterate all vectors
```

**gRPC for search:**

```protobuf
service VectorForge {
    rpc Search(SearchRequest) returns (SearchResponse);
    rpc BatchSearch(BatchSearchRequest) returns (stream SearchResponse);
    rpc Upsert(UpsertRequest) returns (UpsertResponse);
}

message SearchRequest {
    string collection = 1;
    repeated float vector = 2;
    uint32 limit = 3;
    Filter filter = 4;
}
```

---

### Phase 6: Distributed (Month 6)

**Build:** Sharding and replication

**Features:**
- Hash-based sharding
- Raft-based replication per shard
- Distributed search (scatter-gather)
- Node management

**Architecture:**

```
                    ┌─────────────┐
                    │   Router    │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  Shard 0    │ │  Shard 1    │ │  Shard 2    │
    │ (Primary)   │ │ (Primary)   │ │ (Primary)   │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
    ┌──────┴──────┐ ┌──────┴──────┐ ┌──────┴──────┐
    │  Replica    │ │  Replica    │ │  Replica    │
    └─────────────┘ └─────────────┘ └─────────────┘
```

**Skills:** Distributed systems, consistent hashing, scatter-gather

---

## Project 2: Inference Engine (C++)

**Project Name:** TinyInfer

**What you're building:** A neural network inference runtime like ONNX Runtime, TensorRT, or llama.cpp.

### Why This Project

Inference engines are where models meet hardware. You'll learn:
- How neural networks actually execute
- Memory management for tensors
- Operator implementations
- Hardware optimization (SIMD, GPU)

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         TinyInfer                                │
├─────────────────────────────────────────────────────────────────┤
│  Model Loading        │  ONNX Parser        │  Custom Format    │
├─────────────────────────────────────────────────────────────────┤
│                      Graph IR                                    │
│  Nodes (operators)    │  Edges (tensors)    │  Metadata         │
├─────────────────────────────────────────────────────────────────┤
│                      Optimization Passes                         │
│  Constant Folding     │  Operator Fusion    │  Memory Planning  │
├─────────────────────────────────────────────────────────────────┤
│                      Execution Engine                            │
│  Scheduler            │  Memory Allocator   │  Kernel Dispatch  │
├─────────────────────────────────────────────────────────────────┤
│                      Operator Kernels                            │
│  MatMul (BLAS)        │  Conv2D             │  Attention        │
│  Activations          │  Normalization      │  Elementwise      │
├─────────────────────────────────────────────────────────────────┤
│                      Backend                                     │
│  CPU (SIMD)           │  CUDA (optional)    │  Metal (optional) │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 1: Tensor Library (Month 7)

**Build:** N-dimensional array library with efficient memory

**Features:**
- N-dimensional tensors
- Multiple data types (float32, float16, int8)
- Strided views (no-copy slicing)
- Memory pooling
- BLAS integration

**Core Types:**

```cpp
enum class DType {
    Float32,
    Float16,
    Int8,
    Int32,
};

class Tensor {
public:
    Tensor(std::vector<int64_t> shape, DType dtype);

    // Accessors
    int64_t ndim() const { return shape_.size(); }
    int64_t size() const;  // Total elements
    int64_t size(int dim) const { return shape_[dim]; }
    const std::vector<int64_t>& shape() const { return shape_; }
    const std::vector<int64_t>& strides() const { return strides_; }
    DType dtype() const { return dtype_; }

    // Data access
    template<typename T>
    T* data() { return static_cast<T*>(data_.get()); }

    template<typename T>
    const T* data() const { return static_cast<const T*>(data_.get()); }

    // Views (no copy)
    Tensor view(std::vector<int64_t> new_shape) const;
    Tensor slice(int dim, int64_t start, int64_t end) const;
    Tensor transpose(int dim0, int dim1) const;

    // Contiguous copy
    Tensor contiguous() const;
    bool is_contiguous() const;

private:
    std::shared_ptr<void> data_;
    std::vector<int64_t> shape_;
    std::vector<int64_t> strides_;
    DType dtype_;
    int64_t offset_ = 0;
};

class TensorAllocator {
public:
    Tensor allocate(std::vector<int64_t> shape, DType dtype);
    void release(Tensor& tensor);

private:
    // Memory pool for reuse
    std::unordered_map<size_t, std::vector<std::shared_ptr<void>>> pool_;
};
```

**Skills:** Memory layout, RAII, template programming

---

### Phase 2: Operators (Month 8)

**Build:** Core neural network operations

**Operators to implement:**

| Category | Operators |
|----------|-----------|
| Linear | MatMul, Gemm, Linear |
| Activation | ReLU, GELU, SiLU, Sigmoid, Softmax |
| Normalization | LayerNorm, BatchNorm, RMSNorm |
| Elementwise | Add, Mul, Div, Pow |
| Shape | Reshape, Transpose, Concat, Split |
| Reduction | ReduceMean, ReduceSum, ReduceMax |
| Attention | ScaledDotProductAttention |

**Core Types:**

```cpp
class Operator {
public:
    virtual ~Operator() = default;

    virtual std::string name() const = 0;
    virtual std::vector<Tensor> forward(const std::vector<Tensor>& inputs) = 0;

    // Shape inference
    virtual std::vector<std::vector<int64_t>> infer_shapes(
        const std::vector<std::vector<int64_t>>& input_shapes) = 0;
};

class MatMul : public Operator {
public:
    std::string name() const override { return "MatMul"; }

    std::vector<Tensor> forward(const std::vector<Tensor>& inputs) override {
        const Tensor& a = inputs[0];
        const Tensor& b = inputs[1];

        // Use BLAS for performance
        Tensor output = allocate_output(a, b);
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    m, n, k,
                    1.0f,
                    a.data<float>(), k,
                    b.data<float>(), n,
                    0.0f,
                    output.data<float>(), n);
        return {output};
    }
};

class ScaledDotProductAttention : public Operator {
public:
    std::vector<Tensor> forward(const std::vector<Tensor>& inputs) override {
        // Q, K, V: [batch, heads, seq_len, head_dim]
        const Tensor& Q = inputs[0];
        const Tensor& K = inputs[1];
        const Tensor& V = inputs[2];

        // scores = Q @ K^T / sqrt(d)
        Tensor scores = matmul(Q, K.transpose(-2, -1));
        scale_inplace(scores, 1.0f / std::sqrt(head_dim_));

        // weights = softmax(scores)
        Tensor weights = softmax(scores, -1);

        // output = weights @ V
        return {matmul(weights, V)};
    }
};
```

**Skills:** BLAS integration, numerical stability, broadcasting

---

### Phase 3: Model Loading & Graph IR (Month 9)

**Build:** ONNX model parser and internal graph representation

**Features:**
- Parse ONNX protobuf
- Build computation graph
- Weight loading
- Graph validation

**Core Types:**

```cpp
struct NodeDef {
    std::string name;
    std::string op_type;
    std::vector<std::string> inputs;
    std::vector<std::string> outputs;
    std::unordered_map<std::string, Attribute> attributes;
};

class Graph {
public:
    void add_node(NodeDef node);
    void add_input(std::string name, std::vector<int64_t> shape, DType dtype);
    void add_initializer(std::string name, Tensor tensor);

    // Topological sort for execution order
    std::vector<NodeDef*> topological_order() const;

    // Get node by output name
    NodeDef* producer(const std::string& tensor_name) const;

private:
    std::vector<NodeDef> nodes_;
    std::unordered_map<std::string, Tensor> initializers_;
    std::vector<std::string> inputs_;
    std::vector<std::string> outputs_;
};

class OnnxLoader {
public:
    Graph load(const std::string& path);

private:
    Tensor load_tensor(const onnx::TensorProto& proto);
    NodeDef parse_node(const onnx::NodeProto& proto);
};
```

---

### Phase 4: Graph Optimization (Month 10)

**Build:** Optimization passes that transform the graph

**Optimizations:**

| Pass | Description |
|------|-------------|
| Constant folding | Evaluate ops with constant inputs at compile time |
| Dead code elimination | Remove unused nodes |
| Operator fusion | Combine MatMul+Add → Gemm, Conv+ReLU → ConvRelu |
| Memory planning | Reuse tensor memory when possible |
| Layout optimization | Choose optimal memory layout per operator |

**Core Types:**

```cpp
class OptimizationPass {
public:
    virtual ~OptimizationPass() = default;
    virtual std::string name() const = 0;
    virtual bool run(Graph& graph) = 0;  // Returns true if graph was modified
};

class ConstantFolding : public OptimizationPass {
public:
    std::string name() const override { return "ConstantFolding"; }

    bool run(Graph& graph) override {
        bool modified = false;
        for (auto& node : graph.nodes()) {
            if (all_inputs_constant(graph, node)) {
                // Execute node, replace with constant
                Tensor result = execute(node, graph);
                graph.add_initializer(node.outputs[0], result);
                graph.remove_node(node);
                modified = true;
            }
        }
        return modified;
    }
};

class FuseMatMulAdd : public OptimizationPass {
    bool run(Graph& graph) override {
        // Find MatMul -> Add patterns, replace with Gemm
    }
};

class MemoryPlanner : public OptimizationPass {
    bool run(Graph& graph) override {
        // Analyze tensor lifetimes, assign memory offsets
        // Tensors with non-overlapping lifetimes can share memory
    }
};

class PassManager {
public:
    void add_pass(std::unique_ptr<OptimizationPass> pass);
    void run(Graph& graph);

private:
    std::vector<std::unique_ptr<OptimizationPass>> passes_;
};
```

---

### Phase 5: Quantization (Month 11)

**Build:** INT8 inference for faster execution

**Features:**
- Post-training quantization
- Calibration for scale/zero-point
- INT8 operator kernels
- Mixed precision (some ops stay FP32)

**Core Types:**

```cpp
struct QuantizationParams {
    float scale;
    int32_t zero_point;
};

class Quantizer {
public:
    // Calibrate using sample data
    void calibrate(Graph& graph, const std::vector<Tensor>& calibration_data);

    // Quantize weights and activations
    Graph quantize(const Graph& graph);

private:
    // Per-tensor quantization parameters
    std::unordered_map<std::string, QuantizationParams> params_;

    // Observe activation ranges
    void observe(const std::string& tensor_name, const Tensor& tensor);

    // Calculate optimal scale/zero_point
    QuantizationParams calculate_params(float min_val, float max_val);
};

// Quantized operators use different kernels
class QuantizedMatMul : public Operator {
public:
    std::vector<Tensor> forward(const std::vector<Tensor>& inputs) override {
        // INT8 matrix multiplication
        // Output = scale_a * scale_b * (A_int8 @ B_int8)
    }
};
```

**Skills:** Quantization theory, numerical precision, calibration

---

### Phase 6: Execution Engine & Benchmarking (Month 12)

**Build:** High-performance execution and profiling

**Features:**
- Execution session management
- Kernel dispatch
- Memory allocation strategy
- Performance profiling
- Benchmark suite

**Core Types:**

```cpp
class ExecutionSession {
public:
    ExecutionSession(Graph graph, ExecutionConfig config);

    // Run inference
    std::vector<Tensor> run(const std::unordered_map<std::string, Tensor>& inputs);

    // Get profiling info
    ProfilingInfo profile() const;

private:
    Graph graph_;
    std::vector<std::unique_ptr<Operator>> operators_;
    TensorAllocator allocator_;
    ExecutionConfig config_;

    void compile();
    void allocate_intermediate_tensors();
};

struct ProfilingInfo {
    std::unordered_map<std::string, Duration> op_times;
    size_t peak_memory;
    Duration total_time;
};

// Benchmark runner
class Benchmark {
public:
    void run(ExecutionSession& session,
             const std::vector<Tensor>& inputs,
             int warmup_runs,
             int benchmark_runs);

    void report();

private:
    std::vector<Duration> latencies_;
    std::vector<ProfilingInfo> profiles_;
};
```

**Benchmarks to run:**
- BERT-base (encoder)
- GPT-2 (decoder)
- ResNet-50 (CNN)
- Compare FP32 vs INT8

---

## Project 3: ML Platform (Go)

**Project Name:** ModelHub

**What you're building:** An ML model serving platform with Kubernetes integration, like KServe, Seldon, or BentoML.

### Why This Project

MLOps is where ML meets production. You'll learn:
- Model lifecycle management
- Serving patterns (batching, caching, routing)
- Kubernetes operators
- Observability for ML

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         ModelHub                                 │
├─────────────────────────────────────────────────────────────────┤
│  CLI (modelhub)      │  Web UI             │  Python SDK        │
├─────────────────────────────────────────────────────────────────┤
│                      API Gateway                                 │
│  Auth                │  Rate Limiting      │  Request Routing   │
├─────────────────────────────────────────────────────────────────┤
│                      Control Plane                               │
│  Model Registry      │  Deployment Manager │  Traffic Manager   │
├─────────────────────────────────────────────────────────────────┤
│                      Kubernetes Operator                         │
│  InferenceService CRD│  Autoscaler        │  Traffic Split     │
├─────────────────────────────────────────────────────────────────┤
│                      Data Plane (per model)                      │
│  Model Server        │  Batcher            │  Preprocessor      │
├─────────────────────────────────────────────────────────────────┤
│                      Integrations                                │
│  VectorForge         │  Feature Store      │  Monitoring        │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 1: Model Registry (Month 13)

**Build:** Version-controlled model storage

**Features:**
- Model upload/download
- Versioning
- Metadata (framework, input/output schema)
- S3-compatible storage backend
- Model lineage

**API:**

```
POST   /api/v1/models                    Register model
GET    /api/v1/models                    List models
GET    /api/v1/models/{name}             Get model
POST   /api/v1/models/{name}/versions    Upload version
GET    /api/v1/models/{name}/versions    List versions
GET    /api/v1/models/{name}/versions/{v} Get version
DELETE /api/v1/models/{name}/versions/{v} Delete version
```

**Core Types:**

```go
type Model struct {
    ID          string            `json:"id"`
    Name        string            `json:"name"`
    Description string            `json:"description"`
    Framework   string            `json:"framework"` // pytorch, tensorflow, onnx
    Task        string            `json:"task"`      // text-generation, embedding, classification
    InputSchema  *Schema          `json:"inputSchema"`
    OutputSchema *Schema          `json:"outputSchema"`
    CreatedAt   time.Time         `json:"createdAt"`
    UpdatedAt   time.Time         `json:"updatedAt"`
    Labels      map[string]string `json:"labels"`
}

type ModelVersion struct {
    ID           string    `json:"id"`
    ModelID      string    `json:"modelId"`
    Version      string    `json:"version"`
    StorageURI   string    `json:"storageUri"`   // s3://bucket/path
    Framework    string    `json:"framework"`
    Metrics      Metrics   `json:"metrics"`      // accuracy, latency, etc.
    CreatedAt    time.Time `json:"createdAt"`
    CreatedBy    string    `json:"createdBy"`
}

type ModelRegistry interface {
    CreateModel(ctx context.Context, model *Model) error
    GetModel(ctx context.Context, name string) (*Model, error)
    ListModels(ctx context.Context, opts ListOptions) ([]*Model, error)

    CreateVersion(ctx context.Context, modelName string, version *ModelVersion) error
    GetVersion(ctx context.Context, modelName, version string) (*ModelVersion, error)
    ListVersions(ctx context.Context, modelName string) ([]*ModelVersion, error)
}
```

---

### Phase 2: Inference Server (Month 14)

**Build:** HTTP/gRPC server that runs models

**Features:**
- Multi-model serving
- Request batching
- Health checks
- Metrics (latency, throughput, errors)

**Core Types:**

```go
type InferenceServer struct {
    models   map[string]*LoadedModel
    batcher  *Batcher
    metrics  *Metrics
}

type LoadedModel struct {
    Name     string
    Version  string
    Runtime  Runtime  // interface to actual inference
}

type Runtime interface {
    Load(modelPath string) error
    Predict(ctx context.Context, inputs map[string]Tensor) (map[string]Tensor, error)
    Unload() error
}

// Batcher groups requests for efficiency
type Batcher struct {
    maxBatchSize    int
    maxWaitTime     time.Duration
    pendingRequests map[string]*batchQueue
}

func (b *Batcher) Submit(ctx context.Context, model string, input Tensor) (Tensor, error) {
    // Add to batch queue
    // Wait for batch to fill or timeout
    // Return result when batch completes
}

// gRPC service
type InferenceServiceServer struct {
    server *InferenceServer
}

func (s *InferenceServiceServer) Predict(ctx context.Context, req *PredictRequest) (*PredictResponse, error) {
    model, err := s.server.GetModel(req.ModelName)
    if err != nil {
        return nil, err
    }

    outputs, err := model.Runtime.Predict(ctx, req.Inputs)
    if err != nil {
        return nil, err
    }

    return &PredictResponse{Outputs: outputs}, nil
}
```

---

### Phase 3: Kubernetes Operator (Month 15)

**Build:** CRD and controller for deploying models to K8s

**Features:**
- InferenceService CRD
- Automatic deployment creation
- Service and ingress setup
- Resource management (CPU, memory, GPU)
- Rolling updates

**CRD:**

```yaml
apiVersion: modelhub.io/v1alpha1
kind: InferenceService
metadata:
  name: my-model
  namespace: default
spec:
  model:
    name: bert-base
    version: "1.0.0"
  runtime: onnx
  resources:
    requests:
      cpu: "2"
      memory: "4Gi"
    limits:
      cpu: "4"
      memory: "8Gi"
      nvidia.com/gpu: "1"
  scaling:
    minReplicas: 1
    maxReplicas: 10
    targetConcurrency: 100
  traffic:
    - version: "1.0.0"
      percent: 100
status:
  conditions:
    - type: Ready
      status: "True"
  url: https://my-model.default.example.com
  replicas: 2
```

**Controller:**

```go
type InferenceServiceReconciler struct {
    client.Client
    Scheme   *runtime.Scheme
    Registry *registry.Client
}

func (r *InferenceServiceReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    log := log.FromContext(ctx)

    var svc modelhubv1.InferenceService
    if err := r.Get(ctx, req.NamespacedName, &svc); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Fetch model from registry
    model, err := r.Registry.GetVersion(ctx, svc.Spec.Model.Name, svc.Spec.Model.Version)
    if err != nil {
        return ctrl.Result{}, err
    }

    // Reconcile Deployment
    if err := r.reconcileDeployment(ctx, &svc, model); err != nil {
        return ctrl.Result{}, err
    }

    // Reconcile Service
    if err := r.reconcileService(ctx, &svc); err != nil {
        return ctrl.Result{}, err
    }

    // Reconcile HPA
    if err := r.reconcileHPA(ctx, &svc); err != nil {
        return ctrl.Result{}, err
    }

    // Update status
    svc.Status.URL = fmt.Sprintf("https://%s.%s.svc.cluster.local", svc.Name, svc.Namespace)
    if err := r.Status().Update(ctx, &svc); err != nil {
        return ctrl.Result{}, err
    }

    return ctrl.Result{}, nil
}
```

---

### Phase 4: Traffic Management (Month 16)

**Build:** A/B testing, canary deployments, and traffic splitting

**Features:**
- Traffic percentage splitting
- Header-based routing
- Shadow traffic (mirror requests)
- Automatic rollback on errors

**Core Types:**

```go
type TrafficPolicy struct {
    Rules []TrafficRule `json:"rules"`
}

type TrafficRule struct {
    Match     *MatchCondition `json:"match,omitempty"`
    Version   string          `json:"version"`
    Percent   int             `json:"percent"`
    IsShadow  bool            `json:"isShadow,omitempty"`
}

type MatchCondition struct {
    Headers map[string]string `json:"headers,omitempty"`
}

type TrafficRouter struct {
    policy  TrafficPolicy
    servers map[string]*InferenceServer  // version -> server
}

func (r *TrafficRouter) Route(req *http.Request) (*InferenceServer, bool) {
    // Check header matches first
    for _, rule := range r.policy.Rules {
        if rule.Match != nil && matchHeaders(req, rule.Match.Headers) {
            return r.servers[rule.Version], rule.IsShadow
        }
    }

    // Weighted random selection
    roll := rand.Intn(100)
    cumulative := 0
    for _, rule := range r.policy.Rules {
        if rule.Match != nil {
            continue  // Skip match rules
        }
        cumulative += rule.Percent
        if roll < cumulative {
            return r.servers[rule.Version], rule.IsShadow
        }
    }

    return nil, false
}

// Automatic rollback
type RollbackController struct {
    errorThreshold float64
    windowSize     time.Duration
}

func (c *RollbackController) Check(version string, metrics *VersionMetrics) bool {
    errorRate := metrics.Errors / metrics.Requests
    if errorRate > c.errorThreshold {
        return true  // Should rollback
    }
    return false
}
```

---

### Phase 5: Observability (Month 17)

**Build:** Metrics, logging, and tracing for ML

**Features:**
- Prometheus metrics
- Request/response logging
- Distributed tracing
- Model performance monitoring (accuracy drift, latency)
- Dashboards

**Metrics:**

```go
var (
    requestsTotal = promauto.NewCounterVec(prometheus.CounterOpts{
        Name: "modelhub_requests_total",
        Help: "Total inference requests",
    }, []string{"model", "version", "status"})

    requestDuration = promauto.NewHistogramVec(prometheus.HistogramOpts{
        Name:    "modelhub_request_duration_seconds",
        Help:    "Request duration in seconds",
        Buckets: []float64{.001, .005, .01, .025, .05, .1, .25, .5, 1},
    }, []string{"model", "version"})

    batchSize = promauto.NewHistogramVec(prometheus.HistogramOpts{
        Name:    "modelhub_batch_size",
        Help:    "Inference batch sizes",
        Buckets: []float64{1, 2, 4, 8, 16, 32, 64},
    }, []string{"model"})

    modelLoaded = promauto.NewGaugeVec(prometheus.GaugeOpts{
        Name: "modelhub_model_loaded",
        Help: "Currently loaded models",
    }, []string{"model", "version"})
)

// ML-specific metrics
type ModelMetrics struct {
    // Track prediction distribution for drift detection
    PredictionDistribution *prometheus.HistogramVec

    // Track input feature statistics
    FeatureStatistics map[string]*FeatureStats
}

type FeatureStats struct {
    Min, Max, Mean, Stddev float64
    NullCount              int64
}
```

---

### Phase 6: VectorForge Integration & CLI (Month 18)

**Build:** RAG pipeline support and developer CLI

**Features:**
- VectorForge as embedding store
- RAG pipeline (embed → search → generate)
- CLI for all operations
- Python SDK

**RAG Pipeline:**

```go
type RAGPipeline struct {
    embedder    *InferenceService  // Embedding model
    vectorStore *vectorforge.Client
    generator   *InferenceService  // LLM
}

func (p *RAGPipeline) Query(ctx context.Context, query string, opts RAGOptions) (*RAGResponse, error) {
    // 1. Embed the query
    embedding, err := p.embedder.Predict(ctx, map[string]any{
        "text": query,
    })
    if err != nil {
        return nil, fmt.Errorf("embedding: %w", err)
    }

    // 2. Search vector store
    results, err := p.vectorStore.Search(ctx, vectorforge.SearchRequest{
        Vector: embedding["embedding"].([]float32),
        Limit:  opts.TopK,
        Filter: opts.Filter,
    })
    if err != nil {
        return nil, fmt.Errorf("vector search: %w", err)
    }

    // 3. Build context from results
    context := buildContext(results)

    // 4. Generate response
    response, err := p.generator.Predict(ctx, map[string]any{
        "prompt": fmt.Sprintf("Context:\n%s\n\nQuestion: %s\n\nAnswer:", context, query),
    })
    if err != nil {
        return nil, fmt.Errorf("generation: %w", err)
    }

    return &RAGResponse{
        Answer:  response["text"].(string),
        Sources: results,
    }, nil
}
```

**CLI:**

```bash
# Model management
modelhub models list
modelhub models create my-model --framework onnx
modelhub models push my-model:1.0.0 ./model.onnx

# Deployments
modelhub deploy my-model:1.0.0 --replicas 2 --gpu 1
modelhub deployments list
modelhub deployments logs my-model

# Traffic
modelhub traffic set my-model --v1=90 --v2=10
modelhub traffic shadow my-model --from=v1 --to=v2

# Testing
modelhub predict my-model --input '{"text": "hello"}'
modelhub benchmark my-model --duration 60s --concurrency 10

# RAG
modelhub rag create my-rag --embedder=sentence-transformers --generator=llama --vectorstore=my-vectors
modelhub rag query my-rag "What is the capital of France?"
```

---

## How The Projects Connect

```
                    ┌─────────────────────┐
                    │    User Request     │
                    │  "What is X about   │
                    │    document Y?"     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     ModelHub        │
                    │    (Go Platform)    │
                    │   - Routes request  │
                    │   - Batches         │
                    │   - Monitors        │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │   TinyInfer     │ │   TinyInfer     │ │   VectorForge   │
    │   (Embedder)    │ │   (Generator)   │ │   (Retrieval)   │
    │                 │ │                 │ │                 │
    │ C++ inference   │ │ C++ inference   │ │ Rust vector DB  │
    │ engine runs     │ │ engine runs     │ │ stores and      │
    │ embedding model │ │ LLM             │ │ searches docs   │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
```

**The flow:**
1. **ModelHub** receives a RAG query
2. Calls **TinyInfer** with embedding model to vectorize the query
3. Sends vector to **VectorForge** to find similar documents
4. Calls **TinyInfer** with LLM to generate answer using retrieved context
5. Returns response with sources

**Skills that transfer:**
- Storage engine concepts (VectorForge → understanding TinyInfer's memory management)
- Networking (all three use gRPC/HTTP)
- Distributed systems (VectorForge's Raft → ModelHub's multi-replica management)
- Kubernetes (ModelHub operators work with TinyInfer containers)

---

## Tools & Technologies

### ML Frameworks to Understand

| Framework | What to Know |
|-----------|--------------|
| **PyTorch** | Model export (TorchScript, ONNX), tensor semantics |
| **ONNX** | Interchange format, operator set |
| **Hugging Face** | Transformers, tokenizers, model hub |
| **CUDA** | Basics of GPU programming (optional but valuable) |

### Vector Search Libraries

| Library | Language | Notes |
|---------|----------|-------|
| **FAISS** | C++/Python | Facebook's ANN library, GPU support |
| **hnswlib** | C++ | Pure HNSW implementation |
| **usearch** | C++ | Modern, fast |
| **Annoy** | C++ | Spotify's tree-based ANN |

### Inference Runtimes to Study

| Runtime | Focus |
|---------|-------|
| **ONNX Runtime** | General-purpose, well-documented |
| **TensorRT** | NVIDIA optimization |
| **llama.cpp** | LLM-specific, quantization |
| **Candle** | Rust inference |

### ML Platform Tools

| Tool | Purpose |
|------|---------|
| **KServe** | K8s model serving |
| **Seldon Core** | ML deployment |
| **BentoML** | Model packaging |
| **MLflow** | Experiment tracking |
| **Weights & Biases** | Experiment tracking |

---

## Learning Resources

### Courses

| Course | Platform | Focus |
|--------|----------|-------|
| **CS329S: ML Systems Design** | Stanford (online) | ML systems overview |
| **Full Stack Deep Learning** | Online | Production ML |
| **MLOps Zoomcamp** | DataTalks.Club | Hands-on MLOps |
| **Efficient Deep Learning** | MIT | Optimization |

### Blogs & Sites

- **Chip Huyen's blog** - ML systems
- **Lilian Weng's blog** - ML concepts explained
- **Jay Alammar's blog** - Visualized ML
- **Hugging Face blog** - Transformers, inference
- **Qdrant blog** - Vector search

### Papers to Read

| Topic | Papers |
|-------|--------|
| Embeddings | Word2Vec, BERT, Sentence-BERT |
| Vector Search | HNSW, FAISS, ScaNN |
| Inference | TensorRT, FlashAttention, PagedAttention |
| Serving | Clipper, Clockwork, Orca |
| Quantization | LLM.int8(), GPTQ, AWQ |

### YouTube

| Channel | Content |
|---------|---------|
| **Weights & Biases** | MLOps, interviews |
| **Yannic Kilcher** | Paper explanations |
| **Andrej Karpathy** | Neural network fundamentals |

---

## 18-Month Schedule

| Months | Project | Focus |
|--------|---------|-------|
| 1-6 | **VectorForge** (Rust) | Vector DB with HNSW, filtering, persistence, distribution |
| 7-12 | **TinyInfer** (C++) | Inference engine with tensors, ops, ONNX, optimization, quantization |
| 13-18 | **ModelHub** (Go) | ML platform with registry, serving, K8s operator, traffic, observability |

### Detailed Breakdown

| Month | Project | Phase |
|-------|---------|-------|
| 1 | VectorForge | Vector storage, SIMD distance |
| 2 | VectorForge | HNSW index |
| 3 | VectorForge | Filtering, payloads |
| 4 | VectorForge | Persistence, WAL |
| 5 | VectorForge | REST/gRPC API |
| 6 | VectorForge | Distributed (sharding, replication) |
| 7 | TinyInfer | Tensor library |
| 8 | TinyInfer | Operators (MatMul, Attention, etc.) |
| 9 | TinyInfer | ONNX loading, graph IR |
| 10 | TinyInfer | Graph optimization |
| 11 | TinyInfer | Quantization (INT8) |
| 12 | TinyInfer | Execution engine, benchmarks |
| 13 | ModelHub | Model registry |
| 14 | ModelHub | Inference server, batching |
| 15 | ModelHub | Kubernetes operator |
| 16 | ModelHub | Traffic management |
| 17 | ModelHub | Observability |
| 18 | ModelHub | VectorForge integration, CLI |

---

## Career Paths

After completing this track, you'll be prepared for:

### ML Infrastructure Engineer
- Build and maintain training/serving infrastructure
- Companies: OpenAI, Anthropic, Google, Meta

### ML Platform Engineer
- Build internal ML platforms
- Companies: Any large tech company

### Vector Database Engineer
- Build similarity search systems
- Companies: Pinecone, Weaviate, Qdrant, Chroma

### Inference Optimization Engineer
- Optimize model performance
- Companies: NVIDIA, Intel, Apple, startups

### MLOps Engineer
- Production ML pipelines and operations
- Companies: Every company doing ML

---

## Final Words

AI infrastructure is systems programming with an ML flavor. You're not building models - you're building the systems that make models useful.

What makes this track special:
1. **Real demand** - Every company deploying AI needs this
2. **Transferable skills** - Storage, networking, distributed systems apply everywhere
3. **Full stack** - You understand from vectors to serving
4. **Three languages** - Each for its strength

The projects connect: VectorForge stores embeddings, TinyInfer produces them, ModelHub orchestrates everything. By the end, you can build a complete RAG system from scratch.

Start with Rust. Build a vector database. The rest will follow.

---

*Generated: January 2026*
