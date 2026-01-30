# Becoming a Cracked Systems/Infrastructure Developer

A comprehensive guide to mastering C++, Rust, and Go for infrastructure and systems programming.

---

## Table of Contents

1. [Core Philosophy](#core-philosophy)
2. [Language-Specific Guidance](#language-specific-guidance)
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

## Language-Specific Guidance

### C++

**The mountain to climb:** C++ is vast and complex. Mastery takes years.

**Foundational concepts to internalize:**
- Memory layout (stack vs heap, alignment, padding)
- RAII - resource management through object lifetime
- Value categories (lvalues, rvalues, xvalues) and move semantics
- Templates deeply - not just usage, but how they're instantiated
- Undefined behavior - what it is and why it exists

**Modern C++ essentials (C++17/20/23):**
- `constexpr` everything possible
- Concepts for cleaner template constraints
- Ranges and views
- `std::optional`, `std::variant`, `std::expected`

**Practice:**
- Implement data structures from scratch (vector, map, smart pointers)
- Write a memory allocator
- Build something with templates that actually requires them

---

### Rust

**The paradigm shift:** Rust will rewire how you think about memory safety.

**The ownership system (this is everything):**
- Ownership, borrowing, lifetimes - until it's intuitive
- Why the borrow checker rejects certain patterns
- Interior mutability (`RefCell`, `Cell`, `Mutex`)

**Key concepts:**
- Traits as the composition mechanism
- Error handling with `Result` and `?` operator
- Iterators and zero-cost abstractions
- When and why to use `unsafe`

**Advanced territory:**
- Procedural macros
- Async/await and pinning
- `Send` and `Sync` traits for concurrency
- FFI with C

**Practice:**
- Rewrite something you built in C++ in Rust
- Fight the borrow checker until you understand why it's right
- Contribute to a Rust open source project

---

### Go

**The simplicity trap:** Go looks simple but has hidden depth in concurrency and idioms.

**Core mental models:**
- Goroutines are cheap - use them freely
- Channels for communication, not shared memory
- Interfaces are implicit - design around behaviors
- Error handling is explicit and that's intentional

**What separates good from great:**
- Context for cancellation and timeouts
- Understanding the scheduler
- Knowing when NOT to use channels (mutexes are fine)
- Profiling with pprof

**Practice:**
- Build concurrent systems (web servers, workers, pipelines)
- Profile and optimize real code
- Read the `net/http` and `sync` package source

---

## Books: The Foundation

### Systems Programming Fundamentals

| Book | Focus |
|------|-------|
| **"Operating Systems: Three Easy Pieces"** (free online) | OS concepts - processes, memory, concurrency |
| **"Computer Systems: A Programmer's Perspective" (CSAPP)** | How code actually runs on hardware |
| **"The Linux Programming Interface"** by Michael Kerrisk | Linux systems programming bible |
| **"Linux Kernel Development"** by Robert Love | Kernel internals |

### C++

| Book | Level |
|------|-------|
| **"C++ Primer" (5th ed)** by Lippman | Foundational |
| **"Effective Modern C++"** by Scott Meyers | Intermediate (mandatory) |
| **"C++ Concurrency in Action"** by Anthony Williams | Concurrency |
| **"Modern C++ Systems Programming"** by Luis C. Miller | Advanced systems |

### Rust

| Book | Level |
|------|-------|
| **"The Rust Programming Language"** (The Book, free) | Foundational |
| **"Programming Rust" (3rd ed)** by Blandy & Orendorff | Comprehensive |
| **"Rust for Rustaceans"** by Jon Gjengset | Intermediate-Advanced |
| **"Rust Atomics and Locks"** by Mara Bos | Concurrency |

### Go

| Book | Level |
|------|-------|
| **"The Go Programming Language"** by Donovan & Kernighan | Foundational |
| **"System Programming Essentials with Go"** | Systems focus |
| **"Mastering Go"** by Mihalis Tsoukalos | Advanced |
| **"Concurrency in Go"** by Katherine Cox-Buday | Concurrency patterns |

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

Pick ONE language to master first. Here's the reading order for each:

#### Path A: Rust First (Recommended)

| Order | Book | What You'll Learn |
|-------|------|-------------------|
| 1 | **"The Rust Programming Language"** (The Book) | Ownership, borrowing, lifetimes, core syntax |
| 2 | **"Rust by Example"** (online, alongside The Book) | Practical patterns |
| 3 | **"Programming Rust" (3rd ed)** Chapters 1-12 | Deeper understanding, more idiomatic patterns |
| 4 | **"Rust for Rustaceans"** Chapters 1-5 | Mental models, unsafe, macros |

**Why Rust first:** The ownership system forces you to think about memory correctly. These habits transfer to C++ and even help you appreciate Go's simplicity.

#### Path B: C++ First

| Order | Book | What You'll Learn |
|-------|------|-------------------|
| 1 | **"C++ Primer" (5th ed)** Chapters 1-12 | Core language, containers, classes |
| 2 | **"Effective Modern C++"** (all items) | Modern idioms, move semantics, smart pointers |
| 3 | **"C++ Primer"** Chapters 13-16 | Copy control, OOP, templates |
| 4 | **"C++ Concurrency in Action"** Chapters 1-5 | Threading, atomics, synchronization |

#### Path C: Go First

| Order | Book | What You'll Learn |
|-------|------|-------------------|
| 1 | **"The Go Programming Language"** Chapters 1-7 | Core language, functions, methods, interfaces |
| 2 | **"Effective Go"** (online) | Idiomatic Go |
| 3 | **"The Go Programming Language"** Chapters 8-9 | Goroutines, channels, concurrency |
| 4 | **"Concurrency in Go"** | Advanced concurrency patterns |

---

### Phase 3: Systems Programming Depth (Months 6-9)

| Order | Book | Focus |
|-------|------|-------|
| 1 | **"The Linux Programming Interface"** Chapters 1-13, 23-33, 56-61 | File I/O, processes, signals, sockets |
| 2 | **"TCP/IP Sockets in C"** or equivalent in your language | Network programming |
| 3 | **"Rust Atomics and Locks"** OR **"C++ Concurrency in Action"** (remaining) | Low-level concurrency |

---

### Phase 4: Second Language (Months 9-12)

Now add your second language. You can move faster because you have foundations:

| If you started with | Add next | Key reading |
|---------------------|----------|-------------|
| Rust | C++ | "C++ Primer" (condensed), "Effective Modern C++" |
| Rust | Go | "The Go Programming Language" (you'll fly through it) |
| C++ | Rust | "The Book" + "Programming Rust" (focus on ownership) |
| C++ | Go | "The Go Programming Language" |
| Go | Rust | "The Book" + "Rust for Rustaceans" |
| Go | C++ | "C++ Primer", "Effective Modern C++" |

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

Projects are organized by complexity. Complete them in order within each language.

### Rust Projects

#### Level 1: CLI Foundations

**Project: `minigrep`** (from The Book, then extend it)
- Search for patterns in files
- Add: regex support, colored output, `.gitignore` respect
- **Concepts:** File I/O, error handling, iterators, CLI args

**Project: `file-renamer`**
- Bulk rename files with patterns (like `rename 's/old/new/' *.txt`)
- Add: dry-run mode, undo capability, recursive
- **Concepts:** Filesystem operations, regex, user interaction

#### Level 2: Data Structures & Algorithms

**Project: `mini-db`**
- Simple key-value store with persistence
- Commands: `get`, `set`, `delete`, `list`
- Store data in a log-structured format on disk
- **Concepts:** Serialization, file formats, basic storage engines

**Project: `lru-cache`**
- Implement LRU cache with O(1) operations
- Add: TTL support, size limits, thread-safe version
- **Concepts:** Data structures, unsafe Rust (for intrusive lists), concurrency

#### Level 3: Networking

**Project: `mini-redis`**
- TCP server implementing subset of Redis protocol
- Commands: `PING`, `GET`, `SET`, `DEL`, `EXPIRE`
- Add: persistence, pub/sub
- **Concepts:** Async I/O (tokio), protocol parsing, state management
- **Resource:** Tokio's mini-redis tutorial is excellent

**Project: `http-server`**
- HTTP/1.1 server from scratch (no frameworks)
- Serve static files, handle routing
- Add: middleware, logging, graceful shutdown
- **Concepts:** HTTP protocol, async networking, connection handling

#### Level 4: Systems

**Project: `mini-container`**
- Linux container runtime (like a tiny Docker)
- Use namespaces, cgroups, chroot
- Run isolated processes
- **Concepts:** Linux syscalls, process isolation, FFI

**Project: `log-structured-storage`**
- Implement a log-structured merge tree (LSM tree)
- Memtable, SSTables, compaction
- **Concepts:** Storage engines, write-ahead logs, data structures

---

### Go Projects

#### Level 1: CLI & Concurrency Basics

**Project: `parallel-downloader`**
- Download multiple URLs concurrently
- Show progress bars, handle failures gracefully
- Add: retry logic, rate limiting
- **Concepts:** Goroutines, channels, WaitGroups, HTTP client

**Project: `file-watcher`**
- Watch directories for changes, run commands on change
- Like a simple `nodemon` or `watchexec`
- **Concepts:** Filesystem events, process execution, signal handling

#### Level 2: Networking Services

**Project: `url-shortener`**
- HTTP API to create and resolve short URLs
- Persistence with SQLite or BoltDB
- Add: analytics, rate limiting, expiration
- **Concepts:** HTTP servers, databases, middleware

**Project: `chat-server`**
- WebSocket-based chat rooms
- Multiple rooms, user nicknames, message history
- **Concepts:** WebSockets, concurrent state, pub/sub patterns

#### Level 3: Distributed Systems

**Project: `distributed-kv`**
- Key-value store running on multiple nodes
- Implement consistent hashing for partitioning
- Handle node failures gracefully
- **Concepts:** Distributed systems, consensus basics, network partitions

**Project: `job-queue`**
- Distributed task queue (like a mini Celery/Sidekiq)
- Workers pull jobs, at-least-once delivery
- Add: priorities, retries, dead letter queue
- **Concepts:** Message queues, worker patterns, reliability

#### Level 4: Infrastructure Tools

**Project: `mini-terraform`**
- Declarative infrastructure tool for Docker containers
- YAML/JSON config → desired state
- Plan → Apply workflow
- **Concepts:** Declarative vs imperative, state management, reconciliation loops

**Project: `service-mesh-sidecar`**
- Proxy that handles service-to-service communication
- Load balancing, retries, circuit breaking
- **Concepts:** Reverse proxies, observability, resilience patterns

---

### C++ Projects

#### Level 1: Memory & Data Structures

**Project: `custom-vector`**
- Implement `std::vector` from scratch
- Growth strategy, move semantics, exception safety
- **Concepts:** Memory allocation, RAII, copy/move

**Project: `smart-pointers`**
- Implement `unique_ptr` and `shared_ptr`
- Thread-safe reference counting for shared_ptr
- **Concepts:** Ownership, move semantics, atomic operations

#### Level 2: Systems Programming

**Project: `memory-allocator`**
- Custom malloc/free implementation
- Try different strategies: first-fit, best-fit, buddy allocator
- Add: thread-local caches
- **Concepts:** Memory management, fragmentation, performance

**Project: `thread-pool`**
- Work-stealing thread pool
- Submit tasks, get futures back
- Add: priority queues, task cancellation
- **Concepts:** Concurrency, lock-free programming, futures/promises

#### Level 3: Networking & I/O

**Project: `epoll-server`**
- High-performance TCP server using epoll
- Handle thousands of concurrent connections
- **Concepts:** Non-blocking I/O, event loops, system calls

**Project: `rpc-framework`**
- Simple RPC framework with protobuf or custom serialization
- Client stubs, server skeletons, connection pooling
- **Concepts:** Serialization, code generation, network protocols

#### Level 4: Advanced Systems

**Project: `mini-database`**
- Simple SQL database with B-tree storage
- Parser → Planner → Executor pipeline
- Add: indexes, basic joins
- **Concepts:** Storage engines, query planning, B-trees

**Project: `jit-compiler`**
- JIT compile a simple expression language
- Use LLVM or write raw machine code
- **Concepts:** Compilers, code generation, CPU architecture

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

### Online Resources

- **Rust:** Rustlings (exercises), Rust by Example
- **Go:** Go by Example, Effective Go, Go Time podcast
- **C++:** cppreference.com, C++ Core Guidelines
- **Systems:** Julia Evans' zines, Brendan Gregg's blog (performance)

### Open Source Projects to Study & Contribute

#### Rust
- **Tokio** - async runtime
- **ripgrep** - fast grep (excellent code)
- **Nushell** - modern shell

#### Go
- **Docker/Moby** - containerization
- **Kubernetes** - orchestration
- **etcd** - distributed KV store
- **CockroachDB** - distributed SQL

#### C++
- **LLVM** - compiler infrastructure
- **gRPC** - RPC framework
- **Folly** - Facebook's C++ library

---

## Daily Habits

1. **Read code daily** - 30 min reading expert code
2. **Use Compiler Explorer** - understand what your code becomes
3. **Profile before optimizing** - data over intuition
4. **Write, then simplify** - first make it work, then make it clean
5. **Document your learnings** - blog, notes, or teach others

---

## 18-Month Schedule

| Months | Focus | Books | Projects |
|--------|-------|-------|----------|
| 1-2 | Foundations | CSAPP Ch 1-6, OSTEP Part 1 | — |
| 3-4 | Rust basics | The Book, Programming Rust | minigrep, file-renamer |
| 5-6 | Rust depth | Rust for Rustaceans | mini-db, lru-cache |
| 7-8 | Systems + Networking | TLPI selected, Rust Atomics | mini-redis, http-server |
| 9-10 | Go basics | GOPL, Effective Go | parallel-downloader, url-shortener |
| 11-12 | Distributed systems | DDIA Part 1-2 | distributed-kv, chat-server |
| 13-14 | C++ basics | C++ Primer, Effective Modern | custom-vector, thread-pool |
| 15-16 | Infrastructure | DDIA Part 3, SRE book | job-queue, mini-terraform |
| 17-18 | Capstone | Remaining reading | raft-consensus or shell |

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
