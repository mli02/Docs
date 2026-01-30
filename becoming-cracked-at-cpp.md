# Becoming Cracked at C++

A comprehensive guide to mastering C++ for systems programming, high-performance computing, and infrastructure.

---

## Table of Contents

1. [Why C++](#why-c)
2. [Core Mental Models](#core-mental-models)
3. [Books: The Foundation](#books-the-foundation)
4. [Structured Reading Path](#structured-reading-path)
5. [Video Resources](#video-resources)
6. [Tools: Your Arsenal](#tools-your-arsenal)
7. [Development Setup](#development-setup)
8. [Modern C++ Features](#modern-c-features)
9. [The Database Engine Project](#the-database-engine-project)
   - [Phase 1: Storage Engine](#phase-1-storage-engine-month-7)
   - [Phase 2: Buffer Pool Manager](#phase-2-buffer-pool-manager-month-8)
   - [Phase 3: Index Structures](#phase-3-index-structures-month-9)
   - [Phase 4: Query Execution](#phase-4-query-execution-month-10)
   - [Phase 5: Concurrency Control](#phase-5-concurrency-control-month-11)
   - [Phase 6: Recovery and Production](#phase-6-recovery-and-production-month-12)
10. [Project Progression](#project-progression)
11. [Open Source Study](#open-source-study)
12. [Common Pitfalls](#common-pitfalls)
13. [Daily Habits](#daily-habits)
14. [12-Month Schedule](#12-month-schedule)
15. [The Path to Cracked](#the-path-to-cracked)

---

## Why C++

C++ is the language of high-performance systems. When you need:

- **Zero-overhead abstractions** - Pay only for what you use
- **Direct hardware access** - Memory, caches, SIMD, GPU
- **Maximum performance** - Games, trading systems, databases, compilers
- **Long-lived systems** - Codebases that last decades
- **Interoperability** - Every language can call C++

C++ powers: Game engines (Unreal, Unity's core), databases (MySQL, PostgreSQL, MongoDB), browsers (Chrome, Firefox), operating systems (Windows, parts of macOS/Linux), trading systems, embedded systems, and more.

**The honest truth:** C++ is the most complex mainstream language. It has 40+ years of evolution, multiple paradigms, and sharp edges everywhere. Mastery takes years. But no other language offers the same combination of performance, abstraction, and control.

---

## Core Mental Models

### 1. RAII - Resource Acquisition Is Initialization

The most important concept in C++. Resources (memory, files, locks, sockets) are tied to object lifetime.

```cpp
// Bad: Manual resource management
void process_file() {
    FILE* f = fopen("data.txt", "r");
    if (!f) return;

    // If any exception or early return happens, we leak the file
    do_something();  // What if this throws?

    fclose(f);  // Easy to forget
}

// Good: RAII
void process_file() {
    std::ifstream file("data.txt");
    if (!file) return;

    do_something();  // If this throws, file still closes

    // file automatically closed when scope exits
}

// RAII for custom resources
class DatabaseConnection {
    Connection* conn_;
public:
    DatabaseConnection(const std::string& url) : conn_(connect(url)) {}
    ~DatabaseConnection() { if (conn_) disconnect(conn_); }

    // Delete copy (prevent double-free)
    DatabaseConnection(const DatabaseConnection&) = delete;
    DatabaseConnection& operator=(const DatabaseConnection&) = delete;

    // Allow move
    DatabaseConnection(DatabaseConnection&& other) noexcept
        : conn_(other.conn_) { other.conn_ = nullptr; }
};
```

**The rule:** If you write `new`, `malloc`, `fopen`, or acquire any resource directly, wrap it in a class immediately.

### 2. Value Semantics and Move Semantics

C++ defaults to copying. Modern C++ adds moving for efficiency.

```cpp
// Value semantics - each variable owns its data
std::vector<int> a = {1, 2, 3};
std::vector<int> b = a;  // Copy - b has its own memory
a[0] = 100;              // Doesn't affect b

// Move semantics - transfer ownership
std::vector<int> create_data() {
    std::vector<int> result(1000000);
    // Fill result...
    return result;  // Move, not copy (RVO or move constructor)
}

std::vector<int> data = create_data();  // Efficient

// Explicit move when needed
std::vector<int> x = {1, 2, 3};
std::vector<int> y = std::move(x);  // x is now empty, y owns the data
```

**Understand:**
- Lvalues (have identity, can be addressed)
- Rvalues (temporaries, about to be destroyed)
- Move constructors and move assignment

### 3. The Rule of Zero/Three/Five

```cpp
// Rule of Zero: If you don't manage resources, don't write special members
struct Point {
    double x, y;
    // Compiler-generated copy/move/destructor are correct
};

// Rule of Five: If you manage resources, define all five
class Buffer {
    char* data_;
    size_t size_;
public:
    // Constructor
    Buffer(size_t size) : data_(new char[size]), size_(size) {}

    // Destructor
    ~Buffer() { delete[] data_; }

    // Copy constructor
    Buffer(const Buffer& other)
        : data_(new char[other.size_]), size_(other.size_) {
        std::copy(other.data_, other.data_ + size_, data_);
    }

    // Copy assignment
    Buffer& operator=(const Buffer& other) {
        if (this != &other) {
            delete[] data_;
            size_ = other.size_;
            data_ = new char[size_];
            std::copy(other.data_, other.data_ + size_, data_);
        }
        return *this;
    }

    // Move constructor
    Buffer(Buffer&& other) noexcept
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    // Move assignment
    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            delete[] data_;
            data_ = other.data_;
            size_ = other.size_;
            other.data_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }
};

// Better: Use smart pointers (back to Rule of Zero)
class BetterBuffer {
    std::unique_ptr<char[]> data_;
    size_t size_;
public:
    BetterBuffer(size_t size)
        : data_(std::make_unique<char[]>(size)), size_(size) {}
    // Compiler generates correct move operations
    // Copy is deleted (unique_ptr not copyable) - which is probably what you want
};
```

### 4. Templates Are Compile-Time Code Generation

Templates aren't generics - they're a Turing-complete compile-time programming language.

```cpp
// Basic template - code is generated for each type used
template<typename T>
T max(T a, T b) {
    return (a > b) ? a : b;
}

int main() {
    max(1, 2);      // Generates max<int>
    max(1.0, 2.0);  // Generates max<double>
}

// SFINAE - Substitution Failure Is Not An Error
template<typename T>
auto size(const T& container) -> decltype(container.size()) {
    return container.size();
}

// Concepts (C++20) - constrained templates
template<typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template<Numeric T>
T square(T x) {
    return x * x;
}
```

### 5. Undefined Behavior Is Real

C++ trusts you completely. Violate the rules and anything can happen.

```cpp
// Undefined behavior examples - all of these can cause weird bugs
int arr[10];
arr[10] = 0;              // Buffer overflow

int* p = nullptr;
*p = 42;                  // Null dereference

int x;
int y = x + 1;            // Using uninitialized variable

int i = INT_MAX;
i = i + 1;                // Signed integer overflow

std::vector<int> v = {1, 2, 3};
int& ref = v[0];
v.push_back(4);           // ref may now be dangling
int x = ref;              // Undefined behavior
```

**Defense:**
- Use sanitizers (ASan, UBSan, TSan) in development
- Use smart pointers
- Prefer `at()` over `[]` when bounds checking is acceptable
- Enable compiler warnings (`-Wall -Wextra -Wpedantic`)

### 6. Memory Layout Matters

Understanding memory is what separates C++ programmers from others.

```cpp
// Stack vs Heap
void function() {
    int x = 42;                          // Stack - fast, automatic lifetime
    std::array<int, 1000> arr;           // Stack - fixed size at compile time

    auto* p = new int(42);               // Heap - slower, manual lifetime
    std::vector<int> vec(1000);          // Heap internally

    delete p;
}

// Memory layout of objects
struct Point {
    double x;  // 8 bytes
    double y;  // 8 bytes
};  // Total: 16 bytes, no padding needed

struct Mixed {
    char a;    // 1 byte
    // 7 bytes padding
    double b;  // 8 bytes
    char c;    // 1 byte
    // 7 bytes padding
};  // Total: 24 bytes

struct Packed {
    double b;  // 8 bytes
    char a;    // 1 byte
    char c;    // 1 byte
    // 6 bytes padding
};  // Total: 16 bytes - order matters!

// Cache-friendly data structures
// Bad: Array of Structs with poor cache usage
struct Entity {
    bool active;
    double x, y, z;
    double vx, vy, vz;
    // ... many more fields
};
std::vector<Entity> entities;

// Good: Struct of Arrays for hot data
struct Positions {
    std::vector<double> x, y, z;
};
struct Velocities {
    std::vector<double> vx, vy, vz;
};
```

### 7. The Compilation Model

C++ has a complex build process you must understand.

```
Source files (.cpp) ──┐
                      ├── Preprocessor ─── Translation units ─── Compiler ─── Object files (.o) ─── Linker ─── Executable
Header files (.h) ────┘

Preprocessor: #include, #define, #ifdef
Compiler: Parses C++, generates machine code for each .cpp
Linker: Combines object files, resolves symbols
```

**Key concepts:**
- **ODR (One Definition Rule):** Each entity can only be defined once across all translation units
- **Include guards:** Prevent multiple inclusion of headers
- **Forward declarations:** Reduce compile dependencies
- **Templates:** Defined in headers (must be visible at instantiation)

```cpp
// header.h
#pragma once  // Modern include guard

class Foo;  // Forward declaration - avoids including foo.h

class Bar {
    Foo* foo_;  // Pointer to incomplete type is fine
public:
    void process();  // Declaration only
};

// source.cpp
#include "header.h"
#include "foo.h"  // Now we need the full definition

void Bar::process() {
    foo_->do_something();
}
```

---

## Books: The Foundation

### Essential (Read in Order)

| Order | Book | Focus | Why |
|-------|------|-------|-----|
| 1 | **"C++ Primer" (5th ed)** by Lippman, Lajoie, Moo | Complete language coverage | THE C++ book. Comprehensive, well-written, covers C++11. |
| 2 | **"Effective Modern C++"** by Scott Meyers | C++11/14 best practices | 42 items on how to use modern C++ correctly. Mandatory. |
| 3 | **"C++ Concurrency in Action" (2nd ed)** by Anthony Williams | Multithreading | Deep dive into the C++ memory model and threading. |

### Intermediate

| Book | Focus | When to Read |
|------|-------|--------------|
| **"A Tour of C++" (3rd ed)** by Bjarne Stroustrup | Quick overview of modern C++ | Good refresher or quick intro |
| **"C++ Best Practices"** by Jason Turner | Modern idioms | After basics, before production |
| **"Effective C++"** by Scott Meyers | Classic best practices | If working with pre-C++11 code |
| **"More Effective C++"** by Scott Meyers | Advanced topics | After Effective C++ |

### Advanced

| Book | Focus | When to Read |
|------|-------|--------------|
| **"C++ Templates: The Complete Guide" (2nd ed)** | Template metaprogramming | When you need deep template knowledge |
| **"Modern C++ Design"** by Andrei Alexandrescu | Template techniques | Classic, somewhat dated but influential |
| **"C++17/20/23 - The Complete Guide"** by Nicolai Josuttis | Latest standards | When using newest features |

### Systems Programming

| Book | Focus | When to Read |
|------|-------|--------------|
| **"Computer Systems: A Programmer's Perspective"** | How code runs on hardware | Essential for systems work |
| **"The Linux Programming Interface"** | Linux systems programming | For Linux development |
| **"Operating Systems: Three Easy Pieces"** (free) | OS concepts | Understanding the platform |

### Performance

| Book | Focus | When to Read |
|------|-------|--------------|
| **"Performance Analysis and Tuning on Modern CPUs"** by Denis Bakhvalov | CPU architecture, profiling | When optimizing |
| **"Data-Oriented Design"** by Richard Fabian | Cache-friendly design | For game dev and high-performance |
| **"The Art of Writing Efficient Programs"** by Fedor Pikus | C++ optimization | Modern C++ performance |

---

## Structured Reading Path

### Phase 1: Language Fundamentals (Weeks 1-8)

**Primary: "C++ Primer" (5th ed)**

| Week | Chapters | Focus | Practice |
|------|----------|-------|----------|
| 1 | Ch 1-2 | Basics, types, variables | Simple programs |
| 2 | Ch 3-4 | Strings, vectors, arrays, expressions | Implement exercises |
| 3 | Ch 5-6 | Statements, functions | Build small utilities |
| 4 | Ch 7 | Classes | Design a class hierarchy |
| 5 | Ch 8-9 | IO library, sequential containers | File processing |
| 6 | Ch 10-11 | Algorithms, associative containers | STL practice |
| 7 | Ch 12 | Dynamic memory, smart pointers | Memory exercises |
| 8 | Ch 13 | Copy control | Rule of five implementation |

### Phase 2: Modern C++ (Weeks 9-12)

**Primary: "Effective Modern C++"**

| Week | Items | Focus |
|------|-------|-------|
| 9 | 1-11 | Type deduction, auto, decltype |
| 10 | 12-22 | Smart pointers, move semantics |
| 11 | 23-33 | Rvalue references, forwarding |
| 12 | 34-42 | Lambda expressions, concurrency |

**Supplement with:**
- "C++ Primer" Ch 14-16 (templates, OOP)
- CppReference.com for standard library details

### Phase 3: Advanced Language (Weeks 13-16)

**Primary: "C++ Primer" remaining + C++17/20 features**

| Week | Focus |
|------|-------|
| 13 | Templates deep dive (Ch 16, C++ Templates book excerpts) |
| 14 | OOP and virtual functions (Ch 15), CRTP |
| 15 | C++17 features: structured bindings, if constexpr, fold expressions |
| 16 | C++20 features: concepts, ranges, coroutines (basics) |

### Phase 4: Concurrency (Weeks 17-20)

**Primary: "C++ Concurrency in Action" (2nd ed)**

| Week | Chapters | Focus |
|------|----------|-------|
| 17 | Ch 1-2 | Thread management |
| 18 | Ch 3-4 | Sharing data, synchronization |
| 19 | Ch 5 | The C++ memory model (critical!) |
| 20 | Ch 6-8 | Lock-free programming, concurrent data structures |

### Phase 5: Systems & Performance (Weeks 21-24)

| Week | Focus |
|------|-------|
| 21 | CSAPP selected chapters (memory, caching) |
| 22 | Profiling tools: perf, VTune, Instruments |
| 23 | Memory allocators, custom allocation |
| 24 | SIMD, cache optimization |

---

## Video Resources

### YouTube Channels

| Channel | Content |
|---------|---------|
| **CppCon** | Conference talks, essential viewing |
| **C++ Weekly (Jason Turner)** | Short tips, features |
| **The Cherno** | Game dev focused, good explanations |
| **Cᐩᐩ Now** | More conference talks |

### Must-Watch Talks

**Fundamentals:**
- "Back to Basics" series at CppCon (any year)
- "C++ in 2024" (or latest year) - Bjarne Stroustrup
- "The Design of C++" talks by Bjarne Stroustrup

**Modern C++:**
- "Effective Modern C++" talks by Scott Meyers
- "C++11/14/17/20" talks by Nicolai Josuttis
- "Rule of Zero" - Peter Sommerlad

**Performance:**
- "Performance Matters" - Emery Berger
- "What Do You Mean by Cache Friendly?" - Björn Fahller
- "Data-Oriented Design" - Mike Acton (legendary)
- "SIMD Optimization" talks by Bryce Lelbach

**Concurrency:**
- "The C++ Memory Model" - Herb Sutter
- "std::atomic explained" - Fedor Pikus
- "Lock-Free Programming" talks by Herb Sutter, Fedor Pikus

**Systems:**
- "What Has My Compiler Done for Me Lately?" - Matt Godbolt
- "Undefined Behavior" talks
- "ABI Stability" - Louis Dionne

### Courses

| Course | Platform | Focus |
|--------|----------|-------|
| **Beginning C++ Programming** | Udemy (Frank Mitropoulos) | Beginner-friendly |
| **Mastering C++ STL** | Various | STL deep dive |
| **Parallel Programming** | Various | Concurrency |

---

## Tools: Your Arsenal

### Essential Tools

| Tool | Purpose | Install |
|------|---------|---------|
| **Clang/LLVM** | Compiler (better errors than GCC) | brew install llvm |
| **GCC** | Compiler (sometimes better codegen) | brew install gcc |
| **CMake** | Build system | brew install cmake |
| **Ninja** | Fast build execution | brew install ninja |
| **clangd** | Language server | brew install llvm |
| **clang-format** | Code formatting | Comes with LLVM |
| **clang-tidy** | Static analysis, modernization | Comes with LLVM |

### Debugging & Profiling

| Tool | Purpose |
|------|---------|
| **GDB** | Classic debugger |
| **LLDB** | Modern debugger (better on macOS) |
| **Valgrind** | Memory debugging (Linux) |
| **AddressSanitizer (ASan)** | Memory errors at runtime |
| **ThreadSanitizer (TSan)** | Data races |
| **UndefinedBehaviorSanitizer (UBSan)** | UB detection |
| **perf** | Linux profiling |
| **Instruments** | macOS profiling |
| **VTune** | Intel profiler |
| **Compiler Explorer (godbolt.org)** | See assembly - essential! |

### Testing

| Tool | Purpose |
|------|---------|
| **Google Test** | Unit testing framework |
| **Catch2** | Modern testing (header-only) |
| **Google Benchmark** | Microbenchmarking |
| **Doctest** | Lightweight testing |

### Package Management

| Tool | Purpose |
|------|---------|
| **vcpkg** | Microsoft's package manager |
| **Conan** | Decentralized package manager |
| **CPM.cmake** | CMake-based dependency management |

---

## Development Setup

### Compiler Installation

```bash
# macOS
brew install llvm
brew install cmake ninja

# Add to ~/.zshrc
export PATH="/opt/homebrew/opt/llvm/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/llvm/lib"
export CPPFLAGS="-I/opt/homebrew/opt/llvm/include"

# Linux (Ubuntu/Debian)
sudo apt install clang clang-tools cmake ninja-build
```

### Editor Setup

**VS Code (Recommended for beginners):**
```
1. Install "C/C++" extension (Microsoft)
2. Install "clangd" extension
3. Install "CMake Tools" extension
4. Configure clangd as the IntelliSense provider
```

**Neovim:**
```
Use LazyVim or custom config with:
- nvim-lspconfig with clangd
- nvim-dap for debugging
- cmake-tools.nvim
```

### Project Structure

```
myproject/
├── CMakeLists.txt
├── src/
│   ├── main.cpp
│   └── module/
│       ├── module.cpp
│       └── module.h
├── include/
│   └── myproject/
│       └── public_header.h
├── tests/
│   ├── CMakeLists.txt
│   └── test_module.cpp
├── external/            # Third-party deps
├── cmake/               # CMake modules
├── .clang-format
├── .clang-tidy
└── compile_commands.json  # Generated by CMake
```

### CMakeLists.txt Template

```cmake
cmake_minimum_required(VERSION 3.20)
project(myproject VERSION 1.0 LANGUAGES CXX)

# Require C++20
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Generate compile_commands.json for clangd
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Warnings
add_compile_options(-Wall -Wextra -Wpedantic -Werror)

# Sanitizers in debug mode
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    add_compile_options(-fsanitize=address,undefined)
    add_link_options(-fsanitize=address,undefined)
endif()

# Main library
add_library(mylib
    src/module/module.cpp
)
target_include_directories(mylib PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Executable
add_executable(myapp src/main.cpp)
target_link_libraries(myapp PRIVATE mylib)

# Tests
enable_testing()
add_subdirectory(tests)
```

### .clang-format Template

```yaml
BasedOnStyle: Google
IndentWidth: 4
ColumnLimit: 100
BreakBeforeBraces: Attach
AllowShortFunctionsOnASingleLine: Inline
AllowShortIfStatementsOnASingleLine: Never
PointerAlignment: Left
```

### .clang-tidy Template

```yaml
Checks: >
  -*,
  bugprone-*,
  clang-analyzer-*,
  cppcoreguidelines-*,
  modernize-*,
  performance-*,
  readability-*,
  -modernize-use-trailing-return-type,
  -readability-magic-numbers,
  -cppcoreguidelines-avoid-magic-numbers

WarningsAsErrors: ''
HeaderFilterRegex: '.*'
```

---

## Modern C++ Features

### C++11 (The Renaissance)

| Feature | Example |
|---------|---------|
| `auto` | `auto x = func();` |
| Range-based for | `for (auto& item : container)` |
| Lambda expressions | `[&](int x) { return x * 2; }` |
| Move semantics | `std::move(obj)` |
| Smart pointers | `std::unique_ptr`, `std::shared_ptr` |
| `nullptr` | Instead of `NULL` |
| `constexpr` | Compile-time computation |
| Uniform initialization | `std::vector<int> v{1, 2, 3};` |
| `std::thread` | Standard threading |
| `std::atomic` | Lock-free primitives |

### C++14 (Polish)

| Feature | Example |
|---------|---------|
| Generic lambdas | `[](auto x) { return x * 2; }` |
| `decltype(auto)` | Perfect forwarding of return types |
| Variable templates | `template<class T> constexpr T pi = T(3.14159);` |
| `std::make_unique` | `auto p = std::make_unique<Foo>();` |

### C++17 (Practical Additions)

| Feature | Example |
|---------|---------|
| Structured bindings | `auto [x, y] = point;` |
| `if constexpr` | Compile-time conditionals |
| `std::optional` | Optional values without pointers |
| `std::variant` | Type-safe unions |
| `std::string_view` | Non-owning string reference |
| `std::filesystem` | File system operations |
| Fold expressions | `(args + ...)` |
| Inline variables | `inline` in headers |

### C++20 (Major Update)

| Feature | Example |
|---------|---------|
| Concepts | `template<Numeric T>` |
| Ranges | `std::views::filter`, `std::views::transform` |
| Coroutines | `co_await`, `co_yield`, `co_return` |
| Modules | `import std;` (replacing includes) |
| Three-way comparison | `<=>` (spaceship operator) |
| `std::span` | Non-owning view of contiguous data |
| `std::format` | Python-style formatting |
| `consteval` | Must evaluate at compile time |
| `constinit` | Constant initialization |

### C++23 (Latest)

| Feature | Example |
|---------|---------|
| `std::expected` | Better error handling than optional |
| `std::print` | Easy printing |
| `std::mdspan` | Multidimensional spans |
| Deducing `this` | Explicit object parameter |
| `std::generator` | Coroutine generators |

---

## The Database Engine Project

**What you're building:** A simplified relational database engine from scratch - no libraries for the core functionality.

**Why this project:** Database engines are the ultimate C++ systems project. They require:
- Memory management (buffer pools, custom allocators)
- Data structures (B+ trees, hash tables)
- Concurrency (transactions, MVCC)
- Disk I/O (storage engine, WAL)
- Query processing (parsing, planning, execution)

**Architecture Overview:**
```
┌─────────────────────────────────────────────────────────────────┐
│                        MiniDB                                    │
├─────────────────────────────────────────────────────────────────┤
│  SQL Parser         │  Query Planner      │  Query Executor      │
├─────────────────────────────────────────────────────────────────┤
│                     Execution Engine                             │
│  Sequential Scan    │  Index Scan         │  Nested Loop Join    │
├─────────────────────────────────────────────────────────────────┤
│                     Access Methods                               │
│  Heap File          │  B+ Tree Index      │  Hash Index          │
├─────────────────────────────────────────────────────────────────┤
│                     Buffer Pool Manager                          │
│  LRU Replacement    │  Page Pinning       │  Dirty Page Tracking │
├─────────────────────────────────────────────────────────────────┤
│                     Disk Manager                                 │
│  Page Read/Write    │  File Management    │  WAL                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### Phase 1: Storage Engine (Month 7)

**Build:** Disk manager and page abstraction

**Features:**
- Fixed-size pages (4KB or 8KB)
- Read/write pages to/from disk
- Page ID allocation
- Basic file management
- Tuple storage within pages (slotted page format)

**Skills Learned:**
- File I/O in C++
- Memory-mapped files vs explicit I/O
- Page layout design
- Binary serialization

**Core Classes:**

```cpp
// Page abstraction
class Page {
public:
    static constexpr size_t PAGE_SIZE = 4096;

    Page() = default;

    char* GetData() { return data_; }
    PageId GetPageId() const { return page_id_; }

    bool IsDirty() const { return is_dirty_; }
    void SetDirty(bool dirty) { is_dirty_ = dirty; }

    int GetPinCount() const { return pin_count_; }
    void IncrementPinCount() { ++pin_count_; }
    void DecrementPinCount() { --pin_count_; }

private:
    char data_[PAGE_SIZE]{};
    PageId page_id_{INVALID_PAGE_ID};
    bool is_dirty_{false};
    int pin_count_{0};
};

// Disk manager
class DiskManager {
public:
    explicit DiskManager(const std::string& db_file);
    ~DiskManager();

    void ReadPage(PageId page_id, char* page_data);
    void WritePage(PageId page_id, const char* page_data);

    PageId AllocatePage();
    void DeallocatePage(PageId page_id);

private:
    std::fstream db_io_;
    std::string file_name_;
    std::atomic<PageId> next_page_id_{0};
};

// Slotted page for tuple storage
class TablePage {
public:
    void Init(PageId page_id);

    bool InsertTuple(const Tuple& tuple, RID* rid);
    bool DeleteTuple(const RID& rid);
    bool UpdateTuple(const Tuple& tuple, const RID& rid);

    Tuple GetTuple(const RID& rid);

private:
    // Page header
    PageId page_id_;
    uint16_t num_tuples_;
    uint16_t free_space_pointer_;

    // Slot array grows from front, data grows from back
    // [header][slot0][slot1]...[free space]...[tuple1][tuple0]
};
```

**Reading:**
- "Database Internals" by Alex Petrov (storage engines)
- SQLite file format documentation

---

### Phase 2: Buffer Pool Manager (Month 8)

**Build:** In-memory cache for disk pages

**Features:**
- Fixed-size buffer pool (configurable page count)
- LRU replacement policy
- Page pinning (prevent eviction while in use)
- Dirty page tracking
- Concurrent access (reader-writer locks per page)

**Skills Learned:**
- Cache design and replacement policies
- Reference counting
- Concurrent data structures
- Memory management

**Core Classes:**

```cpp
class BufferPoolManager {
public:
    BufferPoolManager(size_t pool_size, DiskManager* disk_manager);
    ~BufferPoolManager();

    // Fetch a page, reading from disk if necessary
    Page* FetchPage(PageId page_id);

    // Create a new page in the buffer pool
    Page* NewPage(PageId* page_id);

    // Unpin a page, allowing it to be evicted
    bool UnpinPage(PageId page_id, bool is_dirty);

    // Flush a page to disk
    bool FlushPage(PageId page_id);

    // Delete a page from buffer pool and disk
    bool DeletePage(PageId page_id);

private:
    Page* FindFreePage();
    void EvictPage();

    size_t pool_size_;
    std::vector<Page> pages_;
    std::unordered_map<PageId, size_t> page_table_;  // page_id -> frame_id
    std::list<size_t> free_list_;                     // Free frame IDs

    // LRU tracking
    std::list<size_t> lru_list_;
    std::unordered_map<size_t, std::list<size_t>::iterator> lru_map_;

    DiskManager* disk_manager_;
    std::mutex latch_;
};

// LRU Replacer (can be extracted)
class LRUReplacer {
public:
    explicit LRUReplacer(size_t num_pages);

    // Remove the least recently used page
    bool Evict(size_t* frame_id);

    // Mark a page as recently used (remove from eviction candidates)
    void Pin(size_t frame_id);

    // Mark a page as evictable
    void Unpin(size_t frame_id);

    size_t Size();

private:
    std::list<size_t> lru_list_;
    std::unordered_map<size_t, std::list<size_t>::iterator> lru_map_;
    size_t capacity_;
    std::mutex latch_;
};
```

**Alternative Replacement Policies to Implement:**
- Clock (approximates LRU, more efficient)
- LRU-K (tracks K most recent accesses)
- 2Q (hot and cold queues)

**Reading:**
- CMU 15-445 lectures on buffer pools
- PostgreSQL buffer manager source

---

### Phase 3: Index Structures (Month 9)

**Build:** B+ tree index for fast lookups

**Features:**
- B+ tree with configurable fan-out
- Insert, delete, search operations
- Range scans via leaf node links
- Concurrent access (latch crabbing)
- Support for variable-length keys

**Skills Learned:**
- Tree data structures
- Complex algorithms (split, merge, redistribute)
- Iterator patterns
- Concurrent tree access

**Core Classes:**

```cpp
// B+ tree
template<typename KeyType, typename ValueType, typename KeyComparator>
class BPlusTree {
public:
    BPlusTree(const std::string& name,
              BufferPoolManager* buffer_pool_manager,
              const KeyComparator& comparator,
              int leaf_max_size,
              int internal_max_size);

    // Insert a key-value pair
    bool Insert(const KeyType& key, const ValueType& value);

    // Delete a key
    bool Delete(const KeyType& key);

    // Point lookup
    bool GetValue(const KeyType& key, std::vector<ValueType>* result);

    // Range scan
    class Iterator;
    Iterator Begin();
    Iterator Begin(const KeyType& key);
    Iterator End();

private:
    Page* FindLeafPage(const KeyType& key, bool leftMost = false);

    void StartNewTree(const KeyType& key, const ValueType& value);
    bool InsertIntoLeaf(const KeyType& key, const ValueType& value);
    void InsertIntoParent(Page* old_node, const KeyType& key, Page* new_node);

    template<typename N>
    N* Split(N* node);

    void Coalesce(Page* neighbor_node, Page* node, Page* parent, int index);
    void Redistribute(Page* neighbor_node, Page* node, int index);

    std::string index_name_;
    PageId root_page_id_{INVALID_PAGE_ID};
    BufferPoolManager* buffer_pool_manager_;
    KeyComparator comparator_;
    int leaf_max_size_;
    int internal_max_size_;
    std::mutex root_latch_;
};

// B+ tree leaf node
class BPlusTreeLeafPage : public BPlusTreePage {
public:
    void Init(PageId page_id, PageId parent_id, int max_size);

    PageId GetNextPageId() const { return next_page_id_; }
    void SetNextPageId(PageId next_page_id) { next_page_id_ = next_page_id; }

    KeyType KeyAt(int index) const;
    ValueType ValueAt(int index) const;

    int KeyIndex(const KeyType& key, const KeyComparator& comparator) const;

    int Insert(const KeyType& key, const ValueType& value, const KeyComparator& comparator);
    bool Delete(const KeyType& key, const KeyComparator& comparator);

    void MoveHalfTo(BPlusTreeLeafPage* recipient);
    void MoveAllTo(BPlusTreeLeafPage* recipient);

private:
    PageId next_page_id_{INVALID_PAGE_ID};
    std::pair<KeyType, ValueType> array_[0];  // Flexible array member
};
```

**Extensions:**
- Hash index for equality lookups
- Extendible hashing (dynamic hash tables)
- Concurrent B+ tree (optimistic locking, Blink tree)

**Reading:**
- "Database Internals" chapters on B-trees
- "The Ubiquitous B-Tree" paper
- CMU 15-445 lectures on indexing

---

### Phase 4: Query Execution (Month 10)

**Build:** SQL parser and query executor

**Features:**
- Simple SQL parser (SELECT, INSERT, UPDATE, DELETE)
- Table creation (CREATE TABLE)
- Volcano-style iterator model
- Sequential scan operator
- Index scan operator
- Projection and filter operators
- Nested loop join

**Skills Learned:**
- Parsing (recursive descent or parser generator)
- Iterator/visitor patterns
- Query plan representation
- Operator pipelining

**Core Classes:**

```cpp
// Abstract executor
class AbstractExecutor {
public:
    explicit AbstractExecutor(ExecutorContext* exec_ctx) : exec_ctx_(exec_ctx) {}
    virtual ~AbstractExecutor() = default;

    virtual void Init() = 0;
    virtual bool Next(Tuple* tuple, RID* rid) = 0;
    virtual const Schema& GetOutputSchema() const = 0;

protected:
    ExecutorContext* exec_ctx_;
};

// Sequential scan
class SeqScanExecutor : public AbstractExecutor {
public:
    SeqScanExecutor(ExecutorContext* exec_ctx, const SeqScanPlanNode* plan);

    void Init() override;
    bool Next(Tuple* tuple, RID* rid) override;
    const Schema& GetOutputSchema() const override { return plan_->OutputSchema(); }

private:
    const SeqScanPlanNode* plan_;
    TableHeap* table_heap_;
    TableIterator iter_;
    TableIterator end_;
};

// Filter
class FilterExecutor : public AbstractExecutor {
public:
    FilterExecutor(ExecutorContext* exec_ctx,
                   const FilterPlanNode* plan,
                   std::unique_ptr<AbstractExecutor>&& child);

    void Init() override;
    bool Next(Tuple* tuple, RID* rid) override;

private:
    const FilterPlanNode* plan_;
    std::unique_ptr<AbstractExecutor> child_;
};

// Nested loop join
class NestedLoopJoinExecutor : public AbstractExecutor {
public:
    NestedLoopJoinExecutor(ExecutorContext* exec_ctx,
                           const NestedLoopJoinPlanNode* plan,
                           std::unique_ptr<AbstractExecutor>&& left,
                           std::unique_ptr<AbstractExecutor>&& right);

    void Init() override;
    bool Next(Tuple* tuple, RID* rid) override;

private:
    const NestedLoopJoinPlanNode* plan_;
    std::unique_ptr<AbstractExecutor> left_;
    std::unique_ptr<AbstractExecutor> right_;
    Tuple left_tuple_;
    RID left_rid_;
    bool left_exhausted_{false};
};

// Simple SQL parser
class Parser {
public:
    std::unique_ptr<Statement> Parse(const std::string& sql);

private:
    std::unique_ptr<SelectStatement> ParseSelect();
    std::unique_ptr<InsertStatement> ParseInsert();
    std::unique_ptr<Expression> ParseExpression();
    // ...

    Lexer lexer_;
    Token current_token_;
};
```

**Extensions:**
- Hash join
- Sort-merge join
- Aggregation operators
- Query optimizer (cost-based)

**Reading:**
- "Architecture of a Database System" paper
- CMU 15-445 lectures on query execution
- Volcano paper

---

### Phase 5: Concurrency Control (Month 11)

**Build:** Transaction support with isolation

**Features:**
- Transaction begin/commit/abort
- Two-phase locking (2PL)
- Lock manager
- Deadlock detection
- MVCC (multi-version concurrency control)
- Isolation levels (read committed, repeatable read, serializable)

**Skills Learned:**
- Transaction theory
- Lock management
- Deadlock handling
- Timestamp ordering
- Concurrent programming patterns

**Core Classes:**

```cpp
// Transaction
class Transaction {
public:
    explicit Transaction(txn_id_t txn_id);

    txn_id_t GetTransactionId() const { return txn_id_; }
    TransactionState GetState() const { return state_; }
    IsolationLevel GetIsolationLevel() const { return isolation_level_; }

    // Write set for undo on abort
    void AddWriteRecord(const RID& rid, const Tuple& old_tuple);
    const std::vector<WriteRecord>& GetWriteSet() const { return write_set_; }

    // Locks held
    std::shared_ptr<std::unordered_set<RID>> GetSharedLockSet() { return s_lock_set_; }
    std::shared_ptr<std::unordered_set<RID>> GetExclusiveLockSet() { return x_lock_set_; }

private:
    txn_id_t txn_id_;
    TransactionState state_{TransactionState::GROWING};
    IsolationLevel isolation_level_{IsolationLevel::REPEATABLE_READ};
    std::vector<WriteRecord> write_set_;
    std::shared_ptr<std::unordered_set<RID>> s_lock_set_;
    std::shared_ptr<std::unordered_set<RID>> x_lock_set_;
};

// Lock manager
class LockManager {
public:
    bool LockShared(Transaction* txn, const RID& rid);
    bool LockExclusive(Transaction* txn, const RID& rid);
    bool LockUpgrade(Transaction* txn, const RID& rid);
    bool Unlock(Transaction* txn, const RID& rid);

private:
    struct LockRequest {
        txn_id_t txn_id_;
        LockMode lock_mode_;
        bool granted_;
    };

    struct LockRequestQueue {
        std::list<LockRequest> request_queue_;
        std::condition_variable cv_;
        bool upgrading_{false};
    };

    bool DetectDeadlock(txn_id_t txn_id);
    void RunDeadlockDetection();

    std::mutex latch_;
    std::unordered_map<RID, LockRequestQueue> lock_table_;
    std::atomic<bool> enable_deadlock_detection_{true};
};

// Transaction manager
class TransactionManager {
public:
    Transaction* Begin(IsolationLevel isolation_level = IsolationLevel::REPEATABLE_READ);
    void Commit(Transaction* txn);
    void Abort(Transaction* txn);

private:
    LockManager* lock_manager_;
    LogManager* log_manager_;
    std::atomic<txn_id_t> next_txn_id_{0};
};
```

**MVCC Extension:**

```cpp
// Tuple with version info
class VersionedTuple {
public:
    txn_id_t GetBeginTimestamp() const { return begin_ts_; }
    txn_id_t GetEndTimestamp() const { return end_ts_; }

    bool IsVisible(txn_id_t read_ts) const {
        return begin_ts_ <= read_ts && read_ts < end_ts_;
    }

private:
    txn_id_t begin_ts_;
    txn_id_t end_ts_{TXN_ID_MAX};
    Tuple data_;
    VersionedTuple* prev_version_{nullptr};  // Version chain
};
```

**Reading:**
- "Concurrency Control and Recovery in Database Systems" (Bernstein)
- CMU 15-445 lectures on concurrency control
- "An Empirical Evaluation of In-Memory MVCC" paper

---

### Phase 6: Recovery and Production (Month 12)

**Build:** Crash recovery and production features

**Features:**
- Write-ahead logging (WAL)
- ARIES recovery algorithm
- Checkpointing
- Log-based recovery
- Simple CLI interface
- Performance benchmarks

**Skills Learned:**
- Durability guarantees
- Log-structured systems
- Crash recovery
- System integration

**Core Classes:**

```cpp
// Log record types
enum class LogRecordType {
    INVALID,
    INSERT,
    DELETE,
    UPDATE,
    BEGIN,
    COMMIT,
    ABORT,
    CHECKPOINT,
};

// Log record
class LogRecord {
public:
    LogRecord() = default;

    // For INSERT/DELETE/UPDATE
    LogRecord(txn_id_t txn_id, lsn_t prev_lsn, LogRecordType type,
              const RID& rid, const Tuple& tuple);

    // Serialize/deserialize
    int SerializeTo(char* dest) const;
    static LogRecord DeserializeFrom(const char* src);

    txn_id_t GetTxnId() const { return txn_id_; }
    lsn_t GetLSN() const { return lsn_; }
    lsn_t GetPrevLSN() const { return prev_lsn_; }
    LogRecordType GetType() const { return type_; }

private:
    int size_{0};
    lsn_t lsn_{INVALID_LSN};
    txn_id_t txn_id_{INVALID_TXN_ID};
    lsn_t prev_lsn_{INVALID_LSN};
    LogRecordType type_{LogRecordType::INVALID};

    // For data modification records
    RID rid_;
    Tuple old_tuple_;  // For undo
    Tuple new_tuple_;  // For redo
};

// Log manager
class LogManager {
public:
    explicit LogManager(DiskManager* disk_manager);

    lsn_t AppendLogRecord(LogRecord& log_record);
    void Flush();

    // Background flushing
    void RunFlushThread();
    void StopFlushThread();

private:
    char log_buffer_[LOG_BUFFER_SIZE];
    int buffer_offset_{0};

    std::atomic<lsn_t> next_lsn_{0};
    std::atomic<lsn_t> persistent_lsn_{INVALID_LSN};

    DiskManager* disk_manager_;
    std::mutex latch_;
    std::condition_variable flush_cv_;
    std::thread flush_thread_;
    std::atomic<bool> flush_thread_running_{false};
};

// Recovery manager (ARIES)
class RecoveryManager {
public:
    RecoveryManager(LogManager* log_manager,
                    BufferPoolManager* buffer_pool_manager);

    void Recover();

private:
    // ARIES phases
    void Analysis();     // Scan log to build ATT and DPT
    void Redo();         // Redo all actions
    void Undo();         // Undo uncommitted transactions

    LogManager* log_manager_;
    BufferPoolManager* buffer_pool_manager_;

    // Active Transaction Table
    std::unordered_map<txn_id_t, lsn_t> active_txn_table_;
    // Dirty Page Table
    std::unordered_map<PageId, lsn_t> dirty_page_table_;
};
```

**CLI Interface:**

```cpp
class CLI {
public:
    void Run();

private:
    void ExecuteCommand(const std::string& input);
    void PrintResult(const QueryResult& result);

    Database db_;
};

// Usage:
// minidb> CREATE TABLE users (id INT, name VARCHAR(100));
// minidb> INSERT INTO users VALUES (1, 'Alice');
// minidb> SELECT * FROM users;
// minidb> BEGIN;
// minidb> UPDATE users SET name = 'Bob' WHERE id = 1;
// minidb> COMMIT;
```

**Benchmarking:**

```cpp
void BenchmarkSequentialScan() {
    // Insert N tuples
    // Measure sequential scan time
    // Report throughput (tuples/sec)
}

void BenchmarkIndexScan() {
    // Insert N tuples
    // Build index
    // Measure point lookups and range scans
    // Report throughput
}

void BenchmarkTransactions() {
    // Run YCSB-like workload
    // Measure transactions/sec at different contention levels
}
```

**Reading:**
- ARIES paper
- CMU 15-445 lectures on recovery
- PostgreSQL WAL documentation

---

## Project Progression

Projects are ordered by complexity. Each builds on concepts from the previous.

### Level 1: Memory & Data Structures

#### Project 1.1: `custom_vector`
**Implement `std::vector` from scratch**

Features:
- Dynamic array with growth strategy
- Copy and move operations
- Iterator support
- Exception safety

**Concepts learned:**
- Memory allocation
- RAII
- Rule of five
- Iterator patterns

---

#### Project 1.2: `smart_ptr`
**Implement `unique_ptr` and `shared_ptr`**

Features:
- `unique_ptr` with custom deleters
- `shared_ptr` with thread-safe reference counting
- `weak_ptr` to break cycles
- `make_unique` and `make_shared`

**Concepts learned:**
- Ownership semantics
- Atomic operations
- Control block design
- Template techniques

---

#### Project 1.3: `hash_map`
**Implement an unordered map**

Features:
- Open addressing or chaining
- Custom hash functions
- Rehashing
- Iterator invalidation handling

**Concepts learned:**
- Hash table design
- Load factor management
- Template specialization

---

### Level 2: Systems Programming

#### Project 2.1: `memory_allocator`
**Custom malloc/free implementation**

Features:
- Free list management
- Coalescing free blocks
- Multiple allocation strategies (first-fit, best-fit, buddy)
- Thread-local caches

**Concepts learned:**
- Memory management internals
- Fragmentation
- Performance tradeoffs
- System calls (sbrk, mmap)

---

#### Project 2.2: `thread_pool`
**Work-stealing thread pool**

Features:
- Submit tasks, get futures
- Work stealing between threads
- Graceful shutdown
- Task cancellation

**Concepts learned:**
- Thread management
- Lock-free queues
- Future/promise pattern
- Concurrency patterns

---

#### Project 2.3: `logger`
**High-performance logging system**

Features:
- Multiple log levels
- Async logging (background thread)
- Log rotation
- Structured logging (JSON)
- Zero-allocation fast path

**Concepts learned:**
- Producer-consumer patterns
- Lock-free ring buffers
- Formatting performance
- File I/O

---

### Level 3: Networking

#### Project 3.1: `tcp_server`
**Event-driven TCP server**

Features:
- epoll/kqueue based event loop
- Non-blocking I/O
- Connection management
- Timeout handling

**Concepts learned:**
- Network programming
- Event-driven architecture
- System calls
- State machines

---

#### Project 3.2: `http_server`
**HTTP/1.1 server from scratch**

Features:
- Request parsing
- Response generation
- Static file serving
- Keep-alive connections
- Basic routing

**Concepts learned:**
- HTTP protocol
- Parser design
- Buffer management
- MIME types

---

#### Project 3.3: `rpc_framework`
**Simple RPC framework**

Features:
- IDL definition (or protobuf)
- Code generation
- Serialization/deserialization
- Connection pooling
- Timeouts and retries

**Concepts learned:**
- Serialization formats
- Code generation
- Client-server patterns
- Error handling

---

### Level 4: Compilers & Languages

#### Project 4.1: `expression_evaluator`
**Calculator with variables**

Features:
- Lexer and parser
- AST representation
- Evaluation
- Variables and functions

**Concepts learned:**
- Parsing (recursive descent)
- AST design
- Visitor pattern
- Symbol tables

---

#### Project 4.2: `interpreter`
**Interpreter for a simple language**

Features:
- Lexer, parser, AST
- Variables, functions, control flow
- Basic type system
- REPL

**Concepts learned:**
- Language implementation
- Scoping rules
- Function calls
- Error reporting

---

#### Project 4.3: `jit_compiler`
**JIT compile expressions to machine code**

Features:
- Generate x86-64 or ARM64 code
- Or use LLVM as backend
- Benchmark vs interpreter

**Concepts learned:**
- Code generation
- Assembly basics
- CPU architecture
- LLVM API

---

### Level 5: Game Engine Components

#### Project 5.1: `entity_component_system`
**ECS for game engines**

Features:
- Entities as IDs
- Components as data
- Systems operate on components
- Archetypal or sparse set storage

**Concepts learned:**
- Data-oriented design
- Cache efficiency
- Template metaprogramming
- Memory layout

---

#### Project 5.2: `physics_engine`
**2D or 3D physics**

Features:
- Rigid body dynamics
- Collision detection (broad + narrow phase)
- Collision response
- Constraints/joints

**Concepts learned:**
- Numerical integration
- Spatial data structures
- Linear algebra
- Optimization

---

#### Project 5.3: `renderer`
**OpenGL or Vulkan renderer**

Features:
- Mesh loading
- Shaders
- Texturing
- Basic lighting
- Scene graph

**Concepts learned:**
- Graphics APIs
- GPU programming
- Rendering pipeline
- Math (matrices, transforms)

---

## Open Source Study

### Projects to Read (In Order of Complexity)

#### Beginner
| Project | Why Study It |
|---------|--------------|
| **Google Test** | Testing framework design |
| **spdlog** | High-performance logging |
| **nlohmann/json** | Modern C++ API design |
| **Catch2** | Header-only testing |

#### Intermediate
| Project | Why Study It |
|---------|--------------|
| **abseil** | Google's C++ library, best practices |
| **folly** | Facebook's C++ library, advanced techniques |
| **gRPC** | RPC framework, code generation |
| **libuv** | Event loop (Node.js base) |

#### Advanced
| Project | Why Study It |
|---------|--------------|
| **LLVM** | Compiler infrastructure |
| **Chromium** | Large codebase, browser architecture |
| **RocksDB** | Storage engine (LSM tree) |
| **ClickHouse** | Analytical database |
| **LevelDB** | Simple key-value store |

#### Expert
| Project | Why Study It |
|---------|--------------|
| **PostgreSQL** (C but C++ patterns) | Database architecture |
| **MongoDB** | Document database |
| **TensorFlow** | ML framework, GPU |
| **Unreal Engine** (if licensed) | Game engine |

### How to Study Open Source

1. **Start with a small feature** - Trace a single operation through the code
2. **Read tests first** - They show intended usage
3. **Use a debugger** - Step through execution to understand flow
4. **Read issues and PRs** - Understand design decisions
5. **Build and modify** - Make small changes to understand impact

---

## Common Pitfalls

### Memory Errors

**1. Use after free**
```cpp
// Bad
std::vector<int> v = {1, 2, 3};
int& ref = v[0];
v.push_back(4);  // May reallocate
use(ref);        // Dangling reference!

// Good
std::vector<int> v = {1, 2, 3};
v.push_back(4);
int& ref = v[0];  // Get reference after modification
use(ref);
```

**2. Double free**
```cpp
// Bad: Raw pointer copied
char* p = new char[100];
char* q = p;
delete[] p;
delete[] q;  // Double free!

// Good: Use unique_ptr
auto p = std::make_unique<char[]>(100);
// Only one owner, automatically freed
```

**3. Memory leaks**
```cpp
// Bad: Early return leaks
void process() {
    char* buf = new char[1024];
    if (error) return;  // Leak!
    delete[] buf;
}

// Good: RAII
void process() {
    auto buf = std::make_unique<char[]>(1024);
    if (error) return;  // Automatically freed
}
```

### Concurrency Errors

**1. Data races**
```cpp
// Bad: Unsynchronized access
int counter = 0;
void increment() { counter++; }  // Not atomic!

// Good: Use atomic or mutex
std::atomic<int> counter{0};
void increment() { counter++; }  // Atomic
```

**2. Deadlock**
```cpp
// Bad: Lock ordering violation
std::mutex m1, m2;
void thread1() { std::lock_guard g1(m1); std::lock_guard g2(m2); }
void thread2() { std::lock_guard g1(m2); std::lock_guard g2(m1); }  // Deadlock!

// Good: Consistent ordering or std::lock
void thread1() { std::scoped_lock lock(m1, m2); }
void thread2() { std::scoped_lock lock(m1, m2); }  // Same order
```

**3. Dangling reference to local**
```cpp
// Bad
std::thread t;
void spawn() {
    int local = 42;
    t = std::thread([&local] { use(local); });  // local destroyed before thread runs!
}

// Good: Capture by value or ensure lifetime
void spawn() {
    int local = 42;
    t = std::thread([local] { use(local); });  // Copied
}
```

### Undefined Behavior

**1. Signed integer overflow**
```cpp
// Bad: UB
int x = INT_MAX;
x = x + 1;  // Undefined!

// Good: Use unsigned or check
unsigned x = UINT_MAX;
x = x + 1;  // Wraps to 0 (defined)
```

**2. Null pointer dereference**
```cpp
// Bad
Foo* p = nullptr;
p->method();  // UB

// Good: Check or use optional
if (p) p->method();
```

**3. Strict aliasing**
```cpp
// Bad: Type punning via pointer cast
float f = 1.0f;
int i = *(int*)&f;  // UB (strict aliasing violation)

// Good: Use memcpy or std::bit_cast (C++20)
float f = 1.0f;
int i;
std::memcpy(&i, &f, sizeof(i));  // Defined
// Or: int i = std::bit_cast<int>(f);
```

### Performance

**1. Unnecessary copies**
```cpp
// Bad
std::string process(std::string s) {  // Copied on call
    return s + "suffix";               // Another copy
}

// Good
std::string process(std::string_view s) {  // No copy
    return std::string(s) + "suffix";
}
```

**2. Virtual function overhead in hot loops**
```cpp
// Bad: Virtual call overhead
for (int i = 0; i < 1000000; i++) {
    obj->virtualMethod();  // Indirect call
}

// Good: Devirtualize if possible, or CRTP
template<typename Derived>
class Base {
    void method() { static_cast<Derived*>(this)->methodImpl(); }
};
```

---

## Daily Habits

### The 2-Hour Daily Practice

| Time | Activity |
|------|----------|
| 30 min | Read C++ code (stdlib, open source) |
| 60 min | Write code (project or exercises) |
| 15 min | Watch CppCon talks or read articles |
| 15 min | Use Compiler Explorer - understand generated assembly |

### Weekly Goals

- **Monday-Friday:** Work on current project
- **Saturday:** Code review / read production code
- **Sunday:** Plan next week, review learnings

### Reading Code Practice

Each week, study one component:

**Week 1-4:** Standard library
- `<vector>`, `<string>`
- `<memory>` (smart pointers)
- `<algorithm>`
- `<atomic>`, `<mutex>`

**Week 5-8:** Popular libraries
- spdlog (logging)
- nlohmann/json
- abseil strings
- folly data structures

**Week 9+:** Systems
- RocksDB write path
- gRPC serialization
- LLVM pass manager

---

## 12-Month Schedule

### Core Path (Months 1-6) - Foundations

| Month | Focus | Books | Projects |
|-------|-------|-------|----------|
| 1 | C++ basics | C++ Primer Ch 1-7 | custom_vector |
| 2 | Classes, copy control | C++ Primer Ch 7-13 | smart_ptr |
| 3 | Templates, STL | C++ Primer Ch 14-16, Effective Modern C++ 1-11 | hash_map |
| 4 | Modern C++ | Effective Modern C++ 12-33 | memory_allocator |
| 5 | Move semantics, perfect forwarding | Effective Modern C++ 23-33 | thread_pool |
| 6 | Concurrency | C++ Concurrency Ch 1-4 | logger |

### Database Engine Project (Months 7-12) - Systems Mastery

| Month | Focus | Books | MiniDB Phase |
|-------|-------|-------|--------------|
| 7 | Storage | CSAPP Ch 6, Database Internals Ch 1-3 | **Phase 1:** Storage Engine (pages, disk I/O) |
| 8 | Caching | Database Internals Ch 4-5 | **Phase 2:** Buffer Pool (LRU, pinning) |
| 9 | Data structures | Database Internals Ch 6-8 | **Phase 3:** B+ Tree Index |
| 10 | Query processing | Architecture of a Database System | **Phase 4:** Query Execution (volcano model) |
| 11 | Concurrency | C++ Concurrency Ch 5-8, 2PL/MVCC papers | **Phase 5:** Transactions (2PL, MVCC) |
| 12 | Recovery | ARIES paper | **Phase 6:** WAL, Recovery, CLI |

### Skills Progression

| Month | Core Skills | Systems Skills |
|-------|-------------|----------------|
| 1-2 | Memory management, RAII, classes | - |
| 3-4 | Templates, STL, move semantics | - |
| 5-6 | Concurrency primitives, atomics | - |
| 7 | - | File I/O, page layout, serialization |
| 8 | - | Cache design, replacement policies |
| 9 | - | B+ tree algorithms, iterators |
| 10 | - | Parser design, iterator patterns |
| 11 | - | Locking, deadlock detection, MVCC |
| 12 | - | WAL, crash recovery, benchmarking |

---

## The Path to Cracked

### Beginner (Months 1-3)
You can:
- Write correct C++ code
- Use RAII for resource management
- Understand copy vs move
- Use STL containers and algorithms
- Write classes with proper copy/move

### Intermediate (Months 4-6)
You can:
- Write templates
- Use smart pointers correctly
- Write concurrent code with mutexes
- Understand undefined behavior
- Profile and optimize

### Advanced (Months 7-9)
After MiniDB Phases 1-3, you can:
- Design storage engines
- Implement buffer management
- Build complex data structures
- Understand database internals
- Write systems code

### Cracked (Months 10-12+)
After completing MiniDB, you can:
- Build database components
- Implement query executors
- Design concurrency control
- Implement crash recovery
- Understand production systems
- Contribute to database projects (RocksDB, DuckDB)

---

## Resources Quick Reference

### Bookmarks

```
# Official
isocpp.org                    # ISO C++ site
cppreference.com              # THE reference
godbolt.org                   # Compiler Explorer

# Learning
learncpp.com                  # Tutorials
cppquiz.org                   # Quiz yourself

# Community
reddit.com/r/cpp              # Discussion
isocpp.org/blog               # News
meetingcpp.com                # Conference

# Reference
github.com/isocpp/CppCoreGuidelines  # Guidelines
abseil.io/tips                # Abseil tips
```

### Key People to Follow

**Language:**
- **Bjarne Stroustrup** - Creator
- **Herb Sutter** - Chair of ISO C++
- **Kate Gregory** - Educator
- **Jason Turner** - C++ Weekly

**Systems:**
- **Chandler Carruth** - LLVM, performance
- **Andrei Alexandrescu** - Generic programming
- **Sean Parent** - Adobe, algorithms
- **Fedor Pikus** - Performance, concurrency

### Conferences

- **CppCon** - Main conference (all talks on YouTube)
- **C++ Now** - Advanced topics
- **Meeting C++** - European conference
- **ACCU** - UK conference

### Podcasts

- **CppCast** - Weekly C++ news
- **ADSP** - Algorithms + Data Structures

---

## Final Words

C++ is a mountain. It takes years to climb, but the view is worth it.

What sets C++ apart:
1. **Control** - You decide exactly what happens
2. **Performance** - Zero-overhead abstractions
3. **Longevity** - Codebases last decades
4. **Interoperability** - Works with everything

### The MiniDB Advantage

Building a database engine is the ultimate C++ project because:
- **It's systems programming** - Disk I/O, memory management, concurrency
- **It requires correctness** - Transactions must be ACID
- **It demands performance** - Every cycle counts
- **It teaches design** - Layered architecture, clean interfaces
- **It's real** - These are the same concepts in PostgreSQL, MySQL, RocksDB

Most tutorials teach syntax. Building MiniDB teaches you to think like a systems programmer.

### What Comes After

Once you've completed MiniDB, you can:
- **Extend it** - Add a query optimizer, more join algorithms, distributed transactions
- **Contribute** - DuckDB, RocksDB, and other projects welcome contributors
- **Work on production systems** - You now understand how databases work internally
- **Build other systems** - The patterns transfer to file systems, game engines, compilers

The infrastructure that runs the world's data is written in C++. Oracle, SQL Server, MySQL, PostgreSQL's performance-critical parts - all C or C++. By mastering C++ through building a database, you join the ranks of those who build the foundations others build upon.

Start today. Build something. Read code. Understand the machine.

---

*Generated: January 2026*
