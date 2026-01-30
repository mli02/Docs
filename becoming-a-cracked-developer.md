# Becoming a Cracked Systems/Infrastructure Developer

A comprehensive guide to mastering systems programming for infrastructure development.

---

## Table of Contents

1. [Core Philosophy](#core-philosophy)
2. [Language Guides](#language-guides)
3. [Books: The Foundation](#books-the-foundation)
4. [Structured Reading Path](#structured-reading-path)
5. [Tools: Your Arsenal](#tools-your-arsenal)
6. [Development Setup](#development-setup)
7. [Project Progression](#project-progression)
8. [Cross-Language Projects](#cross-language-projects)
9. [Learning Resources](#learning-resources)
10. [Daily Habits](#daily-habits)
11. [18-Month Schedule](#18-month-schedule)

---

## Core Philosophy

Being "cracked" means going beyond syntax to understand **why** things work, not just **how**. It's about:

- Deep mental models of memory, performance, and system behavior
- Reading and understanding complex codebases
- Debugging effectively when things break
- Writing code that others can maintain

---

## Language Guides

Each language has its own comprehensive guide with mental models, project progressions, and capstone projects:

| Language | Guide | Capstone Project |
|----------|-------|------------------|
| **C++** | [Becoming Cracked at C++](./becoming-cracked-at-cpp.md) | MiniDB - Database engine from scratch |
| **Rust** | [Becoming Cracked at Rust](./becoming-cracked-at-rust.md) | TinyKV - Distributed KV store with Raft |
| **Go** | [Becoming Cracked at Go](./becoming-cracked-at-go.md) | Launchpad - PaaS with K8s operators |

Each guide includes:
- Core mental models specific to the language
- Structured reading paths (books + timeline)
- Video resources and must-watch talks
- Complete tooling and development setup
- 6-month capstone project with phases
- Level 1-5 project progressions
- Open source projects to study
- Common pitfalls and how to avoid them

---

## Specialized Tracks

### AI Infrastructure Track

For those focused on machine learning systems, there's a dedicated track:

| Guide | Focus |
|-------|-------|
| [Becoming Cracked at AI Infrastructure](./becoming-cracked-at-ai-infra.md) | ML systems, inference engines, vector databases, ML platforms |

This track uses all three languages with AI-focused projects:

| Month | Language | Project | Focus |
|-------|----------|---------|-------|
| 1-6 | Rust | **VectorForge** | Vector database with HNSW, filtering, distributed search |
| 7-12 | C++ | **TinyInfer** | Inference engine with ONNX, graph optimization, quantization |
| 13-18 | Go | **ModelHub** | ML platform with K8s operators, traffic management, observability |

By the end, you can build a complete RAG pipeline from scratch.

---

## Books: The Foundation

### Systems Programming Fundamentals

These are language-agnostic and essential for all systems programmers:

| Book | Focus |
|------|-------|
| **"Operating Systems: Three Easy Pieces"** (free online) | OS concepts - processes, memory, concurrency |
| **"Computer Systems: A Programmer's Perspective" (CSAPP)** | How code actually runs on hardware |
| **"The Linux Programming Interface"** by Michael Kerrisk | Linux systems programming bible |
| **"Linux Kernel Development"** by Robert Love | Kernel internals |

### Infrastructure & Distributed Systems

| Book | Focus |
|------|-------|
| **"Designing Data-Intensive Applications"** by Martin Kleppmann | THE infrastructure bible |
| **"Think Distributed Systems"** | Modern distributed systems |
| **"Site Reliability Engineering"** (Google SRE book, free) | Production systems |
| **"TCP/IP Sockets in C"** | Network programming |

### Computer Architecture

| Book | Focus |
|------|-------|
| **"Computer Architecture: A Quantitative Approach"** by Hennessy & Patterson | CPU, memory, caches |
| **"What Every Programmer Should Know About Memory"** by Ulrich Drepper (free PDF) | Memory hierarchy |

*See the individual language guides for language-specific book recommendations.*

---

## Structured Reading Path

### Phase 1: Core Foundations (Months 1-3)

Read these regardless of which language you start with:

| Order | Book | Focus | Time |
|-------|------|-------|------|
| 1 | **"Computer Systems: A Programmer's Perspective" (CSAPP)** Chapters 1-6 | How programs execute, memory, assembly basics | 4-6 weeks |
| 2 | **"Operating Systems: Three Easy Pieces"** (free online) Parts 1-2 | Processes, threads, memory virtualization | 3-4 weeks |

**Why these first:** Every systems language assumes you understand what's happening beneath the code. These books give you the mental model that makes everything else click.

---

### Phase 2: First Language Deep Dive (Months 3-6)

Pick ONE language to master first. Follow the structured reading path in the corresponding guide:

- **[Rust First](./becoming-cracked-at-rust.md#structured-reading-path)** (Recommended) - The ownership system forces you to think about memory correctly
- **[C++ First](./becoming-cracked-at-cpp.md#structured-reading-path)** - Maximum control, steepest learning curve
- **[Go First](./becoming-cracked-at-go.md#structured-reading-path)** - Fastest path to building production systems

---

### Phase 3: Systems Programming Depth (Months 6-9)

| Order | Book | Focus |
|-------|------|-------|
| 1 | **"The Linux Programming Interface"** Chapters 1-13, 23-33, 56-61 | File I/O, processes, signals, sockets |
| 2 | **"TCP/IP Sockets in C"** or equivalent in your language | Network programming |
| 3 | Language-specific concurrency book (see language guides) | Low-level concurrency |

---

### Phase 4: Second Language (Months 9-12)

Now add your second language. You can move faster because you have foundations:

| If you started with | Add next | Why |
|---------------------|----------|-----|
| Rust | C++ | Understand what Rust protects you from |
| Rust | Go | Appreciate simplicity, learn production patterns |
| C++ | Rust | See memory safety done differently |
| C++ | Go | Fastest path to cloud-native development |
| Go | Rust | Deep systems understanding |
| Go | C++ | Maximum performance, legacy systems |

---

### Phase 5: Infrastructure & Distributed Systems (Months 12-18)

| Order | Book | Focus |
|-------|------|-------|
| 1 | **"Designing Data-Intensive Applications"** (entire book) | THE infrastructure bible - read slowly, take notes |
| 2 | **"Site Reliability Engineering"** (Google SRE book) selected chapters | Production systems thinking |
| 3 | **"Think Distributed Systems"** | Modern distributed systems patterns |

---

### Phase 6: Third Language + Specialization (Months 18+)

Add your third language and go deep in a specialty area.

---

## Tools: Your Arsenal

### Debugging & Profiling

| Tool | Use |
|------|-----|
| **GDB** | C/C++ debugging |
| **LLDB** | C/C++/Rust debugging (better on macOS) |
| **Delve** | Go debugging |
| **perf** | Linux performance profiling |
| **Valgrind** | Memory debugging |
| **AddressSanitizer/ThreadSanitizer** | Runtime bug detection |
| **pprof** | Go profiling |
| **cargo-flamegraph** | Rust performance visualization |

### Development Environment

| Tool | Purpose |
|------|---------|
| **Compiler Explorer (godbolt.org)** | See assembly output - essential |
| **Neovim or VSCode** | Editor (with language server support) |
| **tmux** | Terminal multiplexer - manage sessions |
| **zsh + oh-my-zsh** or **fish** | Better shell experience |
| **ripgrep (rg)** | Fast code search |
| **fd** | Fast file finding |
| **fzf** | Fuzzy finder |
| **lazygit** | Terminal git UI |

### Build & Toolchain

| Language | Tools |
|----------|-------|
| **C++** | CMake, Ninja, clang-tidy, clang-format |
| **Rust** | cargo, clippy, rustfmt, miri |
| **Go** | go build, go test, golangci-lint |

### Infrastructure Tools

| Tool | Purpose |
|------|---------|
| **Docker** | Containerization |
| **Kubernetes** | Orchestration |
| **Terraform** | Infrastructure as code |

---

## Development Setup

### Terminal Setup

```
Shell: zsh with oh-my-zsh (or fish)
Terminal: iTerm2 (macOS), Alacritty, or Kitty
Multiplexer: tmux with sensible defaults
Prompt: Starship (fast, cross-shell)
```

### Editor Setup Options

**Option 1: Neovim (steep learning curve, high ceiling)**
- Use LazyVim or AstroNvim as a starting config
- LSP support for all three languages
- Fast, runs everywhere

**Option 2: VSCode (lower barrier, still powerful)**
- C++: clangd extension
- Rust: rust-analyzer
- Go: gopls (official Go extension)

### Language-Specific Setup

**C++:**
```
Compiler: clang (for better error messages)
Build: CMake + Ninja
Linting: clang-tidy
Formatting: clang-format
LSP: clangd
```

**Rust:**
```
Toolchain: rustup (manage versions)
LSP: rust-analyzer
Linting: clippy
Formatting: rustfmt
Testing: cargo test, cargo-nextest
```

**Go:**
```
Version: latest stable via official installer
LSP: gopls
Linting: golangci-lint (aggregates many linters)
Formatting: gofmt/goimports
```

---

## Project Progression

Each language guide includes a detailed project progression from Level 1 (CLI foundations) through Level 5 (advanced systems), plus a 6-month capstone project:

| Language | Capstone Project | Focus |
|----------|------------------|-------|
| **C++** | MiniDB | Database engine with B+ trees, buffer pool, query execution, transactions, recovery |
| **Rust** | TinyKV | Distributed KV store with Raft consensus, MVCC, async networking |
| **Go** | Launchpad | Platform-as-a-Service with REST APIs, Kubernetes operators, real-time features |

See the individual language guides for complete project progressions:
- [C++ Projects](./becoming-cracked-at-cpp.md#project-progression)
- [Rust Projects](./becoming-cracked-at-rust.md#project-progression)
- [Go Projects](./becoming-cracked-at-go.md#project-progression)

---

## Cross-Language Projects

These are larger projects you can implement in multiple languages to compare them:

### Project: `raft-consensus`

Implement the Raft consensus algorithm:
- Leader election
- Log replication
- Safety guarantees

**Do this in:** Go (natural fit), then Rust (harder but educational)

**Resource:** The Raft paper is very readable

---

### Project: `shell`

Build a Unix shell:
- Parse commands, pipes, redirections
- Job control (fg, bg, jobs)
- Built-in commands (cd, export)

**Do this in:** C++ (traditional), then Rust (compare memory handling)

---

### Project: `load-balancer`

Layer 7 (HTTP) load balancer:
- Multiple backend servers
- Health checks
- Round-robin, least-connections, consistent hashing

**Do this in:** Go (production-ready), then Rust (performance comparison)

---

## Learning Resources

### YouTube Channels

| Channel | Focus |
|---------|-------|
| **Jon Gjengset** | Deep Rust systems programming |
| **CppCon** | C++ talks from experts |
| **GopherCon** | Go conference talks |
| **Computerphile** | General CS concepts |
| **MIT OpenCourseWare** | OS, distributed systems lectures |

### Online Resources

**Systems Programming:**
- Julia Evans' zines (Linux, networking, debugging)
- Brendan Gregg's blog (performance, tracing)
- The Morning Paper (research papers explained)

**General:**
- Compiler Explorer (godbolt.org) - see assembly
- cppreference.com - C++ reference
- doc.rust-lang.org - Rust documentation
- go.dev/doc - Go documentation

*See individual language guides for language-specific resources, talks, and open source projects to study.*

---

## Daily Habits

1. **Read code daily** - 30 min reading expert code
2. **Use Compiler Explorer** - understand what your code becomes
3. **Profile before optimizing** - data over intuition
4. **Write, then simplify** - first make it work, then make it clean
5. **Document your learnings** - blog, notes, or teach others

---

## 18-Month Schedule

This schedule assumes starting with Rust, then adding Go, then C++. Adjust based on your chosen path.

| Months | Focus | Core Books | Project Focus |
|--------|-------|------------|---------------|
| 1-2 | Foundations | CSAPP Ch 1-6, OSTEP Part 1 | Read, understand systems |
| 3-6 | First Language | Language-specific (see guide) | Capstone Phase 1-3 |
| 7-9 | Systems Depth | TLPI selected, DDIA Part 1 | Capstone Phase 4-6 |
| 9-12 | Second Language | Language-specific (see guide) | Cross-language projects |
| 12-15 | Distributed Systems | DDIA Part 2-3, SRE book | Advanced projects |
| 15-18 | Third Language + Specialization | Language-specific + specialty | Capstone in new language |

**Recommended Paths:**

| Path | Month 3-6 | Month 9-12 | Month 15-18 |
|------|-----------|------------|-------------|
| **Systems Focus** | Rust (TinyKV) | C++ (MiniDB) | Go (infra tools) |
| **Cloud Native** | Go (Launchpad) | Rust (systems depth) | C++ (performance) |
| **Performance** | C++ (MiniDB) | Rust (TinyKV) | Go (production systems) |

*See individual language guides for detailed 12-month schedules within each language.*

---

## Project Tips

1. **Don't use frameworks initially** - Build HTTP servers without Actix/Axum/Gin at first. Understand the protocol.

2. **Read before you build** - Before building mini-redis, read through the actual Redis source or the Tokio mini-redis code.

3. **Benchmark your work** - Profile your projects. Find bottlenecks. This teaches you more than building.

4. **Write tests** - Test edge cases. What happens when disk is full? Network drops? OOM?

5. **Document design decisions** - Write a small README explaining why you made certain choices.

6. **Iterate** - First version can be ugly. Refactor once it works. Third time, make it elegant.

---

## The Honest Truth

Becoming "cracked" is a multi-year journey. There are no shortcuts, but there are force multipliers:

- Consistent daily practice beats sporadic marathons
- Working on real problems beats contrived exercises
- Reading expert code accelerates learning
- Having mentors or a community helps immensely

The fact that you're choosing systems languages (C++, Rust, Go) rather than only high-level ones suggests you want to understand how computers actually work. That foundation will serve you well across your entire career.

---

*Generated: January 2026*
