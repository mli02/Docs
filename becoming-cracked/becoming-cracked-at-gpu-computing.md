# Becoming Cracked at GPU & Parallel Computing

A comprehensive guide to mastering GPU programming and parallel computing for high-performance systems.

---

## Table of Contents

1. [Core Philosophy](#core-philosophy)
2. [Core Mental Models](#core-mental-models)
3. [Books & Resources](#books--resources)
4. [Structured Learning Path](#structured-learning-path)
5. [Tools & Setup](#tools--setup)
6. [Project Progression](#project-progression)
7. [Capstone Project: TinyKernels](#capstone-project-tinykernels)
8. [Open Source to Study](#open-source-to-study)
9. [Common Pitfalls](#common-pitfalls)
10. [12-Month Schedule](#12-month-schedule)

---

## Core Philosophy

GPU programming is about **thinking in parallel**. The mental shift from sequential to massively parallel execution is the hard part—the syntax is easy.

**Why learn GPU programming:**
- AI/ML is bottlenecked by GPU compute
- 100-1000x speedups are possible for parallel workloads
- Understanding hardware makes you a better systems programmer
- It's where performance-critical work happens

**The key insight:** GPUs aren't faster CPUs—they're different machines with different tradeoffs. Success comes from understanding those tradeoffs deeply.

---

## Core Mental Models

### 1. SIMT: Single Instruction, Multiple Threads

GPUs execute the same instruction across many threads simultaneously. This is NOT the same as SIMD on CPUs.

```
CPU SIMD: One instruction operates on a vector register (4-8 elements)
GPU SIMT: One instruction dispatched to 32+ threads, each with own registers

Key insight: Threads can diverge (if/else), but divergence kills performance
```

**Mental model:** Think of a GPU as a massive choir. Everyone sings the same note at the same time. If half the choir needs to sing a different note, they take turns—destroying parallelism.

### 2. The Memory Hierarchy

```
Registers     → Per thread    → ~1 cycle      → KB total
Shared Memory → Per block     → ~5 cycles     → 48-164 KB per SM
L1 Cache      → Per SM        → ~30 cycles    → 128 KB per SM
L2 Cache      → Per GPU       → ~200 cycles   → 4-50 MB
Global Memory → Per GPU       → ~400 cycles   → 8-80 GB (HBM or GDDR)
```

**Mental model:** Global memory is like reading from a library across town. Shared memory is your desk. Registers are your hands. Optimize for keeping data close.

### 3. Occupancy and Latency Hiding

GPUs hide memory latency by switching between threads, not by caching.

```
CPU approach: Cache data, minimize memory accesses
GPU approach: Keep thousands of threads ready, switch when one waits

Occupancy = Active warps / Maximum warps per SM
```

**Mental model:** A GPU is like a restaurant with 1000 tables. When one table waits for food, the waiter serves another. High occupancy = many tables occupied = waiters always busy.

### 4. Coalesced Memory Access

When threads in a warp access consecutive memory addresses, the hardware combines them into fewer transactions.

```
Good: Thread 0 reads addr 0, Thread 1 reads addr 1, Thread 2 reads addr 2...
Bad:  Thread 0 reads addr 0, Thread 1 reads addr 128, Thread 2 reads addr 256...

Coalesced access: 1 transaction for 32 threads
Strided access: Up to 32 transactions for 32 threads (32x slower)
```

**Mental model:** Memory bus is like a highway. Coalesced access = carpooling. Strided access = everyone driving alone.

### 5. Warp Divergence

A warp (32 threads) must execute the same instruction. Branches cause serialization.

```cuda
if (threadIdx.x < 16) {
    // First 16 threads execute, other 16 idle
    doA();
} else {
    // Last 16 threads execute, first 16 idle
    doB();
}
// Total time: time(doA) + time(doB), not max(doA, doB)
```

**Mental model:** The choir analogy again. If half sing verse 1 and half sing verse 2, you hear both verses sequentially.

### 6. Thread Hierarchy

```
Thread → Warp (32 threads) → Block (up to 1024 threads) → Grid (millions of threads)

- Threads in a warp execute in lockstep
- Threads in a block can synchronize and share memory
- Blocks are independent (enables scaling across GPUs)
```

### 7. Compute vs Memory Bound

```
Arithmetic Intensity = FLOPs / Bytes loaded

Low intensity (< 10): Memory bound → optimize memory access patterns
High intensity (> 50): Compute bound → optimize arithmetic operations

Matrix multiply: O(n³) compute, O(n²) memory → compute bound
Vector add: O(n) compute, O(n) memory → memory bound
```

**Mental model:** Use the roofline model to understand your kernel's bottleneck.

### 8. Synchronization Primitives

```
__syncthreads()     → Barrier within a block
__syncwarp()        → Barrier within a warp
atomicAdd/CAS       → Cross-block synchronization (expensive)
cooperative_groups  → Flexible synchronization scopes
```

**Rule:** Synchronization within a block is cheap. Synchronization across blocks is expensive or impossible.

---

## Books & Resources

### Foundational (Read First)

| Book | Focus | Priority |
|------|-------|----------|
| **"Programming Massively Parallel Processors"** by Kirk & Hwu (4th ed) | THE CUDA textbook, theory + practice | Essential |
| **"CUDA by Example"** by Sanders & Kandrot | Gentler introduction, practical focus | Good first book |
| **NVIDIA CUDA C++ Programming Guide** (online) | Official reference | Essential reference |

### Intermediate

| Book | Focus | Priority |
|------|-------|----------|
| **"Professional CUDA C Programming"** by Cheng et al. | Production patterns, optimization | High |
| **"GPU Gems"** series (free online) | Graphics + compute techniques | Medium |
| **"Parallel and High Performance Computing"** by Robey & Zamora | Broader HPC context | Medium |

### Advanced / Specialized

| Book | Focus | Priority |
|------|-------|----------|
| **"The Art of Multiprocessor Programming"** by Herlihy & Shavit | Lock-free algorithms, correctness | High for systems work |
| **"Real-Time Rendering"** (4th ed) | Graphics programming bible | If doing graphics |
| **"Ray Tracing Gems"** (free online) | Modern ray tracing techniques | If doing graphics |

### Papers (Essential Reading)

| Paper | Why |
|-------|-----|
| **"Roofline: An Insightful Visual Performance Model"** | Understand compute vs memory bound |
| **"Efficient Parallel Scan Algorithms for GPUs"** | Fundamental parallel primitive |
| **"Understanding the GPU Microarchitecture"** | What's actually happening in hardware |
| **"FlashAttention: Fast and Memory-Efficient Attention"** | Modern ML kernel optimization |
| **"Tensor Cores: Programming and Performance"** | Using specialized hardware |

---

## Structured Learning Path

### Phase 1: Foundations (Months 1-2)

**Goal:** Understand the programming model and write basic kernels.

**Reading:**
- "CUDA by Example" chapters 1-7
- NVIDIA CUDA Programming Guide chapters 1-4

**Practice:**
- Set up CUDA development environment
- Vector addition, scaling
- Matrix operations (add, transpose)
- Image brightness/contrast adjustment

**Key concepts to master:**
- Thread/block/grid hierarchy
- Memory allocation (cudaMalloc, cudaMemcpy)
- Kernel launch syntax `<<<blocks, threads>>>`
- Basic error handling

### Phase 2: Memory Optimization (Months 2-3)

**Goal:** Understand and optimize memory access patterns.

**Reading:**
- "Programming Massively Parallel Processors" chapters 4-6
- CUDA Best Practices Guide: Memory Optimizations

**Practice:**
- Matrix multiply (naive → tiled with shared memory)
- Coalescing experiments
- Bank conflict analysis
- Memory bandwidth benchmarking

**Key concepts to master:**
- Shared memory tiling
- Memory coalescing
- Bank conflicts
- Pinned memory and async transfers

### Phase 3: Parallel Patterns (Months 3-4)

**Goal:** Master fundamental parallel algorithms.

**Reading:**
- "Programming Massively Parallel Processors" chapters 7-11
- GPU Gems 3: Parallel algorithms chapters

**Practice:**
- Parallel reduction (sum, max, min)
- Prefix scan (inclusive, exclusive)
- Histogram
- Compact/filter
- Sort (radix sort on GPU)

**Key concepts to master:**
- Work-efficient algorithms
- Avoiding thread divergence
- Handling non-power-of-2 sizes
- Multi-pass algorithms

### Phase 4: Performance Analysis (Months 4-5)

**Goal:** Profile, analyze, and systematically optimize kernels.

**Reading:**
- NVIDIA Nsight Compute documentation
- "Professional CUDA C Programming" optimization chapters

**Practice:**
- Profile your previous kernels
- Identify bottlenecks (compute, memory, latency)
- Roofline analysis
- Occupancy optimization
- Instruction-level optimization

**Key concepts to master:**
- Nsight Compute profiler
- Achieved vs theoretical bandwidth
- Warp efficiency metrics
- Register pressure

### Phase 5: Advanced Features (Months 5-6)

**Goal:** Use advanced hardware features and multi-GPU programming.

**Reading:**
- CUDA Programming Guide: Advanced features
- Multi-GPU programming guides

**Practice:**
- Tensor Cores (WMMA API or cuBLAS)
- Cooperative groups
- Dynamic parallelism
- Multi-GPU with NCCL
- CUDA graphs

**Key concepts to master:**
- Tensor Core programming model
- Stream and event management
- Peer-to-peer memory access
- Unified memory

### Phase 6: Domain Application (Months 6+)

Choose a specialization based on your interests:

**Option A: ML Kernels**
- GEMM optimization
- Attention mechanisms
- Custom autograd operations
- Quantization kernels

**Option B: Graphics/Simulation**
- Ray tracing with OptiX
- Physics simulation
- Particle systems
- Fluid dynamics

**Option C: Scientific Computing**
- Stencil computations
- FFT implementations
- Sparse matrix operations
- Solvers (CG, GMRES)

---

## Tools & Setup

### Hardware Requirements

| Tier | Hardware | Notes |
|------|----------|-------|
| **Minimum** | GTX 1060 or better | Supports CUDA Compute 6.0+ |
| **Recommended** | RTX 3080/4080 | Tensor Cores, good performance |
| **Ideal** | A100/H100 or RTX 4090 | Full feature set, HBM/high bandwidth |

**Cloud options:** Lambda Labs, Vast.ai, Google Colab Pro (for learning)

### Software Stack

```
CUDA Toolkit: Latest stable (12.x as of 2024)
Compiler: nvcc (comes with toolkit)
IDE: VSCode with CUDA extensions or CLion
Profiler: Nsight Compute, Nsight Systems
Debugger: cuda-gdb, Nsight debugger
```

### Essential Tools

| Tool | Purpose |
|------|---------|
| **Nsight Compute** | Kernel profiling, performance analysis |
| **Nsight Systems** | System-wide profiling, timeline view |
| **cuda-gdb** | CUDA debugger |
| **compute-sanitizer** | Memory error detection (like Valgrind for GPU) |
| **nvprof** | Legacy profiler (still useful) |

### Development Environment Setup

```bash
# Ubuntu/Debian
# Install CUDA Toolkit from NVIDIA's website (not apt for latest version)

# Add to ~/.bashrc
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Verify installation
nvcc --version
nvidia-smi

# Compile and run
nvcc -O3 -arch=sm_80 my_kernel.cu -o my_kernel
./my_kernel
```

### VSCode Setup

```json
// .vscode/settings.json
{
    "files.associations": {
        "*.cu": "cuda-cpp",
        "*.cuh": "cuda-cpp"
    }
}

// Extensions: NVIDIA Nsight Visual Studio Code Edition, C/C++
```

---

## Project Progression

### Level 1: Hello GPU

**Goal:** Get comfortable with the programming model.

| Project | Concepts |
|---------|----------|
| Vector addition | Kernel launch, memory allocation |
| Matrix transpose | 2D indexing, naive vs coalesced |
| Image processing (grayscale, brightness) | Working with real data |
| Dot product | Introduction to reduction |

### Level 2: Memory Mastery

**Goal:** Understand and optimize memory access.

| Project | Concepts |
|---------|----------|
| Tiled matrix multiply | Shared memory, tiling |
| Convolution (1D, 2D) | Halos, shared memory patterns |
| Histogram | Atomics, privatization |
| Memory bandwidth benchmark | Measuring achieved bandwidth |

### Level 3: Parallel Primitives

**Goal:** Implement fundamental parallel building blocks.

| Project | Concepts |
|---------|----------|
| Parallel reduction (multiple strategies) | Tree reduction, warp shuffle |
| Prefix scan (Blelloch, Kogge-Stone) | Work-efficient algorithms |
| Radix sort | Multi-pass algorithms |
| Stream compaction | Scan applications |

### Level 4: Real Applications

**Goal:** Apply knowledge to useful problems.

| Project | Concepts |
|---------|----------|
| N-body simulation | O(n²) → O(n log n) algorithms |
| Image blur/filters | 2D convolution, separable filters |
| K-means clustering | Iterative algorithms |
| BFS/graph algorithms | Irregular parallelism |

### Level 5: Advanced Systems

**Goal:** Production-quality implementations.

| Project | Concepts |
|---------|----------|
| GEMM optimization | Memory hierarchy, register tiling, Tensor Cores |
| FlashAttention implementation | Memory-efficient algorithms |
| Custom PyTorch/JAX operator | Framework integration |
| Multi-GPU reduction | NCCL, peer-to-peer |

---

## Capstone Project: TinyKernels

Build a **mini ML kernel library** from scratch—a simplified cuBLAS/cuDNN that teaches you how high-performance ML libraries actually work.

### Project Overview

```
TinyKernels/
├── src/
│   ├── gemm/           # Matrix multiplication kernels
│   ├── attention/      # Attention mechanisms
│   ├── activation/     # ReLU, GELU, SiLU
│   ├── normalization/  # LayerNorm, RMSNorm
│   ├── elementwise/    # Fused operations
│   └── reduce/         # Reductions, softmax
├── tests/
├── benchmarks/
└── python/             # PyTorch/JAX bindings
```

### Phase 1: Foundation GEMM (Weeks 1-4)

Build matrix multiplication from naive to near-cuBLAS performance.

**Week 1: Naive Implementation**
- Basic GEMM kernel (C = αAB + βC)
- Correctness testing against cuBLAS
- Baseline performance measurement

**Week 2: Shared Memory Tiling**
- Implement 2D tiling
- Analyze shared memory usage
- Profile and measure improvement

**Week 3: Register Tiling**
- Thread-level tiling (each thread computes multiple outputs)
- Register pressure analysis
- Vectorized loads (float4)

**Week 4: Advanced Optimizations**
- Double buffering (hide memory latency)
- Bank conflict resolution
- Auto-tuning tile sizes

**Milestone:** Achieve 70%+ of cuBLAS performance on RTX 3080/4080.

### Phase 2: Memory-Efficient Attention (Weeks 5-8)

Implement FlashAttention from the paper.

**Week 5: Standard Attention**
- Naive Q @ K^T @ V implementation
- Memory analysis (O(n²) intermediate)
- Numerical stability (online softmax)

**Week 6: FlashAttention v1**
- Tiled attention (avoid materializing O(n²))
- Online softmax computation
- Memory-efficient backward pass

**Week 7: FlashAttention v2**
- Improved parallelism
- Better work partitioning
- Sequence parallelism

**Week 8: Extensions**
- Multi-head attention
- Causal masking
- Variable sequence lengths

**Milestone:** Memory usage O(n) instead of O(n²), performance within 2x of official FlashAttention.

### Phase 3: Fused Kernels (Weeks 9-12)

Build commonly fused operations.

**Week 9: Activation Functions**
- ReLU, GELU, SiLU implementations
- Fused bias + activation
- Vectorized implementations

**Week 10: Normalization**
- LayerNorm (reduction + normalize)
- RMSNorm
- Fused residual + norm

**Week 11: Elementwise Fusion**
- JIT kernel generation for elementwise ops
- Fusing chains of operations
- Code generation basics

**Week 12: Softmax & Reductions**
- Numerically stable softmax
- Cross-entropy loss
- TopK selection

**Milestone:** Fused kernels 2-5x faster than separate operations.

### Phase 4: Tensor Core Integration (Weeks 13-16)

Use specialized hardware for maximum performance.

**Week 13: WMMA Basics**
- Understand Tensor Core architecture
- WMMA API basics
- Matrix fragment operations

**Week 14: Tensor Core GEMM**
- Rewrite GEMM using Tensor Cores
- Mixed precision (FP16 compute, FP32 accumulate)
- Compare with cuBLAS

**Week 15: Tensor Core Attention**
- Integrate Tensor Cores into FlashAttention
- Handle precision considerations
- Profile and optimize

**Week 16: Quantization**
- INT8 GEMM
- Quantization-aware kernels
- Performance vs accuracy tradeoffs

**Milestone:** 2-4x speedup over CUDA core implementations.

### Phase 5: Multi-GPU & Integration (Weeks 17-20)

Scale across GPUs and integrate with frameworks.

**Week 17: Multi-GPU Primitives**
- NCCL all-reduce
- Tensor parallelism basics
- Ring-allreduce implementation

**Week 18: Distributed GEMM**
- Split computation across GPUs
- Overlap communication and compute
- Scaling efficiency analysis

**Week 19: PyTorch Integration**
- Custom autograd functions
- Torch extension building
- Backward pass implementation

**Week 20: JAX Integration**
- Custom JAX primitives
- XLA custom calls
- Benchmark against JAX native

**Milestone:** Drop-in replacement for torch.nn.functional.linear, attention.

### Phase 6: Polish & Document (Weeks 21-24)

**Week 21: Performance Engineering**
- Comprehensive benchmarks
- Auto-tuning framework
- Handle edge cases

**Week 22: Testing & Correctness**
- Numerical accuracy tests
- Gradient checking
- Stress testing

**Week 23: Documentation**
- Architecture documentation
- Performance guide
- API documentation

**Week 24: Open Source**
- Clean up codebase
- Write README and examples
- Publish and blog about it

---

## Open Source to Study

### Essential Codebases

| Project | Why Study It |
|---------|--------------|
| **[CUTLASS](https://github.com/NVIDIA/cutlass)** | NVIDIA's GEMM library—gold standard for matmul |
| **[FlashAttention](https://github.com/Dao-AILab/flash-attention)** | Memory-efficient attention, excellent code |
| **[cuBLAS/cuDNN](https://developer.nvidia.com/)** | Closed source, but study the APIs and benchmarks |

### Learning-Friendly Projects

| Project | Focus |
|---------|-------|
| **[cuda-samples](https://github.com/NVIDIA/cuda-samples)** | Official examples covering all features |
| **[GPU-Puzzles](https://github.com/srush/GPU-Puzzles)** | Interactive exercises for GPU programming |
| **[ThunderKittens](https://github.com/HazyResearch/ThunderKittens)** | Simple DSL for GPU kernels |

### Advanced Study

| Project | Focus |
|---------|-------|
| **[Triton](https://github.com/openai/triton)** | Python-based GPU programming language |
| **[TVM](https://github.com/apache/tvm)** | ML compiler, kernel generation |
| **[llm.c](https://github.com/karpathy/llm.c)** | LLM training in pure CUDA |
| **[ggml](https://github.com/ggerganov/ggml)** | Tensor library, see CUDA backend |

### Graphics-Focused

| Project | Focus |
|---------|-------|
| **[PBRT](https://github.com/mmp/pbrt-v4)** | Physically based renderer with GPU backend |
| **[Blender Cycles](https://github.com/blender/cycles)** | Production ray tracer |

---

## Common Pitfalls

### 1. Ignoring Memory Coalescing

```cuda
// BAD: Strided access
int idx = threadIdx.x * stride;
output[idx] = input[idx];

// GOOD: Coalesced access
int idx = threadIdx.x;
output[idx] = input[idx];
```

**Impact:** 10-32x performance difference.

### 2. Excessive Synchronization

```cuda
// BAD: Sync after every operation
for (int i = 0; i < 100; i++) {
    doWork();
    __syncthreads();  // Often unnecessary
}

// GOOD: Sync only when required for correctness
loadToSharedMem();
__syncthreads();  // Needed before reading shared memory
useSharedMem();
```

### 3. Not Profiling

**Mistake:** Guessing where the bottleneck is.

**Solution:** Always profile with Nsight Compute first. Check:
- Memory throughput (compute or memory bound?)
- Warp execution efficiency (divergence?)
- Occupancy (register/shared memory limited?)

### 4. Branch Divergence in Inner Loops

```cuda
// BAD: Divergent branch executed many times
for (int i = 0; i < n; i++) {
    if (threadIdx.x % 2 == 0) {
        // Half the warp idles
    }
}

// GOOD: Restructure to minimize divergence
if (threadIdx.x % 2 == 0) {
    for (int i = 0; i < n; i++) {
        // All active threads execute together
    }
}
```

### 5. Shared Memory Bank Conflicts

```cuda
// BAD: All threads access same bank
shared[threadIdx.x * 32] = data;  // 32-way bank conflict

// GOOD: Consecutive access or padding
shared[threadIdx.x] = data;  // No conflicts
// Or add padding: shared[row][col + row % pad]
```

### 6. Register Spilling

**Symptoms:** Kernel slower than expected, high local memory traffic.

**Solutions:**
- Reduce variables per thread
- Use `__launch_bounds__` to control register usage
- Trade parallelism for registers (larger tiles, fewer threads)

### 7. Ignoring Occupancy

**Mistake:** Assuming more threads per block is always better.

**Reality:** Register and shared memory usage limits how many blocks can run concurrently. Sometimes fewer threads per block = higher occupancy = better performance.

### 8. Not Using Tensor Cores

For matrix operations on modern GPUs, Tensor Cores provide 8-16x speedup. Not using them leaves massive performance on the table.

### 9. CPU-GPU Transfer Overhead

**Mistake:** Moving small amounts of data back and forth frequently.

**Solution:**
- Batch operations on GPU
- Use pinned memory for faster transfers
- Overlap compute and transfer with streams
- Keep data on GPU as long as possible

### 10. Premature Optimization

**Mistake:** Optimizing before understanding the algorithm.

**Correct approach:**
1. Write correct naive implementation
2. Verify correctness
3. Profile to find bottlenecks
4. Optimize based on data
5. Verify correctness again

---

## 12-Month Schedule

| Month | Focus | Project Work |
|-------|-------|--------------|
| **1** | Setup, basics, first kernels | Vector ops, matrix transpose |
| **2** | Memory hierarchy, tiling | Tiled matmul, convolution |
| **3** | Parallel primitives | Reduction, scan, sort |
| **4** | Performance analysis | Profile and optimize previous work |
| **5** | Advanced features | Tensor Cores, cooperative groups |
| **6** | **Capstone Phase 1** | GEMM from scratch |
| **7** | **Capstone Phase 2** | FlashAttention |
| **8** | **Capstone Phase 3** | Fused kernels |
| **9** | **Capstone Phase 4** | Tensor Core integration |
| **10** | **Capstone Phase 5** | Multi-GPU, framework integration |
| **11** | **Capstone Phase 6** | Polish, document, open source |
| **12** | Specialization | Graphics, scientific computing, or advanced ML |

---

## Beyond CUDA

### Alternative Platforms

| Platform | When to Use |
|----------|-------------|
| **OpenCL** | Cross-vendor (AMD, Intel, NVIDIA) |
| **SYCL** | Modern C++ abstraction over OpenCL |
| **HIP** | AMD's CUDA-like API |
| **Metal** | Apple GPUs |
| **WebGPU** | Browser-based GPU compute |
| **Vulkan Compute** | Cross-platform, lower-level than OpenCL |

### Higher-Level Abstractions

| Tool | Use Case |
|------|----------|
| **Triton** | Python-based GPU programming (easier than CUDA) |
| **JAX** | Automatic vectorization and GPU compilation |
| **CuPy** | NumPy-compatible GPU arrays |
| **Numba CUDA** | Python with CUDA kernels |
| **RAPIDS** | GPU-accelerated data science |

### When to Use What

```
Need maximum performance → CUDA/HIP
Need cross-platform → OpenCL/SYCL/Vulkan
Prototyping → Triton/CuPy/JAX
Production ML → Use existing kernels (cuBLAS, FlashAttention)
Custom ML ops → Triton first, CUDA if needed
```

---

## Resources & Community

### Online Resources

| Resource | Focus |
|----------|-------|
| **NVIDIA Developer Blog** | New features, optimization guides |
| **GTC Talks** (on-demand) | Deep dives on specific topics |
| **GPU Gems** (free online) | Classic techniques |
| **Parallel Forall Blog** | Technical tutorials |

### Communities

| Community | Platform |
|-----------|----------|
| **NVIDIA Developer Forums** | Official support |
| **r/CUDA** | Reddit community |
| **GPU MODE Discord** | Active ML kernel community |

### Must-Watch Talks

| Talk | Why |
|------|-----|
| **"How GPU Computing Works"** (GTC) | Architecture overview |
| **"CUTLASS: Fast GEMM"** (GTC) | High-performance matmul |
| **"FlashAttention"** (Stanford) | Memory-efficient algorithms |
| **"Programming Tensor Cores"** (GTC) | Using specialized hardware |

---

*Generated: January 2026*
