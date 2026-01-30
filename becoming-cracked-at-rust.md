# Becoming Cracked at Rust

A comprehensive guide to mastering Rust for systems programming, infrastructure, and high-performance applications.

---

## Table of Contents

1. [Why Rust](#why-rust)
2. [Core Mental Models](#core-mental-models)
3. [Books: The Foundation](#books-the-foundation)
4. [Structured Reading Path](#structured-reading-path)
5. [Video Resources](#video-resources)
6. [Tools: Your Arsenal](#tools-your-arsenal)
7. [Development Setup](#development-setup)
8. [The Ownership System Deep Dive](#the-ownership-system-deep-dive)
9. [The Distributed KV Store Project](#the-distributed-kv-store-project)
   - [Phase 1: Storage Engine](#phase-1-storage-engine-month-7)
   - [Phase 2: Network Layer](#phase-2-network-layer-month-8)
   - [Phase 3: Raft Consensus](#phase-3-raft-consensus-month-9)
   - [Phase 4: Distributed Transactions](#phase-4-distributed-transactions-month-10)
   - [Phase 5: Client Library & CLI](#phase-5-client-library--cli-month-11)
   - [Phase 6: Production Hardening](#phase-6-production-hardening-month-12)
10. [Project Progression](#project-progression)
11. [Open Source Study](#open-source-study)
12. [Common Pitfalls](#common-pitfalls)
13. [Daily Habits](#daily-habits)
14. [12-Month Schedule](#12-month-schedule)
15. [The Path to Cracked](#the-path-to-cracked)

---

## Why Rust

Rust offers what no other language does: **memory safety without garbage collection**.

- **Zero-cost abstractions** - High-level code compiles to efficient machine code
- **Memory safety guaranteed** - No null pointers, no dangling references, no data races
- **Fearless concurrency** - The compiler prevents race conditions
- **Modern tooling** - Cargo, rustfmt, clippy, rust-analyzer are excellent
- **Growing ecosystem** - Web (Axum, Actix), CLI (clap), async (Tokio), embedded, WASM

Rust powers: Firefox components, Dropbox's storage, Discord's read states, Cloudflare's edge, AWS Firecracker, Linux kernel modules, and an explosion of infrastructure tools.

**The honest truth:** Rust has a steep learning curve. The borrow checker will fight you. But once it clicks, you'll write concurrent code with confidence you never had before. The compiler catches bugs that would take days to debug in C++.

---

## Core Mental Models

### 1. Ownership - One Owner, Always

Every value in Rust has exactly one owner. When the owner goes out of scope, the value is dropped.

```rust
fn main() {
    let s1 = String::from("hello");  // s1 owns the String
    let s2 = s1;                      // Ownership moves to s2
    // println!("{}", s1);            // Error! s1 no longer valid

    let s3 = s2.clone();              // Deep copy - s2 and s3 both valid
    println!("{} {}", s2, s3);        // Works
}

// When s2 and s3 go out of scope, their Strings are dropped
```

**Why this matters:** No double-free, no use-after-free, no memory leaks (mostly). The compiler enforces it.

### 2. Borrowing - References Without Ownership

You can borrow a value without taking ownership. Two rules:
1. You can have **either** one mutable reference **or** any number of immutable references
2. References must always be valid (no dangling)

```rust
fn main() {
    let mut s = String::from("hello");

    // Multiple immutable borrows - OK
    let r1 = &s;
    let r2 = &s;
    println!("{} {}", r1, r2);

    // Mutable borrow - OK (r1, r2 no longer used)
    let r3 = &mut s;
    r3.push_str(" world");
    println!("{}", r3);

    // This would fail:
    // let r4 = &s;
    // let r5 = &mut s;  // Error! Can't have mutable while immutable exists
}

fn calculate_length(s: &String) -> usize {
    s.len()  // Borrows s, doesn't take ownership
}
```

### 3. Lifetimes - How Long References Live

Lifetimes ensure references don't outlive the data they point to.

```rust
// This won't compile - dangling reference
fn bad() -> &String {
    let s = String::from("hello");
    &s  // Error! s is dropped, reference would dangle
}

// Lifetime annotation: 'a says "the return value lives as long as the input"
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

// Structs holding references need lifetimes
struct Excerpt<'a> {
    part: &'a str,
}

impl<'a> Excerpt<'a> {
    fn level(&self) -> i32 {
        3  // Doesn't use self.part, no lifetime issues
    }

    fn announce(&self, announcement: &str) -> &str {
        println!("Attention: {}", announcement);
        self.part  // Returns reference with lifetime 'a
    }
}
```

**The key insight:** Lifetimes are about proving to the compiler that references are valid. They don't change runtime behavior.

### 4. Traits - Behavior Over Inheritance

Rust has no inheritance. Instead, traits define shared behavior.

```rust
// Define a trait
trait Summary {
    fn summarize(&self) -> String;

    // Default implementation
    fn summarize_author(&self) -> String {
        String::from("(Anonymous)")
    }
}

// Implement for types
struct Article {
    headline: String,
    content: String,
}

impl Summary for Article {
    fn summarize(&self) -> String {
        format!("{}: {}", self.headline, &self.content[..50])
    }
}

// Trait bounds
fn notify(item: &impl Summary) {
    println!("Breaking: {}", item.summarize());
}

// More explicit syntax
fn notify_verbose<T: Summary>(item: &T) {
    println!("Breaking: {}", item.summarize());
}

// Multiple bounds
fn complex<T: Summary + Clone>(item: &T) { }

// Where clauses for readability
fn complex_where<T, U>(t: &T, u: &U)
where
    T: Summary + Clone,
    U: Clone + Debug,
{ }
```

### 5. Error Handling - Result and Option

No exceptions. Errors are values you must handle.

```rust
use std::fs::File;
use std::io::{self, Read};

// Option for nullable values
fn find_user(id: u32) -> Option<User> {
    if id == 0 {
        None
    } else {
        Some(User { id })
    }
}

// Result for operations that can fail
fn read_file(path: &str) -> Result<String, io::Error> {
    let mut file = File::open(path)?;  // ? propagates errors
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    Ok(contents)
}

// Pattern matching for handling
fn process() {
    match read_file("config.txt") {
        Ok(contents) => println!("{}", contents),
        Err(e) => eprintln!("Error: {}", e),
    }

    // Or use combinators
    let contents = read_file("config.txt")
        .unwrap_or_else(|_| String::from("default"));

    // For Option
    let user = find_user(1)
        .map(|u| u.name)
        .unwrap_or_default();
}
```

### 6. Enums - Algebraic Data Types

Rust enums are sum types - they can hold different variants with different data.

```rust
// Simple enum
enum Direction {
    North,
    South,
    East,
    West,
}

// Enum with data
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(u8, u8, u8),
}

// Pattern matching
fn process_message(msg: Message) {
    match msg {
        Message::Quit => println!("Quitting"),
        Message::Move { x, y } => println!("Moving to ({}, {})", x, y),
        Message::Write(text) => println!("Writing: {}", text),
        Message::ChangeColor(r, g, b) => println!("Color: #{:02x}{:02x}{:02x}", r, g, b),
    }
}

// Option and Result are just enums!
enum Option<T> {
    Some(T),
    None,
}

enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

### 7. Zero-Cost Abstractions

High-level Rust compiles to efficient machine code.

```rust
// Iterators are zero-cost
let sum: i32 = (0..1000)
    .filter(|x| x % 2 == 0)
    .map(|x| x * x)
    .sum();
// Compiles to the same code as a hand-written loop

// Generics are monomorphized - no runtime cost
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list {
        if item > largest {
            largest = item;
        }
    }
    largest
}
// Separate versions generated for each type used
```

---

## Books: The Foundation

### Essential (Read in Order)

| Order | Book | Focus | Why |
|-------|------|-------|-----|
| 1 | **"The Rust Programming Language"** (The Book, free) | Complete language coverage | THE Rust book. Start here. Read it twice. |
| 2 | **"Programming Rust" (3rd ed)** by Blandy, Orendorff, Tindall | Comprehensive deep dive | More depth than The Book, excellent explanations. |
| 3 | **"Rust for Rustaceans"** by Jon Gjengset | Intermediate to advanced | Takes you from competent to expert. |

### Concurrency & Async

| Book | Focus | When to Read |
|------|-------|--------------|
| **"Rust Atomics and Locks"** by Mara Bos (free) | Low-level concurrency | After basics, essential for systems |
| **"Asynchronous Programming in Rust"** | Async/await, Tokio | When building async services |

### Systems Programming

| Book | Focus | When to Read |
|------|-------|--------------|
| **"Command-Line Rust"** by Ken Youens-Clark | CLI tools | Great first project book |
| **"Zero To Production In Rust"** by Luca Palmieri | Web backends | Building production services |
| **"Rust in Action"** by Tim McNamara | Systems programming | Practical systems projects |

### Advanced

| Book | Focus | When to Read |
|------|-------|--------------|
| **"The Rustonomicon"** (free) | Unsafe Rust | When you need unsafe |
| **"Rust Design Patterns"** (free) | Idiomatic patterns | After intermediate level |
| **"Rust API Guidelines"** (free) | API design | When building libraries |

### Supporting Books (Not Rust-specific)

| Book | Focus |
|------|-------|
| **"Designing Data-Intensive Applications"** | Distributed systems |
| **"Computer Systems: A Programmer's Perspective"** | How code runs |
| **"Operating Systems: Three Easy Pieces"** | OS concepts |

---

## Structured Reading Path

### Phase 1: Language Fundamentals (Weeks 1-6)

**Primary: "The Rust Programming Language" (The Book)**

| Week | Chapters | Focus | Practice |
|------|----------|-------|----------|
| 1 | Ch 1-4 | Setup, basics, ownership | Guessing game, small programs |
| 2 | Ch 5-6 | Structs, enums, pattern matching | Model real domain with types |
| 3 | Ch 7-8 | Modules, collections | Build a project with modules |
| 4 | Ch 9-10 | Errors, generics, traits | Implement common traits |
| 5 | Ch 11-12 | Testing, CLI project | Complete minigrep project |
| 6 | Ch 13-15 | Closures, iterators, smart pointers | Refactor with iterators |

**Supplement with:**
- Rustlings (exercises)
- Rust by Example (online)
- Exercism Rust track

### Phase 2: Intermediate Rust (Weeks 7-12)

**Primary: "Programming Rust" (3rd ed) + The Book Ch 16-20**

| Week | Focus | Chapters |
|------|-------|----------|
| 7 | Ownership deep dive | PR Ch 4-5 |
| 8 | Traits and generics | PR Ch 11-12 |
| 9 | Concurrency basics | Book Ch 16, PR Ch 19 |
| 10 | Smart pointers, interior mutability | PR Ch 9-10 |
| 11 | Unsafe Rust | Book Ch 19, PR Ch 22 |
| 12 | Macros | Book Ch 19, PR Ch 21 |

### Phase 3: Advanced Rust (Weeks 13-16)

**Primary: "Rust for Rustaceans"**

| Week | Chapters | Focus |
|------|----------|-------|
| 13 | Ch 1-3 | Foundations, types, designing interfaces |
| 14 | Ch 4-6 | Error handling, project structure, testing |
| 15 | Ch 7-9 | Macros, async, unsafe |
| 16 | Ch 10-11 | Concurrency, FFI |

### Phase 4: Async & Concurrency Deep Dive (Weeks 17-20)

**Primary: "Rust Atomics and Locks" + async resources**

| Week | Focus |
|------|-------|
| 17 | Atomics and memory ordering |
| 18 | Locks and condition variables |
| 19 | Lock-free data structures |
| 20 | Async/await, Tokio fundamentals |

### Phase 5: Production Rust (Weeks 21-24)

**Primary: "Zero To Production In Rust" (selected) + Tokio docs**

| Week | Focus |
|------|-------|
| 21 | HTTP servers, middleware |
| 22 | Database integration, testing |
| 23 | Observability, deployment |
| 24 | Production patterns, error handling at scale |

---

## Video Resources

### YouTube Channels

| Channel | Content |
|---------|---------|
| **Jon Gjengset** | Deep Rust systems programming, implementing data structures |
| **Let's Get Rusty** | Tutorials, news |
| **No Boilerplate** | Conceptual Rust videos |
| **Rust Videos** | Conference talks |
| **fasterthanlime** | Deep dives |

### Must-Watch Talks

**Fundamentals:**
- "Rust: A Language for the Next 40 Years" - Carol Nichols
- "Considering Rust" - Jon Gjengset
- "The Why, What, and How of Pinning" - Jon Gjengset

**Ownership & Borrowing:**
- "Rust's Journey to Async/Await" - Steve Klabnik
- "Understanding Ownership" - Various
- "Lifetime Annotations" - Various

**Concurrency:**
- "Lock-free to wait-free simulation in Rust" - Mara Bos
- "Rust Atomics and Locks" - Mara Bos (RustConf)
- "Fearless Concurrency in Your Microcontroller" - Various

**Systems:**
- "Is It Time to Rewrite the Operating System in Rust?" - Bryan Cantrill
- "Rust for Linux" - Various
- "Building on an Unsafe Foundation" - Various

**Async:**
- "Async Rust: Hurdles and Lessons" - Various
- "How Tokio Works" - Various

### Courses

| Course | Platform | Focus |
|--------|----------|-------|
| **Rustlings** | Free | Interactive exercises |
| **Exercism Rust Track** | Free | Mentored exercises |
| **Tour of Rust** | Free (online) | Interactive tutorial |
| **Ultimate Rust Crash Course** | Udemy | Quick intro |
| **Rust in Motion** | Manning | Video course |

---

## Tools: Your Arsenal

### Essential Tools

| Tool | Purpose | Install |
|------|---------|---------|
| **rustup** | Toolchain manager | curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh |
| **cargo** | Package manager, build tool | Comes with rustup |
| **rust-analyzer** | Language server | Editor plugin |
| **clippy** | Linter | rustup component add clippy |
| **rustfmt** | Formatter | rustup component add rustfmt |

### Debugging & Profiling

| Tool | Purpose |
|------|---------|
| **LLDB/GDB** | Debugging |
| **cargo-flamegraph** | Flamegraph profiling |
| **perf** | Linux profiling |
| **Instruments** | macOS profiling |
| **miri** | Undefined behavior detection |
| **cargo-valgrind** | Memory debugging |

### Testing & Quality

| Tool | Purpose |
|------|---------|
| **cargo test** | Built-in testing |
| **cargo-nextest** | Faster test runner |
| **cargo-tarpaulin** | Code coverage |
| **cargo-mutants** | Mutation testing |
| **criterion** | Benchmarking |

### Development

| Tool | Purpose |
|------|---------|
| **cargo-watch** | Auto-rebuild on change |
| **cargo-edit** | Add/remove dependencies easily |
| **cargo-expand** | Expand macros |
| **cargo-deny** | Dependency auditing |
| **cargo-udeps** | Find unused dependencies |
| **sccache** | Compilation caching |

### Async & Web

| Tool | Purpose |
|------|---------|
| **Tokio** | Async runtime |
| **Axum** | Web framework |
| **Actix-web** | Web framework |
| **sqlx** | Async SQL |
| **tonic** | gRPC |

---

## Development Setup

### Installation

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Add components
rustup component add clippy rustfmt rust-analyzer

# Useful cargo extensions
cargo install cargo-watch cargo-edit cargo-expand cargo-nextest
```

### Editor Setup

**VS Code (Recommended):**
```
1. Install "rust-analyzer" extension
2. Install "Even Better TOML" for Cargo.toml
3. Install "crates" for dependency management
4. Install "CodeLLDB" for debugging
```

**Neovim:**
```
Use LazyVim or custom config with:
- nvim-lspconfig with rust-analyzer
- nvim-dap with codelldb
- crates.nvim for Cargo.toml
```

### Project Structure

```
myproject/
├── Cargo.toml
├── Cargo.lock
├── src/
│   ├── main.rs          # Binary entry
│   ├── lib.rs           # Library root
│   ├── module/
│   │   ├── mod.rs
│   │   └── submodule.rs
│   └── bin/             # Additional binaries
│       └── tool.rs
├── tests/               # Integration tests
│   └── integration.rs
├── benches/             # Benchmarks
│   └── benchmark.rs
├── examples/            # Example code
│   └── example.rs
└── .cargo/
    └── config.toml      # Cargo config
```

### Cargo.toml Template

```toml
[package]
name = "myproject"
version = "0.1.0"
edition = "2021"
rust-version = "1.75"

[dependencies]
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
thiserror = "1"
anyhow = "1"
tracing = "0.1"

[dev-dependencies]
criterion = "0.5"
proptest = "1"
tokio-test = "0.4"

[[bench]]
name = "benchmark"
harness = false

[profile.release]
lto = true
codegen-units = 1

[lints.rust]
unsafe_code = "forbid"

[lints.clippy]
all = "warn"
pedantic = "warn"
nursery = "warn"
```

### .cargo/config.toml

```toml
[build]
rustflags = ["-D", "warnings"]

[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=lld"]
```

---

## The Ownership System Deep Dive

### When the Borrow Checker Fights You

Common patterns that confuse beginners and how to solve them:

**1. Borrowing from a collection while modifying**

```rust
// Won't compile
let mut vec = vec![1, 2, 3];
for item in &vec {
    if *item == 2 {
        vec.push(4);  // Error! Can't mutate while borrowed
    }
}

// Solution 1: Collect indices first
let indices: Vec<_> = vec.iter()
    .enumerate()
    .filter(|(_, &x)| x == 2)
    .map(|(i, _)| i)
    .collect();
for i in indices {
    vec.push(4);
}

// Solution 2: Use retain, drain, or other methods
vec.retain(|&x| x != 2);
```

**2. Self-referential structs**

```rust
// Won't compile - self-referential
struct Bad<'a> {
    data: String,
    reference: &'a str,  // Can't reference data
}

// Solution 1: Store indices instead
struct Good {
    data: String,
    start: usize,
    end: usize,
}

impl Good {
    fn reference(&self) -> &str {
        &self.data[self.start..self.end]
    }
}

// Solution 2: Use Pin and unsafe (advanced)
// Solution 3: Use crates like ouroboros or self_cell
```

**3. Returning references to local data**

```rust
// Won't compile
fn bad() -> &str {
    let s = String::from("hello");
    &s  // s is dropped!
}

// Solution: Return owned data
fn good() -> String {
    String::from("hello")
}

// Or take input and return reference with lifetime
fn better<'a>(s: &'a str) -> &'a str {
    &s[0..5]
}
```

**4. Multiple mutable references through different fields**

```rust
struct Foo {
    a: i32,
    b: i32,
}

// Won't compile with naive approach
fn bad(foo: &mut Foo) {
    let a = &mut foo.a;
    let b = &mut foo.b;  // Error! Two mutable borrows of foo
}

// Rust is smart enough to allow this actually!
fn good(foo: &mut Foo) {
    let a = &mut foo.a;
    let b = &mut foo.b;
    *a += *b;  // Works - different fields
}

// But not through methods
impl Foo {
    fn get_a(&mut self) -> &mut i32 { &mut self.a }
    fn get_b(&mut self) -> &mut i32 { &mut self.b }
}

fn bad_methods(foo: &mut Foo) {
    let a = foo.get_a();
    let b = foo.get_b();  // Error! Can't prove they're different
}
```

### Interior Mutability

When you need mutability behind an immutable reference:

```rust
use std::cell::{Cell, RefCell};
use std::sync::{Mutex, RwLock};

// Cell - for Copy types, single-threaded
struct Counter {
    value: Cell<i32>,
}

impl Counter {
    fn increment(&self) {  // Note: &self not &mut self
        self.value.set(self.value.get() + 1);
    }
}

// RefCell - for any type, runtime borrow checking, single-threaded
struct Cache {
    data: RefCell<HashMap<String, String>>,
}

impl Cache {
    fn get(&self, key: &str) -> Option<String> {
        self.data.borrow().get(key).cloned()
    }

    fn insert(&self, key: String, value: String) {
        self.data.borrow_mut().insert(key, value);
    }
}

// Mutex/RwLock - thread-safe interior mutability
struct SharedCache {
    data: Mutex<HashMap<String, String>>,
}

impl SharedCache {
    fn get(&self, key: &str) -> Option<String> {
        self.data.lock().unwrap().get(key).cloned()
    }
}
```

### Send and Sync

Traits that enable safe concurrency:

```rust
// Send: Safe to transfer between threads
// Most types are Send

// Sync: Safe to share references between threads
// T is Sync if &T is Send

// Rc is neither Send nor Sync (not thread-safe)
use std::rc::Rc;
let rc = Rc::new(5);
// std::thread::spawn(move || { println!("{}", rc); }); // Error!

// Arc is Send + Sync (thread-safe)
use std::sync::Arc;
let arc = Arc::new(5);
std::thread::spawn(move || { println!("{}", arc); }); // OK!

// RefCell is Send but not Sync (single-threaded mutation)
// Mutex<T> is Send + Sync if T is Send
```

---

## The Distributed KV Store Project

**What you're building:** A distributed key-value store with Raft consensus, similar to etcd or Consul's KV store.

**Why this project:** It combines everything:
- Ownership and lifetimes in complex data structures
- Async networking with Tokio
- Distributed systems concepts (consensus, replication)
- Production concerns (persistence, observability)

**Architecture Overview:**
```
┌─────────────────────────────────────────────────────────────────┐
│                        TinyKV                                    │
├─────────────────────────────────────────────────────────────────┤
│  CLI (tinykv)        │  Client Library     │  HTTP/gRPC API     │
├─────────────────────────────────────────────────────────────────┤
│                      Server                                      │
│  Request Router      │  Session Manager    │  Watch Streams     │
├─────────────────────────────────────────────────────────────────┤
│                      Raft Consensus                              │
│  Leader Election     │  Log Replication    │  Membership        │
├─────────────────────────────────────────────────────────────────┤
│                      State Machine                               │
│  KV Operations       │  Transactions       │  Leases            │
├─────────────────────────────────────────────────────────────────┤
│                      Storage Engine                              │
│  LSM Tree / B-Tree   │  WAL                │  Snapshots         │
└─────────────────────────────────────────────────────────────────┘
```

---

### Phase 1: Storage Engine (Month 7)

**Build:** Persistent key-value storage with write-ahead logging

**Features:**
- LSM tree or B-tree based storage
- Write-ahead log for durability
- Point lookups and range scans
- Compaction (for LSM)
- Snapshots

**Skills Learned:**
- File I/O in Rust
- Binary serialization (serde, bincode)
- Iterator design
- Error handling patterns

**Core Types:**

```rust
use std::path::Path;
use bytes::Bytes;

pub trait Storage: Send + Sync {
    fn get(&self, key: &[u8]) -> Result<Option<Bytes>>;
    fn put(&self, key: Bytes, value: Bytes) -> Result<()>;
    fn delete(&self, key: &[u8]) -> Result<()>;
    fn scan(&self, start: &[u8], end: &[u8]) -> Result<Box<dyn Iterator<Item = (Bytes, Bytes)>>>;
    fn flush(&self) -> Result<()>;
}

// Write-ahead log
pub struct Wal {
    file: std::fs::File,
    path: PathBuf,
}

impl Wal {
    pub fn open(path: impl AsRef<Path>) -> Result<Self>;
    pub fn append(&mut self, entry: &WalEntry) -> Result<u64>;
    pub fn sync(&self) -> Result<()>;
    pub fn replay(&self) -> Result<Vec<WalEntry>>;
}

#[derive(Serialize, Deserialize)]
pub struct WalEntry {
    pub sequence: u64,
    pub operation: Operation,
}

#[derive(Serialize, Deserialize)]
pub enum Operation {
    Put { key: Bytes, value: Bytes },
    Delete { key: Bytes },
}

// MemTable (in-memory sorted structure)
pub struct MemTable {
    data: BTreeMap<Bytes, Option<Bytes>>,  // None = tombstone
    size: usize,
}

impl MemTable {
    pub fn get(&self, key: &[u8]) -> Option<Option<&Bytes>>;
    pub fn put(&mut self, key: Bytes, value: Bytes);
    pub fn delete(&mut self, key: Bytes);
    pub fn iter(&self) -> impl Iterator<Item = (&Bytes, &Option<Bytes>)>;
}

// SSTable (sorted string table on disk)
pub struct SSTable {
    path: PathBuf,
    index: BTreeMap<Bytes, u64>,  // key -> offset
    bloom_filter: BloomFilter,
}

impl SSTable {
    pub fn create(path: impl AsRef<Path>, entries: impl Iterator<Item = (Bytes, Bytes)>) -> Result<Self>;
    pub fn get(&self, key: &[u8]) -> Result<Option<Bytes>>;
    pub fn iter(&self) -> Result<SSTableIterator>;
}
```

**Reading:**
- "Designing Data-Intensive Applications" Ch 3 (LSM trees)
- LevelDB design document
- RocksDB wiki

---

### Phase 2: Network Layer (Month 8)

**Build:** Async RPC framework for node communication

**Features:**
- TCP-based message passing
- Request/response and streaming
- Connection pooling
- Timeout and retry handling
- Graceful shutdown

**Skills Learned:**
- Tokio async runtime
- TCP networking
- Protocol design
- Connection management

**Core Types:**

```rust
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::{mpsc, oneshot};

// Message types
#[derive(Serialize, Deserialize)]
pub enum Message {
    // Raft messages
    RequestVote(RequestVoteArgs),
    RequestVoteResponse(RequestVoteResponse),
    AppendEntries(AppendEntriesArgs),
    AppendEntriesResponse(AppendEntriesResponse),

    // Client messages
    Get(GetRequest),
    Put(PutRequest),
    Delete(DeleteRequest),
}

// RPC client
pub struct RpcClient {
    addr: SocketAddr,
    connection: Option<TcpStream>,
}

impl RpcClient {
    pub async fn connect(addr: SocketAddr) -> Result<Self>;

    pub async fn call<R: DeserializeOwned>(
        &mut self,
        request: Message,
        timeout: Duration,
    ) -> Result<R>;
}

// RPC server
pub struct RpcServer {
    listener: TcpListener,
    handler: Arc<dyn MessageHandler>,
}

#[async_trait]
pub trait MessageHandler: Send + Sync {
    async fn handle(&self, message: Message) -> Result<Message>;
}

impl RpcServer {
    pub async fn bind(addr: SocketAddr, handler: Arc<dyn MessageHandler>) -> Result<Self>;
    pub async fn run(self) -> Result<()>;
}

// Connection pool
pub struct ConnectionPool {
    connections: Mutex<HashMap<SocketAddr, Vec<TcpStream>>>,
    max_per_peer: usize,
}

impl ConnectionPool {
    pub async fn get(&self, addr: SocketAddr) -> Result<PooledConnection>;
}
```

**Reading:**
- Tokio tutorial
- "Asynchronous Programming in Rust"

---

### Phase 3: Raft Consensus (Month 9)

**Build:** Raft consensus algorithm for leader election and log replication

**Features:**
- Leader election with randomized timeouts
- Log replication
- Safety guarantees
- Cluster membership changes
- Snapshotting

**Skills Learned:**
- Distributed consensus
- State machines
- Async coordination
- Testing distributed systems

**Core Types:**

```rust
use tokio::sync::{mpsc, watch};
use tokio::time::{interval, timeout};

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Role {
    Follower,
    Candidate,
    Leader,
}

pub struct RaftNode {
    // Persistent state
    current_term: u64,
    voted_for: Option<NodeId>,
    log: Vec<LogEntry>,

    // Volatile state
    commit_index: u64,
    last_applied: u64,
    role: Role,

    // Leader state
    next_index: HashMap<NodeId, u64>,
    match_index: HashMap<NodeId, u64>,

    // Configuration
    id: NodeId,
    peers: Vec<NodeId>,

    // Channels
    rpc_tx: mpsc::Sender<RpcMessage>,
    apply_tx: mpsc::Sender<ApplyMessage>,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct LogEntry {
    pub term: u64,
    pub index: u64,
    pub command: Command,
}

#[derive(Clone, Serialize, Deserialize)]
pub enum Command {
    Put { key: Bytes, value: Bytes },
    Delete { key: Bytes },
    Noop,
}

impl RaftNode {
    pub async fn new(
        id: NodeId,
        peers: Vec<NodeId>,
        storage: Box<dyn RaftStorage>,
    ) -> Result<Self>;

    // Main loop
    pub async fn run(&mut self) -> Result<()> {
        loop {
            match self.role {
                Role::Follower => self.run_follower().await?,
                Role::Candidate => self.run_candidate().await?,
                Role::Leader => self.run_leader().await?,
            }
        }
    }

    // Propose a new command (only leader)
    pub async fn propose(&mut self, command: Command) -> Result<u64>;

    // Handle incoming RPC
    pub async fn handle_request_vote(&mut self, args: RequestVoteArgs) -> RequestVoteResponse;
    pub async fn handle_append_entries(&mut self, args: AppendEntriesArgs) -> AppendEntriesResponse;
}

// RequestVote RPC
#[derive(Serialize, Deserialize)]
pub struct RequestVoteArgs {
    pub term: u64,
    pub candidate_id: NodeId,
    pub last_log_index: u64,
    pub last_log_term: u64,
}

#[derive(Serialize, Deserialize)]
pub struct RequestVoteResponse {
    pub term: u64,
    pub vote_granted: bool,
}

// AppendEntries RPC
#[derive(Serialize, Deserialize)]
pub struct AppendEntriesArgs {
    pub term: u64,
    pub leader_id: NodeId,
    pub prev_log_index: u64,
    pub prev_log_term: u64,
    pub entries: Vec<LogEntry>,
    pub leader_commit: u64,
}

#[derive(Serialize, Deserialize)]
pub struct AppendEntriesResponse {
    pub term: u64,
    pub success: bool,
    pub match_index: u64,
}
```

**Testing Raft:**

```rust
#[cfg(test)]
mod tests {
    use super::*;

    // Deterministic testing with simulated network
    struct TestCluster {
        nodes: Vec<RaftNode>,
        network: SimulatedNetwork,
    }

    impl TestCluster {
        fn new(size: usize) -> Self;
        async fn wait_for_leader(&mut self, timeout: Duration) -> Option<NodeId>;
        fn partition(&mut self, groups: Vec<Vec<NodeId>>);
        fn heal_partition(&mut self);
    }

    #[tokio::test]
    async fn test_leader_election() {
        let mut cluster = TestCluster::new(3);
        let leader = cluster.wait_for_leader(Duration::from_secs(5)).await;
        assert!(leader.is_some());
    }

    #[tokio::test]
    async fn test_leader_election_after_partition() {
        let mut cluster = TestCluster::new(5);
        let leader1 = cluster.wait_for_leader(Duration::from_secs(5)).await.unwrap();

        // Partition leader from majority
        cluster.partition(vec![vec![leader1], vec![/* other 4 */]]);

        // New leader should be elected
        let leader2 = cluster.wait_for_leader(Duration::from_secs(10)).await.unwrap();
        assert_ne!(leader1, leader2);
    }
}
```

**Reading:**
- The Raft paper (raft.github.io)
- Raft visualization (thesecretlivesofdata.com/raft)
- etcd's Raft implementation

---

### Phase 4: Distributed Transactions (Month 10)

**Build:** Multi-key transactions with MVCC

**Features:**
- Snapshot isolation
- Multi-version concurrency control
- Distributed transactions (2PC or Percolator-style)
- Conflict detection

**Skills Learned:**
- Transaction theory
- MVCC implementation
- Timestamp ordering
- Distributed coordination

**Core Types:**

```rust
pub type Timestamp = u64;

// MVCC value with version history
pub struct MvccValue {
    pub versions: BTreeMap<Timestamp, ValueVersion>,
}

pub enum ValueVersion {
    Value(Bytes),
    Tombstone,
}

// Transaction
pub struct Transaction {
    start_ts: Timestamp,
    writes: HashMap<Bytes, WriteOp>,
    reads: HashSet<Bytes>,
}

pub enum WriteOp {
    Put(Bytes),
    Delete,
}

impl Transaction {
    pub fn new(start_ts: Timestamp) -> Self;

    pub fn get(&mut self, key: &[u8]) -> Result<Option<Bytes>>;
    pub fn put(&mut self, key: Bytes, value: Bytes);
    pub fn delete(&mut self, key: Bytes);

    pub async fn commit(self) -> Result<Timestamp>;
    pub fn rollback(self);
}

// Transaction manager
pub struct TxnManager {
    storage: Arc<MvccStorage>,
    oracle: Arc<TimestampOracle>,
}

impl TxnManager {
    pub async fn begin(&self) -> Result<Transaction>;
    pub async fn commit(&self, txn: Transaction) -> Result<Timestamp>;
}

// Timestamp oracle (single source of timestamps)
pub struct TimestampOracle {
    current: AtomicU64,
}

impl TimestampOracle {
    pub fn get_timestamp(&self) -> Timestamp;
    pub fn get_timestamp_async(&self) -> impl Future<Output = Timestamp>;
}

// Percolator-style distributed transactions
pub struct DistributedTxn {
    start_ts: Timestamp,
    primary_key: Option<Bytes>,
    writes: HashMap<Bytes, WriteOp>,
}

impl DistributedTxn {
    // Two-phase commit
    pub async fn prewrite(&self, storage: &dyn Storage) -> Result<()>;
    pub async fn commit(&self, storage: &dyn Storage, commit_ts: Timestamp) -> Result<()>;
}
```

**Reading:**
- "Designing Data-Intensive Applications" Ch 7
- Percolator paper
- TiKV transaction design

---

### Phase 5: Client Library & CLI (Month 11)

**Build:** Client library and command-line interface

**Features:**
- Async client with connection pooling
- Automatic leader discovery
- Retry with backoff
- Watch functionality (streaming changes)
- CLI for operations

**Skills Learned:**
- Library API design
- CLI development (clap)
- Streaming patterns
- Error handling ergonomics

**Core Types:**

```rust
use clap::{Parser, Subcommand};
use tokio_stream::Stream;

// Client library
pub struct Client {
    cluster: Vec<SocketAddr>,
    leader: Arc<Mutex<Option<SocketAddr>>>,
    pool: ConnectionPool,
}

impl Client {
    pub async fn connect(cluster: Vec<SocketAddr>) -> Result<Self>;

    pub async fn get(&self, key: &[u8]) -> Result<Option<Bytes>>;
    pub async fn put(&self, key: Bytes, value: Bytes) -> Result<()>;
    pub async fn delete(&self, key: &[u8]) -> Result<()>;

    pub async fn scan(&self, start: &[u8], end: &[u8]) -> Result<Vec<(Bytes, Bytes)>>;

    // Transactions
    pub async fn txn(&self) -> Result<ClientTransaction>;

    // Watch for changes
    pub async fn watch(&self, prefix: &[u8]) -> Result<impl Stream<Item = WatchEvent>>;
}

pub struct ClientTransaction {
    client: Client,
    txn_id: u64,
    writes: Vec<WriteOp>,
}

impl ClientTransaction {
    pub async fn get(&mut self, key: &[u8]) -> Result<Option<Bytes>>;
    pub fn put(&mut self, key: Bytes, value: Bytes);
    pub fn delete(&mut self, key: Bytes);
    pub async fn commit(self) -> Result<()>;
}

#[derive(Debug)]
pub struct WatchEvent {
    pub key: Bytes,
    pub value: Option<Bytes>,
    pub revision: u64,
    pub event_type: EventType,
}

#[derive(Debug)]
pub enum EventType {
    Put,
    Delete,
}

// CLI
#[derive(Parser)]
#[command(name = "tinykv")]
#[command(about = "TinyKV command-line client")]
pub struct Cli {
    #[arg(long, default_value = "127.0.0.1:5000")]
    endpoints: Vec<String>,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
pub enum Commands {
    Get { key: String },
    Put { key: String, value: String },
    Del { key: String },
    Scan { start: String, end: String },
    Watch { prefix: String },
    Member {
        #[command(subcommand)]
        action: MemberAction,
    },
}

#[derive(Subcommand)]
pub enum MemberAction {
    List,
    Add { addr: String },
    Remove { id: String },
}
```

**CLI Usage:**

```bash
# Basic operations
tinykv put mykey myvalue
tinykv get mykey
tinykv del mykey

# Range operations
tinykv scan "" ""  # All keys
tinykv scan "user/" "user0"  # Prefix scan

# Watch for changes
tinykv watch "config/"

# Cluster management
tinykv member list
tinykv member add 10.0.0.4:5000
tinykv member remove node-3
```

**Reading:**
- etcd client documentation
- Clap documentation

---

### Phase 6: Production Hardening (Month 12)

**Build:** Production-ready features

**Features:**
- Metrics (Prometheus)
- Distributed tracing
- Structured logging
- Graceful shutdown
- Health checks
- TLS support
- Benchmarking

**Skills Learned:**
- Observability
- Production operations
- Performance testing
- Security basics

**Core Types:**

```rust
use tracing::{info, instrument, span, Level};
use metrics::{counter, gauge, histogram};
use opentelemetry::trace::Tracer;

// Metrics
pub struct Metrics {
    requests_total: Counter,
    request_duration: Histogram,
    active_connections: Gauge,
    raft_term: Gauge,
    log_entries: Gauge,
}

impl Metrics {
    pub fn new() -> Self {
        Self {
            requests_total: counter!("tinykv_requests_total"),
            request_duration: histogram!("tinykv_request_duration_seconds"),
            active_connections: gauge!("tinykv_active_connections"),
            raft_term: gauge!("tinykv_raft_term"),
            log_entries: gauge!("tinykv_log_entries"),
        }
    }

    pub fn record_request(&self, method: &str, duration: Duration, success: bool) {
        self.requests_total.increment(1);
        self.request_duration.record(duration.as_secs_f64());
    }
}

// Instrumented operations
impl Server {
    #[instrument(skip(self))]
    pub async fn handle_get(&self, key: &[u8]) -> Result<Option<Bytes>> {
        let start = Instant::now();
        let result = self.storage.get(key).await;
        self.metrics.record_request("get", start.elapsed(), result.is_ok());
        result
    }
}

// Health check
pub struct HealthChecker {
    raft: Arc<RaftNode>,
    storage: Arc<dyn Storage>,
}

impl HealthChecker {
    pub async fn check(&self) -> HealthStatus {
        HealthStatus {
            healthy: self.raft.is_healthy() && self.storage.is_healthy(),
            is_leader: self.raft.is_leader(),
            term: self.raft.current_term(),
            commit_index: self.raft.commit_index(),
        }
    }
}

// Graceful shutdown
pub async fn run_server(config: Config) -> Result<()> {
    let (shutdown_tx, shutdown_rx) = tokio::sync::broadcast::channel(1);

    // Handle signals
    tokio::spawn(async move {
        tokio::signal::ctrl_c().await.unwrap();
        info!("Received shutdown signal");
        let _ = shutdown_tx.send(());
    });

    let server = Server::new(config).await?;

    tokio::select! {
        result = server.run() => result,
        _ = shutdown_rx.recv() => {
            info!("Shutting down gracefully");
            server.shutdown().await
        }
    }
}

// TLS configuration
pub struct TlsConfig {
    pub cert_path: PathBuf,
    pub key_path: PathBuf,
    pub ca_path: Option<PathBuf>,
}

impl Server {
    pub async fn with_tls(config: Config, tls: TlsConfig) -> Result<Self> {
        let cert = tokio::fs::read(&tls.cert_path).await?;
        let key = tokio::fs::read(&tls.key_path).await?;

        let identity = Identity::from_pem(cert, key);
        let tls_config = ServerTlsConfig::new().identity(identity);

        // ...
    }
}
```

**Benchmarking:**

```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion, Throughput};

fn bench_get(c: &mut Criterion) {
    let rt = tokio::runtime::Runtime::new().unwrap();
    let client = rt.block_on(Client::connect(vec!["127.0.0.1:5000".parse().unwrap()])).unwrap();

    // Populate data
    rt.block_on(async {
        for i in 0..10000 {
            client.put(format!("key{}", i).into(), b"value".to_vec().into()).await.unwrap();
        }
    });

    let mut group = c.benchmark_group("get");
    group.throughput(Throughput::Elements(1));

    group.bench_function("single_get", |b| {
        b.iter(|| {
            rt.block_on(async {
                black_box(client.get(b"key5000").await.unwrap())
            })
        })
    });

    group.finish();
}

criterion_group!(benches, bench_get);
criterion_main!(benches);
```

**Reading:**
- Prometheus Rust client docs
- Tracing crate documentation
- Tokio graceful shutdown patterns

---

## Project Progression

Projects are ordered by complexity. Each builds on concepts from the previous.

### Level 1: CLI Foundations

#### Project 1.1: `minigrep`
**File search tool (from The Book, then extend)**

Features:
- Search for patterns in files
- Case-insensitive option
- Regex support
- Colored output
- Recursive directory search

**Concepts learned:**
- Basic Rust syntax
- File I/O
- Error handling
- Command-line arguments
- Iterators

---

#### Project 1.2: `minifind`
**File finder (like fd)**

Features:
- Find files by name pattern
- Filter by type (file, directory, symlink)
- Ignore patterns (.gitignore)
- Parallel search

**Concepts learned:**
- Filesystem operations
- Glob patterns
- Parallel iteration (rayon)
- Builder pattern

---

#### Project 1.3: `minicat`
**File concatenation with extras**

Features:
- Syntax highlighting
- Line numbers
- Git diff integration
- Paging

**Concepts learned:**
- Terminal handling
- ANSI colors
- Trait implementations

---

### Level 2: Data Structures

#### Project 2.1: `lru_cache`
**LRU cache with O(1) operations**

Features:
- Get and put operations
- Configurable capacity
- TTL support
- Thread-safe version

**Concepts learned:**
- Ownership in data structures
- Interior mutability
- Generic programming
- Custom iterators

---

#### Project 2.2: `arena`
**Arena allocator**

Features:
- Allocate objects with arena lifetime
- No individual deallocation
- Drop all at once

**Concepts learned:**
- Lifetimes
- Unsafe Rust basics
- Memory allocation

---

#### Project 2.3: `concurrent_hashmap`
**Lock-free concurrent hashmap**

Features:
- Concurrent reads and writes
- Lock-free or fine-grained locking
- Resize handling

**Concepts learned:**
- Concurrent data structures
- Atomics
- Memory ordering

---

### Level 3: Networking

#### Project 3.1: `mini_redis`
**Redis clone (Tokio mini-redis extended)**

Features:
- TCP server with RESP protocol
- GET, SET, DEL, EXPIRE commands
- Pub/Sub
- Persistence

**Concepts learned:**
- Async programming (Tokio)
- Protocol parsing
- Connection handling
- Graceful shutdown

---

#### Project 3.2: `http_server`
**HTTP/1.1 server from scratch**

Features:
- Request parsing
- Routing
- Static file serving
- Middleware pattern
- Keep-alive

**Concepts learned:**
- HTTP protocol
- State machine parsing
- Async I/O
- Tower-like middleware

---

#### Project 3.3: `reverse_proxy`
**Load-balancing reverse proxy**

Features:
- Multiple backends
- Health checks
- Load balancing strategies
- Request/response modification

**Concepts learned:**
- Proxy patterns
- Connection pooling
- Resilience patterns

---

### Level 4: Systems Programming

#### Project 4.1: `mini_container`
**Container runtime**

Features:
- Linux namespaces
- Cgroups
- Chroot/pivot_root
- Network setup

**Concepts learned:**
- Linux syscalls
- FFI with libc
- Process isolation
- Capability handling

---

#### Project 4.2: `shell`
**Unix shell**

Features:
- Command parsing
- Pipes and redirections
- Job control
- Built-in commands

**Concepts learned:**
- Process management
- Signal handling
- TTY handling
- Parser design

---

#### Project 4.3: `debugger`
**Simple debugger**

Features:
- Breakpoints
- Single stepping
- Register inspection
- Memory reading

**Concepts learned:**
- ptrace
- DWARF debugging info
- ELF format
- Low-level systems

---

### Level 5: Databases & Distributed Systems

#### Project 5.1: `bitcask`
**Log-structured storage engine**

Features:
- Append-only log
- In-memory index
- Compaction
- Crash recovery

**Concepts learned:**
- Storage engine design
- Write-ahead logging
- Compaction strategies

---

#### Project 5.2: `raft`
**Raft consensus implementation**

Features:
- Leader election
- Log replication
- Membership changes
- Snapshotting

**Concepts learned:**
- Distributed consensus
- State machines
- Network simulation for testing

---

#### Project 5.3: `distributed_kv`
**Complete distributed KV store**

The capstone project described above.

---

## Open Source Study

### Projects to Read (In Order of Complexity)

#### Beginner
| Project | Why Study It |
|---------|--------------|
| **ripgrep** | Excellent CLI, regex, parallelism |
| **bat** | CLI tool, syntax highlighting |
| **fd** | File finding, parallel |
| **exa/eza** | Modern ls replacement |

#### Intermediate
| Project | Why Study It |
|---------|--------------|
| **tokio** | Async runtime internals |
| **hyper** | HTTP implementation |
| **serde** | Serialization framework |
| **clap** | CLI argument parsing |
| **axum** | Web framework design |

#### Advanced
| Project | Why Study It |
|---------|--------------|
| **TiKV** | Distributed KV store |
| **nushell** | Shell implementation |
| **RustPython** | Language implementation |
| **wasmtime** | WASM runtime |
| **rustc** | The Rust compiler itself |

#### Expert
| Project | Why Study It |
|---------|--------------|
| **servo** | Browser engine |
| **Firecracker** | MicroVM |
| **Vector** | Observability pipeline |
| **Meilisearch** | Search engine |

### How to Study Open Source

1. **Start with `main.rs`** - Trace the entry point
2. **Read Cargo.toml** - Understand dependencies
3. **Study `lib.rs`** - Find the public API
4. **Run with `RUST_LOG=debug`** - See execution flow
5. **Use rust-analyzer** - Go to definition liberally
6. **Read tests** - They show intended usage
7. **Make a small change** - Best way to learn

---

## Common Pitfalls

### Ownership & Borrowing

**1. Moved value**
```rust
// Error: use of moved value
let s = String::from("hello");
let t = s;
println!("{}", s);  // Error!

// Fix: clone or use reference
let s = String::from("hello");
let t = s.clone();
println!("{}", s);  // OK
```

**2. Cannot borrow as mutable**
```rust
// Error: cannot borrow as mutable
let v = vec![1, 2, 3];
v.push(4);  // Error! v is not mut

// Fix: declare as mutable
let mut v = vec![1, 2, 3];
v.push(4);  // OK
```

**3. Borrowed value does not live long enough**
```rust
// Error
fn bad() -> &str {
    let s = String::from("hello");
    &s  // Error! s dropped
}

// Fix: return owned value
fn good() -> String {
    String::from("hello")
}
```

### Async

**1. Future not Send**
```rust
// Error: future is not Send
async fn bad() {
    let rc = Rc::new(5);
    some_async_fn().await;  // Error if spawned
    println!("{}", rc);
}

// Fix: use Arc instead
async fn good() {
    let arc = Arc::new(5);
    some_async_fn().await;
    println!("{}", arc);
}
```

**2. Holding lock across await**
```rust
// Error/Deadlock: MutexGuard held across await
async fn bad(mutex: &Mutex<i32>) {
    let guard = mutex.lock().unwrap();
    some_async_fn().await;  // Bad!
    *guard += 1;
}

// Fix: drop before await
async fn good(mutex: &Mutex<i32>) {
    {
        let mut guard = mutex.lock().unwrap();
        *guard += 1;
    }  // guard dropped
    some_async_fn().await;
}

// Or use tokio::sync::Mutex
async fn also_good(mutex: &tokio::sync::Mutex<i32>) {
    let mut guard = mutex.lock().await;
    some_async_fn().await;  // OK with async mutex
    *guard += 1;
}
```

**3. Blocking in async**
```rust
// Bad: blocking in async context
async fn bad() {
    std::thread::sleep(Duration::from_secs(1));  // Blocks runtime!
}

// Good: use async sleep
async fn good() {
    tokio::time::sleep(Duration::from_secs(1)).await;
}

// For blocking operations, use spawn_blocking
async fn with_blocking() {
    tokio::task::spawn_blocking(|| {
        std::fs::read_to_string("large_file.txt")
    }).await.unwrap();
}
```

### Lifetimes

**1. Missing lifetime specifier**
```rust
// Error
fn longest(x: &str, y: &str) -> &str {  // Error!
    if x.len() > y.len() { x } else { y }
}

// Fix: add lifetime
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

**2. Lifetime bounds in structs**
```rust
// Error: missing lifetime
struct Bad {
    data: &str,  // Error!
}

// Fix: add lifetime parameter
struct Good<'a> {
    data: &'a str,
}
```

### Performance

**1. Unnecessary allocations**
```rust
// Bad: creates intermediate Vec
let sum: i32 = data.iter()
    .filter(|x| **x > 0)
    .collect::<Vec<_>>()  // Unnecessary!
    .iter()
    .sum();

// Good: chain iterators
let sum: i32 = data.iter()
    .filter(|x| **x > 0)
    .sum();
```

**2. Clone when borrow would work**
```rust
// Bad: unnecessary clone
fn process(data: &str) {
    let owned = data.to_string();  // Unnecessary if we just read
    println!("{}", owned);
}

// Good: just use the reference
fn process(data: &str) {
    println!("{}", data);
}
```

---

## Daily Habits

### The 2-Hour Daily Practice

| Time | Activity |
|------|----------|
| 30 min | Read Rust code (stdlib or crates) |
| 60 min | Write code (project or exercises) |
| 15 min | Watch Rust talks or read blog posts |
| 15 min | Review PRs or participate in community |

### Weekly Goals

- **Monday-Friday:** Work on current project
- **Saturday:** Study open source code
- **Sunday:** Plan next week, write about learnings

### Reading Code Practice

Each week, study one crate:

**Week 1-4:** Standard library
- `std::collections` (Vec, HashMap)
- `std::sync` (Mutex, Arc)
- `std::io` (Read, Write)
- `std::iter` (Iterator trait)

**Week 5-8:** Popular crates
- `serde` (serialization)
- `tokio` (selected modules)
- `clap` (CLI)
- `tracing` (logging)

**Week 9+:** Systems crates
- `hyper` (HTTP)
- `mio` (async I/O)
- `crossbeam` (concurrency)

---

## 12-Month Schedule

### Core Path (Months 1-6) - Foundations

| Month | Focus | Books | Projects |
|-------|-------|-------|----------|
| 1 | Ownership, basics | The Book Ch 1-8 | minigrep |
| 2 | Traits, generics, errors | The Book Ch 9-11, 17 | minifind, minicat |
| 3 | Lifetimes, smart pointers | The Book Ch 15, 19 | lru_cache |
| 4 | Concurrency | The Book Ch 16, Rust Atomics | concurrent data structures |
| 5 | Async basics | Async book, Tokio tutorial | mini_redis |
| 6 | Advanced patterns | Rust for Rustaceans Ch 1-6 | http_server |

### Distributed KV Store Project (Months 7-12)

| Month | Focus | Books | TinyKV Phase |
|-------|-------|-------|--------------|
| 7 | Storage | DDIA Ch 3, LSM papers | **Phase 1:** Storage Engine |
| 8 | Networking | Tokio in depth | **Phase 2:** Network Layer |
| 9 | Consensus | Raft paper | **Phase 3:** Raft Consensus |
| 10 | Transactions | DDIA Ch 7, Percolator | **Phase 4:** Distributed Transactions |
| 11 | API design | API guidelines | **Phase 5:** Client Library & CLI |
| 12 | Production | Zero to Production | **Phase 6:** Production Hardening |

### Skills Progression

| Month | Core Skills | Systems Skills |
|-------|-------------|----------------|
| 1-2 | Ownership, borrowing, traits | - |
| 3-4 | Lifetimes, concurrency | - |
| 5-6 | Async, advanced patterns | - |
| 7 | - | File I/O, serialization, B-trees |
| 8 | - | TCP networking, protocol design |
| 9 | - | Consensus, state machines |
| 10 | - | MVCC, distributed transactions |
| 11 | - | API design, CLI |
| 12 | - | Observability, production ops |

---

## The Path to Cracked

### Beginner (Months 1-3)
You can:
- Write code that compiles
- Understand ownership at a basic level
- Use Result and Option
- Write structs with traits
- Handle basic errors

### Intermediate (Months 4-6)
You can:
- Understand lifetimes
- Write async code
- Use interior mutability correctly
- Design clean APIs
- Write concurrent programs

### Advanced (Months 7-9)
After TinyKV Phases 1-3, you can:
- Build storage engines
- Implement network protocols
- Write consensus algorithms
- Test distributed systems
- Debug complex ownership issues

### Cracked (Months 10-12+)
After completing TinyKV, you can:
- Build distributed systems
- Implement transactions
- Design production-ready software
- Contribute to Rust infrastructure projects
- Understand Rust's guarantees deeply

---

## Resources Quick Reference

### Bookmarks

```
# Official
rust-lang.org                 # Official site
doc.rust-lang.org/book        # The Book
doc.rust-lang.org/std         # Standard library docs
crates.io                     # Package registry
lib.rs                        # Better crate search

# Learning
rustlings                     # Exercises
exercism.org/tracks/rust      # Mentored exercises
rust-by-example               # Examples
tour.rust-lang.org            # Interactive tour

# Advanced
doc.rust-lang.org/nomicon     # Unsafe Rust
rust-lang.github.io/api-guidelines  # API design
github.com/rust-unofficial/patterns  # Patterns

# Community
reddit.com/r/rust             # Reddit
users.rust-lang.org           # Forums
rust-lang.zulipchat.com       # Zulip chat
```

### Key People to Follow

**Core Team:**
- **Steve Klabnik** - Docs, advocacy
- **Mara Bos** - Atomics, library team
- **Niko Matsakis** - Language design

**Community:**
- **Jon Gjengset** - YouTube, systems
- **Amos (fasterthanlime)** - Deep dives
- **Luca Palmieri** - Zero to Production
- **Alice Ryhl** - Tokio maintainer

### Podcasts

- **New Rustacean** - Learning Rust (completed)
- **Rustacean Station** - Interviews
- **Are We Podcast Yet** - General Rust

---

## Final Words

Rust is demanding. The compiler will reject code that would compile in other languages. This is the point.

What sets Rust apart:
1. **Fearless concurrency** - Data races are compile errors
2. **Memory safety** - No null pointers, no dangling references
3. **Zero-cost abstractions** - High-level code, low-level performance
4. **Expressive type system** - Encode invariants in types

### The TinyKV Advantage

Building a distributed KV store is the ultimate Rust project because:
- **It uses everything** - Ownership, lifetimes, async, unsafe
- **It's distributed** - Network protocols, consensus, transactions
- **It must be correct** - Raft requires precision
- **It must be fast** - Storage engines are performance-critical
- **It's real** - etcd, Consul, TiKV use these same patterns

Most tutorials teach syntax. Building TinyKV teaches you to think in Rust.

### What Comes After

Once you've completed TinyKV, you can:
- **Extend it** - Add more features (watches, leases, auth)
- **Contribute** - TiKV, Materialize, and others welcome contributors
- **Build more systems** - The patterns transfer
- **Go deeper** - Async runtimes, compilers, operating systems

The infrastructure of the future is being written in Rust. AWS, Microsoft, Google, Cloudflare, Discord - all betting on Rust for systems work. By mastering Rust through building distributed systems, you join those building the foundations.

Fight the borrow checker. Win. Build something real.

---

*Generated: January 2026*
