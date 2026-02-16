# Becoming Cracked at Go

A comprehensive guide to mastering Go for web development, cloud native systems, and infrastructure.

---

## Table of Contents

1. [Why Go](#why-go)
2. [Core Mental Models](#core-mental-models)
3. [Books: The Foundation](#books-the-foundation)
4. [Structured Reading Path](#structured-reading-path)
5. [Video Resources](#video-resources)
6. [Tools: Your Arsenal](#tools-your-arsenal)
7. [Development Setup](#development-setup)
8. [Specialization Tracks](#specialization-tracks)
9. [The Launchpad Project](#the-launchpad-project)
   - [Phase 1: Foundation API](#phase-1-foundation-api-month-7)
   - [Phase 2: App Deployment API](#phase-2-app-deployment-api-month-8)
   - [Phase 3: First Kubernetes Controller](#phase-3-first-kubernetes-controller-month-9)
   - [Phase 4: Connect API to Operator](#phase-4-connect-api-to-operator-month-10)
   - [Phase 5: Advanced Operator Features](#phase-5-advanced-operator-features-month-11)
   - [Phase 6: CLI & Production Polish](#phase-6-cli--production-polish-month-12)
10. [Project Progression](#project-progression)
11. [Open Source Study](#open-source-study)
12. [Common Pitfalls](#common-pitfalls)
13. [Daily Habits](#daily-habits)
14. [12-Month Schedule](#12-month-schedule)
15. [The Path to Cracked](#the-path-to-cracked)

---

## Why Go

Go was designed by Rob Pike, Ken Thompson, and Robert Griesemer at Google to solve real problems:

- **Fast compilation** - Go compiles in seconds, not minutes
- **Simplicity** - Small language spec, easy to read others' code
- **Built-in concurrency** - Goroutines and channels are first-class
- **Single binary deployment** - No runtime dependencies
- **Great standard library** - `net/http`, `encoding/json`, `testing` are production-ready

Go powers: Docker, Kubernetes, Terraform, Prometheus, etcd, CockroachDB, Vault, Consul, and most modern infrastructure tools.

---

## Core Mental Models

### 1. Simplicity is a Feature

Go intentionally lacks:
- Generics complexity (they exist now, but keep them simple)
- Inheritance
- Exceptions
- Macros

This is by design. Embrace it. Fight the urge to make things "clever."

```go
// Bad: Trying to be clever
func Process[T any, F func(T) T](items []T, fns ...F) []T { ... }

// Good: Simple and readable
func ProcessStrings(items []string, transform func(string) string) []string {
    result := make([]string, len(items))
    for i, item := range items {
        result[i] = transform(item)
    }
    return result
}
```

### 2. Goroutines Are Cheap, Use Them

Goroutines cost ~2KB stack (grows as needed). Spawn thousands.

```go
// This is fine
for _, url := range urls {
    go func(u string) {
        fetch(u)
    }(url)
}
```

But always think: **"How does this goroutine stop?"**

### 3. Share Memory by Communicating

The Go proverb: "Don't communicate by sharing memory; share memory by communicating."

```go
// Instead of this (shared memory with mutex):
var count int
var mu sync.Mutex

func increment() {
    mu.Lock()
    count++
    mu.Unlock()
}

// Consider this (communicate via channel):
func counter(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        count := 0
        for n := range in {
            count += n
        }
        out <- count
        close(out)
    }()
    return out
}
```

**But:** Mutexes are fine too. Don't force channels where a mutex is cleaner.

### 4. Interfaces Are Implicit

You don't declare that a type implements an interface. It just does if it has the methods.

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

// os.File implements Reader without declaring it
// bytes.Buffer implements Reader without declaring it
// Your type can too
```

Design around small interfaces. The smaller, the more useful.

### 5. Errors Are Values

Errors are not exceptions. They're returned values you handle explicitly.

```go
f, err := os.Open(filename)
if err != nil {
    return fmt.Errorf("opening config: %w", err)
}
defer f.Close()
```

This is verbose but explicit. You always know what can fail.

### 6. Context for Control Flow

`context.Context` carries deadlines, cancellation, and request-scoped values.

```go
func fetchData(ctx context.Context, url string) ([]byte, error) {
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, err
    }
    // Request will be cancelled if ctx is cancelled
    resp, err := http.DefaultClient.Do(req)
    // ...
}
```

Every long-running function should accept a context as its first parameter.

### 7. Zero Values Are Useful

In Go, uninitialized variables have zero values:
- `int`: 0
- `string`: ""
- `bool`: false
- `pointer/slice/map/channel`: nil

Design your types so zero values are useful:

```go
// sync.Mutex zero value is an unlocked mutex - ready to use
var mu sync.Mutex

// bytes.Buffer zero value is an empty buffer - ready to use
var buf bytes.Buffer
buf.WriteString("hello")
```

---

## Books: The Foundation

### Essential (Read in Order)

| Order | Book | Focus | Why |
|-------|------|-------|-----|
| 1 | **"The Go Programming Language"** by Donovan & Kernighan | Complete language coverage | THE Go book. Written by one of the creators of C. Covers everything with depth. |
| 2 | **"Concurrency in Go"** by Katherine Cox-Buday | Goroutines, channels, patterns | Deep dive into Go's concurrency model. Essential for production Go. |
| 3 | **"100 Go Mistakes and How to Avoid Them"** by Teiva Harsanyi | Common pitfalls, best practices | Learn from others' mistakes. Covers subtle bugs you'll definitely hit. |

### Systems & Infrastructure

| Book | Focus | When to Read |
|------|-------|--------------|
| **"Powerful Command-Line Applications in Go"** by Ricardo Gerardi | CLI tools, cobra, viper | When building CLI tools |
| **"Network Programming with Go"** by Adam Woodbeck | TCP/UDP, protocols | When doing network programming |
| **"Distributed Services with Go"** by Travis Jeffery | Building distributed systems | After basics, when building services |
| **"Cloud Native Go"** by Matthew Titmus | Production systems, observability | When deploying to production |

### Web Development & APIs

| Book | Focus | When to Read |
|------|-------|--------------|
| **"Let's Go"** by Alex Edwards | Web fundamentals, templates, sessions | Starting web development |
| **"Let's Go Further"** by Alex Edwards | REST APIs, JSON, auth, deployment | After Let's Go |
| **"Web Development with Go"** by Jon Calhoun | Full-stack patterns | Alternative/supplement |
| **"Building Microservices with Go"** by Nic Jackson | Microservice patterns | When building distributed services |
| **"gRPC: Up and Running"** by Kasun Indrasiri | gRPC and protocol buffers | When building internal APIs |

### Cloud Native & Kubernetes

| Book | Focus | When to Read |
|------|-------|--------------|
| **"Programming Kubernetes"** by Hausenblas & Schimanski | Controllers, operators, CRDs | Essential for K8s development |
| **"Kubernetes Operators"** by Dobies & Wood | Operator pattern deep dive | When building operators |
| **"Kubernetes in Action"** by Marko Lukša | K8s fundamentals | If new to Kubernetes |
| **"Cloud Native DevOps with Kubernetes"** | Production K8s patterns | For deployment patterns |
| **"Production Kubernetes"** by Rosso, Lander, Brand, Harris | Real-world K8s | For advanced production use |

### Supporting Books (Not Go-specific but essential)

| Book | Focus |
|------|-------|
| **"Designing Data-Intensive Applications"** by Kleppmann | Distributed systems bible |
| **"The Linux Programming Interface"** by Kerrisk | Understanding syscalls Go wraps |
| **"Computer Systems: A Programmer's Perspective"** | Understanding what's beneath |

---

## Structured Reading Path

### Phase 1: Language Fundamentals (Weeks 1-6)

**Primary: "The Go Programming Language" (GOPL)**

| Week | Chapters | Focus | Exercises |
|------|----------|-------|-----------|
| 1 | Ch 1-2 | Tutorial, program structure | All exercises in Ch 1 |
| 2 | Ch 3-4 | Basic types, composites | Implement exercises, build small CLI |
| 3 | Ch 5-6 | Functions, methods | Refactor previous code with methods |
| 4 | Ch 7 | Interfaces | Implement io.Reader/Writer for something |
| 5 | Ch 8 | Goroutines, channels | Build concurrent pipeline |
| 6 | Ch 9 | Concurrency with shared memory | Race condition exercises |

**Supplement with:**
- Go Tour (tour.golang.org) - do this before the book
- Go by Example (gobyexample.com) - quick reference
- Effective Go (golang.org/doc/effective_go) - read after Ch 7

### Phase 2: Concurrency Deep Dive (Weeks 7-10)

**Primary: "Concurrency in Go"**

| Week | Chapters | Focus |
|------|----------|-------|
| 7 | Ch 1-2 | Why concurrency, modeling |
| 8 | Ch 3 | Go's concurrency building blocks |
| 9 | Ch 4 | Concurrency patterns |
| 10 | Ch 5-6 | Scale, goroutine management |

**Projects during this phase:**
- Worker pool implementation
- Pipeline with fan-out/fan-in
- Rate limiter

### Phase 3: Intermediate Patterns (Weeks 11-14)

**Primary: "100 Go Mistakes and How to Avoid Them"**

Read 5-10 mistakes per day. For each:
1. Understand the mistake
2. Write code that demonstrates it
3. Fix it

**Key sections:**
- Data types (#1-20)
- Control structures (#21-30)
- Strings (#31-40)
- Functions/methods (#41-50)
- Error management (#51-60)
- Concurrency (#61-80)
- Standard library (#81-90)
- Testing (#91-100)

### Phase 4: Domain Specialization (Weeks 15-20)

Choose your path (or combine them):

**Path A: Web Development & APIs**
- "Let's Go" and "Let's Go Further" by Alex Edwards
- "Building Microservices with Go" by Nic Jackson
- Build: REST API, GraphQL server, real-time WebSocket app
- Focus: HTTP, routing, middleware, auth, databases, testing

**Path B: Cloud Native & Kubernetes**
- "Programming Kubernetes" by Hausenblas & Schimanski
- "Kubernetes Operators" by Dobies & Wood
- Build: Custom controller, operator, admission webhook
- Focus: client-go, controller-runtime, CRDs, reconciliation

**Path C: Infrastructure & CLI Tools**
- "Powerful Command-Line Applications in Go"
- "Distributed Services with Go"
- Build: CLI tool suite, distributed KV, service mesh
- Focus: cobra, protocols, consensus

**Path D: Network Programming**
- "Network Programming with Go"
- Build: proxy, protocol implementation, scanner
- Focus: TCP/UDP, HTTP internals, TLS

### Phase 5: Production (Weeks 21-24)

**Primary: "Cloud Native Go"**

- Observability (metrics, tracing, logging)
- Resilience (circuit breakers, retries)
- Configuration management
- Deployment patterns

---

## Video Resources

### YouTube Channels

| Channel | Content |
|---------|---------|
| **GopherCon** | Conference talks, essential viewing |
| **Ardan Labs (Bill Kennedy)** | Deep technical Go content |
| **justforfunc (Francesc Campoy)** | Practical Go tutorials |
| **Melkey** | Modern Go development |
| **Anthony GG** | Go projects and patterns |
| **Dreams of Code** | Go tooling and projects |

### Must-Watch Talks

**Fundamentals:**
- "Go Proverbs" - Rob Pike (understand Go's philosophy)
- "Concurrency Is Not Parallelism" - Rob Pike
- "Simplicity Is Complicated" - Rob Pike

**Concurrency:**
- "Rethinking Classical Concurrency Patterns" - Bryan Mills (GopherCon 2018)
- "Advanced Testing with Go" - Mitchell Hashimoto
- "Understanding Channels" - Kavya Joshi

**Performance:**
- "Understanding Go's Memory Allocator" - Andre Carvalho
- "Profiling and Optimizing Go" - Brad Fitzpatrick
- "High Performance Go Workshop" - Dave Cheney

**Web Development:**
- "How I Write HTTP Services After 8 Years" - Mat Ryer
- "Building a Bank with Go" - Matt Heath
- "Go + Microservices = Go Kit" - Peter Bourgon
- "The Art of Graceful Shutdown" - various GopherCon talks
- "REST API Design Best Practices" - various

**Cloud Native & Kubernetes:**
- "Writing a Kubernetes Operator from Scratch" - various KubeCon talks
- "Kubernetes Controllers at Scale" - GopherCon
- "Deep Dive into Kubernetes Controllers" - KubeCon
- "client-go: The Good, The Bad and The Ugly" - KubeCon
- "Building Cloud Native Applications with Go" - various

**Production:**
- "Production-Ready Go" - various talks
- "Twelve Go Best Practices" - Francesc Campoy
- "Failure Is Always an Option" - Brian Ketelsen

### Courses

| Course | Platform | Focus |
|--------|----------|-------|
| **Go: The Complete Developer's Guide** | Udemy (Stephen Grider) | Visual, beginner-friendly |
| **Learn Go with Tests** | Free (quii.gitbook.io) | TDD approach, excellent |
| **Ardan Labs Go Training** | ardanlabs.com | Production Go, deep |
| **Boot.dev Backend Course** | boot.dev | Project-based learning |

---

## Tools: Your Arsenal

### Essential Tools

| Tool | Purpose | Install |
|------|---------|---------|
| **Go itself** | Latest stable | go.dev/dl |
| **gopls** | Language server (auto-installed by editors) | `go install golang.org/x/tools/gopls@latest` |
| **golangci-lint** | Linter aggregator | brew or binary |
| **delve** | Debugger | `go install github.com/go-delve/delve/cmd/dlv@latest` |
| **air** | Live reload for development | `go install github.com/cosmtrek/air@latest` |
| **gofumpt** | Stricter gofmt | `go install mvdan.cc/gofumpt@latest` |

### Profiling & Performance

| Tool | Purpose |
|------|---------|
| **pprof** | CPU/memory profiling (built-in) |
| **trace** | Execution tracing (built-in) |
| **benchstat** | Compare benchmarks |
| **go-torch** | Flamegraph generation |

### Testing

| Tool | Purpose |
|------|---------|
| **go test** | Built-in testing (excellent) |
| **testify** | Assertions and mocking |
| **gomock** | Interface mocking |
| **httptest** | HTTP testing (built-in) |
| **goleak** | Goroutine leak detection |

### Development

| Tool | Purpose |
|------|---------|
| **wire** | Dependency injection |
| **sqlc** | Type-safe SQL |
| **ent** | Entity framework |
| **cobra** | CLI framework |
| **viper** | Configuration |

### Web Development

| Tool | Purpose |
|------|---------|
| **chi** | Lightweight router |
| **gin** | Full-featured web framework |
| **echo** | High performance framework |
| **fiber** | Express-inspired framework |
| **gqlgen** | GraphQL code generation |
| **gorilla/websocket** | WebSocket library |
| **go-playground/validator** | Struct validation |
| **jwt-go / golang-jwt** | JWT handling |
| **oapi-codegen** | OpenAPI code generation |
| **swaggo/swag** | Swagger documentation |

### Cloud Native & Kubernetes

| Tool | Purpose |
|------|---------|
| **client-go** | Official K8s Go client |
| **controller-runtime** | Building controllers/operators |
| **kubebuilder** | Scaffold K8s APIs and controllers |
| **operator-sdk** | Build Kubernetes operators |
| **k8s.io/apimachinery** | K8s API types and utilities |
| **kind** | Local K8s clusters for testing |
| **envtest** | Test K8s controllers without cluster |
| **kustomize** | K8s configuration management |
| **helm-sdk** | Programmatic Helm |
| **ko** | Build and deploy Go to K8s |

---

## Development Setup

### Go Installation

```bash
# macOS
brew install go

# Or download from go.dev/dl for any platform
```

### Environment

```bash
# Add to ~/.zshrc or ~/.bashrc
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
```

### Editor Setup

**VS Code (Recommended for beginners):**
```
1. Install Go extension (by Go Team at Google)
2. Cmd+Shift+P → "Go: Install/Update Tools" → Select all
```

**Neovim (For the dedicated):**
```
Use LazyVim or AstroNvim with gopls
Or manually configure:
- nvim-lspconfig with gopls
- nvim-dap for debugging
- null-ls for linting
```

### Project Structure

```
myproject/
├── cmd/
│   └── myapp/
│       └── main.go           # Entry point
├── internal/
│   ├── handler/              # HTTP handlers
│   ├── service/              # Business logic
│   ├── repository/           # Data access
│   └── model/                # Domain types
├── pkg/                       # Public packages (use sparingly)
├── go.mod
├── go.sum
└── Makefile
```

### Makefile Template

```makefile
.PHONY: build test lint run

build:
	go build -o bin/app ./cmd/myapp

test:
	go test -race -cover ./...

lint:
	golangci-lint run

run:
	go run ./cmd/myapp
```

---

## Specialization Tracks

After mastering Go fundamentals, you'll combine Web Development and Kubernetes through a unified project that grows in complexity.

---

### Combined Track: Web + Cloud Native

This track builds one system progressively - a **Platform-as-a-Service (PaaS)** called **"Launchpad"** that lets developers deploy applications to Kubernetes. Each phase adds new capabilities and teaches new skills.

By the end, you'll have built something similar to a simplified Heroku/Railway/Render - a complete platform with APIs, operators, real-time updates, and production observability.

---

### Mental Models You'll Learn

#### From Web Development

**1. Handler as Pure Function**
```go
// Handlers should be stateless - take request, return response
func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "id")
    user, err := h.userService.Get(r.Context(), id)
    if err != nil {
        h.respondError(w, err)
        return
    }
    h.respondJSON(w, http.StatusOK, user)
}
```

**2. Middleware Chain**
```go
// Compose behavior through middleware stacking
r := chi.NewRouter()
r.Use(middleware.RequestID)
r.Use(middleware.Logger)
r.Use(middleware.Recoverer)
r.Use(h.AuthMiddleware)
r.Get("/users/{id}", h.GetUser)
```

**3. Repository Pattern for Data**
```go
type UserRepository interface {
    Get(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) error
    Update(ctx context.Context, user *User) error
    Delete(ctx context.Context, id string) error
}
```

**4. Service Layer for Business Logic**
```go
type UserService struct {
    repo  UserRepository
    cache Cache
    events EventPublisher
}

func (s *UserService) Create(ctx context.Context, input CreateUserInput) (*User, error) {
    // Validate
    if err := input.Validate(); err != nil {
        return nil, err
    }
    // Business logic
    user := input.ToUser()
    user.CreatedAt = time.Now()
    // Persist
    if err := s.repo.Create(ctx, user); err != nil {
        return nil, err
    }
    // Side effects
    s.events.Publish(ctx, UserCreatedEvent{User: user})
    return user, nil
}
```

#### From Kubernetes Development

**1. The Reconciliation Loop**
```go
// Controllers watch desired state and reconcile actual state
func (r *MyReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // 1. Fetch the resource
    var myResource v1.MyResource
    if err := r.Get(ctx, req.NamespacedName, &myResource); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // 2. Check actual state
    actual, err := r.getActualState(ctx, &myResource)

    // 3. Compare desired vs actual
    if !reflect.DeepEqual(myResource.Spec, actual) {
        // 4. Reconcile
        if err := r.reconcile(ctx, &myResource); err != nil {
            return ctrl.Result{RequeueAfter: time.Minute}, err
        }
    }

    // 5. Update status
    myResource.Status.Phase = "Ready"
    if err := r.Status().Update(ctx, &myResource); err != nil {
        return ctrl.Result{}, err
    }

    return ctrl.Result{}, nil
}
```

**2. Kubernetes API Conventions**
```go
// Resources follow conventions: Spec (desired) + Status (actual)
type MyResourceSpec struct {
    Replicas int32  `json:"replicas"`
    Image    string `json:"image"`
}

type MyResourceStatus struct {
    Phase           string `json:"phase"`
    ReadyReplicas   int32  `json:"readyReplicas"`
    ObservedGeneration int64 `json:"observedGeneration"`
}

type MyResource struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec   MyResourceSpec   `json:"spec,omitempty"`
    Status MyResourceStatus `json:"status,omitempty"`
}
```

**3. Owner References for Garbage Collection**
```go
// Child resources should reference their parent
func (r *Reconciler) createDeployment(ctx context.Context, parent *v1.MyResource) error {
    deployment := &appsv1.Deployment{
        ObjectMeta: metav1.ObjectMeta{
            Name:      parent.Name + "-deployment",
            Namespace: parent.Namespace,
        },
        // ...
    }

    // Set owner reference - when parent is deleted, child is too
    if err := ctrl.SetControllerReference(parent, deployment, r.Scheme); err != nil {
        return err
    }

    return r.Create(ctx, deployment)
}
```

**4. Finalizers for Cleanup**
```go
const myFinalizer = "myresource.example.com/finalizer"

func (r *Reconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var resource v1.MyResource
    if err := r.Get(ctx, req.NamespacedName, &resource); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Resource is being deleted
    if !resource.DeletionTimestamp.IsZero() {
        if containsString(resource.Finalizers, myFinalizer) {
            // Perform cleanup
            if err := r.cleanupExternalResources(ctx, &resource); err != nil {
                return ctrl.Result{}, err
            }
            // Remove finalizer
            resource.Finalizers = removeString(resource.Finalizers, myFinalizer)
            if err := r.Update(ctx, &resource); err != nil {
                return ctrl.Result{}, err
            }
        }
        return ctrl.Result{}, nil
    }

    // Add finalizer if not present
    if !containsString(resource.Finalizers, myFinalizer) {
        resource.Finalizers = append(resource.Finalizers, myFinalizer)
        if err := r.Update(ctx, &resource); err != nil {
            return ctrl.Result{}, err
        }
    }

    // Normal reconciliation...
}
```

---

## The Launchpad Project

**What you're building:** A Platform-as-a-Service that lets developers deploy applications to Kubernetes via API or CLI.

**Why this project:** It naturally combines REST APIs, real-time features, Kubernetes controllers, operators, and production patterns. Every phase teaches skills that build on the previous ones.

**Architecture Overview:**
```
┌─────────────────────────────────────────────────────────────────┐
│                         Launchpad                                │
├─────────────────────────────────────────────────────────────────┤
│  CLI (launchpad)     │  Web Dashboard     │  REST/GraphQL API   │
├─────────────────────────────────────────────────────────────────┤
│                      API Server (Go)                             │
│  - Auth (JWT)        - App management      - Real-time (WS)     │
│  - Teams/Projects    - Deployments         - Logs streaming     │
├─────────────────────────────────────────────────────────────────┤
│                    Kubernetes Operators                          │
│  - App Controller    - Build Controller   - Domain Controller   │
├─────────────────────────────────────────────────────────────────┤
│                       Kubernetes                                 │
│  Deployments, Services, Ingress, ConfigMaps, Secrets            │
└─────────────────────────────────────────────────────────────────┘
```

---

### Phase 1: Foundation API (Month 7)

**Build:** Core REST API for user and project management

**Features:**
- User registration and authentication (JWT)
- Team creation and membership
- Project CRUD operations
- PostgreSQL database with migrations
- Input validation
- Structured logging
- Health endpoints

**Skills Learned:**
- HTTP handlers and routing (chi)
- Middleware (auth, logging, recovery)
- Database patterns (sqlc or raw SQL)
- JWT authentication
- Configuration management (viper)
- Testing (unit + integration)

**Project Structure:**
```
launchpad/
├── cmd/
│   └── api/
│       └── main.go
├── internal/
│   ├── api/
│   │   ├── handler/
│   │   │   ├── user.go
│   │   │   ├── team.go
│   │   │   └── project.go
│   │   ├── middleware/
│   │   │   ├── auth.go
│   │   │   └── logging.go
│   │   └── router.go
│   ├── service/
│   │   ├── user.go
│   │   ├── team.go
│   │   └── project.go
│   ├── repository/
│   │   ├── user.go
│   │   ├── team.go
│   │   └── project.go
│   └── model/
│       └── models.go
├── pkg/
│   └── auth/
│       └── jwt.go
├── migrations/
├── go.mod
└── Makefile
```

**Endpoints:**
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/users/me
POST   /api/v1/teams
GET    /api/v1/teams
POST   /api/v1/teams/:id/members
POST   /api/v1/projects
GET    /api/v1/projects
GET    /api/v1/projects/:id
PUT    /api/v1/projects/:id
DELETE /api/v1/projects/:id
```

**Reading:**
- "Let's Go" chapters 1-10
- chi documentation
- sqlc documentation

---

### Phase 2: App Deployment API (Month 8)

**Build:** API for defining and triggering app deployments

**Features:**
- App definition (name, image, env vars, replicas, ports)
- Deployment creation and management
- Environment management (dev, staging, prod)
- Secrets management
- Deployment history
- Rollback support

**Skills Learned:**
- Complex domain modeling
- State machines (deployment states)
- Validation with go-playground/validator
- API versioning
- Pagination and filtering
- OpenAPI documentation (swaggo)

**New Endpoints:**
```
POST   /api/v1/projects/:id/apps
GET    /api/v1/projects/:id/apps
GET    /api/v1/apps/:id
PUT    /api/v1/apps/:id
DELETE /api/v1/apps/:id

POST   /api/v1/apps/:id/deployments
GET    /api/v1/apps/:id/deployments
GET    /api/v1/deployments/:id
POST   /api/v1/deployments/:id/rollback

POST   /api/v1/apps/:id/env
GET    /api/v1/apps/:id/env
PUT    /api/v1/apps/:id/env/:key
DELETE /api/v1/apps/:id/env/:key
```

**App Model:**
```go
type App struct {
    ID          string            `json:"id"`
    ProjectID   string            `json:"projectId"`
    Name        string            `json:"name"`
    Image       string            `json:"image"`
    Replicas    int32             `json:"replicas"`
    Port        int32             `json:"port"`
    Environment map[string]string `json:"environment"`
    Status      AppStatus         `json:"status"`
    CreatedAt   time.Time         `json:"createdAt"`
    UpdatedAt   time.Time         `json:"updatedAt"`
}

type Deployment struct {
    ID        string           `json:"id"`
    AppID     string           `json:"appId"`
    Version   int              `json:"version"`
    Image     string           `json:"image"`
    Status    DeploymentStatus `json:"status"` // pending, building, deploying, running, failed
    CreatedAt time.Time        `json:"createdAt"`
    StartedAt *time.Time       `json:"startedAt"`
    FinishedAt *time.Time      `json:"finishedAt"`
}
```

**Reading:**
- "Let's Go Further" chapters 1-15
- OpenAPI 3.0 specification

---

### Phase 3: First Kubernetes Controller (Month 9)

**Build:** Kubernetes controller that deploys apps based on CRD

**Features:**
- Custom Resource Definition (LaunchpadApp)
- Controller watches LaunchpadApp resources
- Creates Deployment, Service, Ingress for each app
- Status reflects actual deployment state
- Handles updates (rolling updates)
- Handles deletes (cleanup)

**Skills Learned:**
- kubebuilder scaffolding
- CRD design
- Reconciliation loop
- Owner references
- Status subresource
- Kubernetes client-go basics
- envtest for testing

**CRD Design:**
```yaml
apiVersion: launchpad.io/v1alpha1
kind: LaunchpadApp
metadata:
  name: my-app
  namespace: default
spec:
  image: nginx:latest
  replicas: 3
  port: 80
  env:
    - name: DATABASE_URL
      value: postgres://...
status:
  phase: Running
  replicas: 3
  readyReplicas: 3
  conditions:
    - type: Available
      status: "True"
      lastTransitionTime: "2024-01-15T10:00:00Z"
```

**Controller Logic:**
```go
func (r *LaunchpadAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    log := log.FromContext(ctx)

    // Fetch the LaunchpadApp
    var app launchpadv1.LaunchpadApp
    if err := r.Get(ctx, req.NamespacedName, &app); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Create or update Deployment
    if err := r.reconcileDeployment(ctx, &app); err != nil {
        return ctrl.Result{}, err
    }

    // Create or update Service
    if err := r.reconcileService(ctx, &app); err != nil {
        return ctrl.Result{}, err
    }

    // Create or update Ingress
    if err := r.reconcileIngress(ctx, &app); err != nil {
        return ctrl.Result{}, err
    }

    // Update status
    if err := r.updateStatus(ctx, &app); err != nil {
        return ctrl.Result{}, err
    }

    return ctrl.Result{}, nil
}
```

**Project Structure:**
```
launchpad-operator/
├── api/
│   └── v1alpha1/
│       ├── launchpadapp_types.go
│       └── zz_generated.deepcopy.go
├── cmd/
│   └── main.go
├── config/
│   ├── crd/
│   ├── manager/
│   ├── rbac/
│   └── samples/
├── internal/
│   └── controller/
│       ├── launchpadapp_controller.go
│       └── launchpadapp_controller_test.go
├── go.mod
└── Makefile
```

**Reading:**
- kubebuilder book (book.kubebuilder.io)
- "Programming Kubernetes" chapters 1-6

---

### Phase 4: Connect API to Operator (Month 10)

**Build:** API server creates Kubernetes resources, watches for changes

**Features:**
- API creates LaunchpadApp CRs when deployments triggered
- Watch Kubernetes for status updates
- Sync status back to database
- Real-time status updates via WebSocket
- Log streaming from pods

**Skills Learned:**
- Kubernetes client-go informers
- WebSocket implementation
- Real-time event streaming
- Pod log streaming
- Kubernetes RBAC for API server

**Architecture:**
```
User → API Server → Creates LaunchpadApp CR → Operator reconciles → Creates Deployment/Service/Ingress
                  ← Watches LaunchpadApp status ←
                  ← Streams pod logs ←
         ↓
      WebSocket → Dashboard shows real-time status
```

**WebSocket Events:**
```go
type DeploymentEvent struct {
    Type      string    `json:"type"` // status_change, log, error
    AppID     string    `json:"appId"`
    Status    string    `json:"status,omitempty"`
    Log       string    `json:"log,omitempty"`
    Timestamp time.Time `json:"timestamp"`
}

// Handler for WebSocket connection
func (h *Handler) StreamDeployment(w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        return
    }
    defer conn.Close()

    appID := chi.URLParam(r, "id")

    // Subscribe to events for this app
    events := h.eventBus.Subscribe(appID)
    defer h.eventBus.Unsubscribe(appID, events)

    for event := range events {
        if err := conn.WriteJSON(event); err != nil {
            return
        }
    }
}
```

**Log Streaming:**
```go
func (s *K8sService) StreamLogs(ctx context.Context, appName, namespace string) (<-chan string, error) {
    pods, err := s.clientset.CoreV1().Pods(namespace).List(ctx, metav1.ListOptions{
        LabelSelector: fmt.Sprintf("app=%s", appName),
    })
    if err != nil {
        return nil, err
    }

    logs := make(chan string)

    for _, pod := range pods.Items {
        go func(podName string) {
            req := s.clientset.CoreV1().Pods(namespace).GetLogs(podName, &corev1.PodLogOptions{
                Follow: true,
            })
            stream, err := req.Stream(ctx)
            if err != nil {
                return
            }
            defer stream.Close()

            scanner := bufio.NewScanner(stream)
            for scanner.Scan() {
                logs <- fmt.Sprintf("[%s] %s", podName, scanner.Text())
            }
        }(pod.Name)
    }

    return logs, nil
}
```

**Reading:**
- gorilla/websocket documentation
- client-go examples (informers, watches)
- Kubernetes pod logs API

---

### Phase 5: Advanced Operator Features (Month 11)

**Build:** Production-ready operator with advanced patterns

**Features:**
- Admission webhooks (validate app specs)
- Mutating webhooks (inject sidecars, defaults)
- Finalizers for cleanup
- Horizontal Pod Autoscaler integration
- Custom metrics
- Multi-environment support (namespaces)

**Skills Learned:**
- Admission webhooks
- Webhook certificate management
- Finalizer patterns
- HPA integration
- Prometheus metrics
- Multi-tenant patterns

**Validating Webhook:**
```go
func (v *LaunchpadAppValidator) ValidateCreate(ctx context.Context, obj runtime.Object) error {
    app := obj.(*launchpadv1.LaunchpadApp)

    // Validate image is from allowed registry
    if !strings.HasPrefix(app.Spec.Image, "gcr.io/") &&
       !strings.HasPrefix(app.Spec.Image, "docker.io/") {
        return fmt.Errorf("image must be from allowed registry")
    }

    // Validate replicas within limits
    if app.Spec.Replicas > 10 {
        return fmt.Errorf("replicas cannot exceed 10")
    }

    // Validate resource requests
    if app.Spec.Resources.Requests.Memory().Value() > 4*1024*1024*1024 {
        return fmt.Errorf("memory request cannot exceed 4Gi")
    }

    return nil
}
```

**Mutating Webhook (Inject Sidecar):**
```go
func (m *LaunchpadAppMutator) Default(ctx context.Context, obj runtime.Object) error {
    app := obj.(*launchpadv1.LaunchpadApp)

    // Inject default labels
    if app.Labels == nil {
        app.Labels = make(map[string]string)
    }
    app.Labels["launchpad.io/managed"] = "true"

    // Set default replicas
    if app.Spec.Replicas == 0 {
        app.Spec.Replicas = 1
    }

    // Inject logging sidecar
    app.Spec.Sidecars = append(app.Spec.Sidecars, Sidecar{
        Name:  "log-forwarder",
        Image: "fluent/fluent-bit:latest",
    })

    return nil
}
```

**Finalizer for External Cleanup:**
```go
func (r *LaunchpadAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var app launchpadv1.LaunchpadApp
    if err := r.Get(ctx, req.NamespacedName, &app); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Handle deletion
    if !app.DeletionTimestamp.IsZero() {
        if containsString(app.Finalizers, finalizerName) {
            // Cleanup external resources (DNS, load balancer, etc.)
            if err := r.cleanupExternalResources(ctx, &app); err != nil {
                return ctrl.Result{}, err
            }

            // Notify API server
            if err := r.notifyAPIServer(ctx, &app, "deleted"); err != nil {
                log.Error(err, "failed to notify API server")
            }

            // Remove finalizer
            app.Finalizers = removeString(app.Finalizers, finalizerName)
            if err := r.Update(ctx, &app); err != nil {
                return ctrl.Result{}, err
            }
        }
        return ctrl.Result{}, nil
    }

    // Add finalizer if not present
    if !containsString(app.Finalizers, finalizerName) {
        app.Finalizers = append(app.Finalizers, finalizerName)
        if err := r.Update(ctx, &app); err != nil {
            return ctrl.Result{}, err
        }
    }

    // Normal reconciliation...
}
```

**Reading:**
- "Kubernetes Operators" book
- Admission webhook documentation
- cert-manager source code

---

### Phase 6: CLI & Production Polish (Month 12)

**Build:** CLI tool and production-ready deployment

**Features:**
- CLI for all API operations (launchpad)
- `launchpad deploy` - deploy from current directory
- `launchpad logs` - stream logs
- `launchpad status` - show deployment status
- GraphQL API alternative
- Helm chart for deployment
- Observability (Prometheus, Grafana, Jaeger)

**Skills Learned:**
- CLI development (cobra)
- GraphQL with gqlgen
- Helm chart creation
- Prometheus metrics
- Distributed tracing
- Production deployment patterns

**CLI Commands:**
```bash
# Authentication
launchpad login
launchpad logout

# Projects
launchpad project create myproject
launchpad project list
launchpad project switch myproject

# Apps
launchpad create myapp --image nginx:latest --port 80
launchpad deploy                    # Deploy from current directory
launchpad deploy --image v2.0.0     # Deploy specific image
launchpad status myapp
launchpad logs myapp -f             # Stream logs
launchpad rollback myapp            # Rollback to previous version

# Environment
launchpad env set DATABASE_URL=postgres://...
launchpad env list
launchpad env unset DATABASE_URL

# Scaling
launchpad scale myapp --replicas 5
```

**CLI Implementation:**
```go
var deployCmd = &cobra.Command{
    Use:   "deploy",
    Short: "Deploy an application",
    RunE: func(cmd *cobra.Command, args []string) error {
        client := api.NewClient(getToken())

        // Read launchpad.yaml from current directory
        config, err := readConfig("launchpad.yaml")
        if err != nil {
            return err
        }

        // Create deployment
        deployment, err := client.CreateDeployment(cmd.Context(), config.AppID, &api.DeploymentInput{
            Image: image,
        })
        if err != nil {
            return err
        }

        fmt.Printf("Deployment %s created\n", deployment.ID)

        // Stream status updates
        if follow {
            return streamDeploymentStatus(cmd.Context(), client, deployment.ID)
        }

        return nil
    },
}

func streamDeploymentStatus(ctx context.Context, client *api.Client, deploymentID string) error {
    events, err := client.StreamDeployment(ctx, deploymentID)
    if err != nil {
        return err
    }

    spinner := NewSpinner()

    for event := range events {
        switch event.Type {
        case "status_change":
            spinner.Update(event.Status)
            if event.Status == "running" {
                spinner.Success("Deployment complete!")
                return nil
            } else if event.Status == "failed" {
                spinner.Fail("Deployment failed")
                return fmt.Errorf("deployment failed: %s", event.Error)
            }
        case "log":
            fmt.Println(event.Log)
        }
    }

    return nil
}
```

**Observability Setup:**
```go
// Prometheus metrics
var (
    deploymentsTotal = promauto.NewCounterVec(prometheus.CounterOpts{
        Name: "launchpad_deployments_total",
        Help: "Total number of deployments",
    }, []string{"status"})

    deploymentDuration = promauto.NewHistogramVec(prometheus.HistogramOpts{
        Name:    "launchpad_deployment_duration_seconds",
        Help:    "Deployment duration in seconds",
        Buckets: []float64{10, 30, 60, 120, 300, 600},
    }, []string{"app"})

    activeApps = promauto.NewGauge(prometheus.GaugeOpts{
        Name: "launchpad_active_apps",
        Help: "Number of active applications",
    })
)

// Trace deployment
func (s *DeploymentService) Deploy(ctx context.Context, input DeployInput) (*Deployment, error) {
    ctx, span := tracer.Start(ctx, "deploy")
    defer span.End()

    span.SetAttributes(
        attribute.String("app.id", input.AppID),
        attribute.String("image", input.Image),
    )

    start := time.Now()
    defer func() {
        deploymentDuration.WithLabelValues(input.AppID).Observe(time.Since(start).Seconds())
    }()

    // ... deployment logic
}
```

**Reading:**
- "Powerful Command-Line Applications in Go"
- "Cloud Native Go" chapters on observability
- Prometheus client_golang documentation
- OpenTelemetry Go documentation

---

## Project Progression

Projects are ordered by complexity. Each builds on concepts from the previous.

### Level 1: CLI Foundations

#### Project 1.1: `gofetch`
**A system info display tool (like neofetch)**

Build a CLI that displays:
- OS and kernel version
- CPU info
- Memory usage
- Disk usage
- Uptime

**Concepts learned:**
- Basic Go syntax
- Standard library (`os`, `runtime`, `syscall`)
- String formatting
- Building and distributing binaries

**Extensions:**
- Add color output with `fatih/color`
- ASCII art logo
- Plugin system for custom info

---

#### Project 1.2: `godu`
**Disk usage analyzer (like `du` but better)**

Features:
- Scan directories for space usage
- Show top N largest files/directories
- Progress indicator for large scans
- Ignore patterns (like .gitignore)

**Concepts learned:**
- File system operations
- Recursive algorithms
- CLI flags with `flag` package
- Error handling patterns

**Extensions:**
- Interactive mode with `bubbletea`
- Export to JSON
- Parallel scanning for faster results

---

#### Project 1.3: `gojson`
**JSON Swiss Army knife**

Features:
- Pretty print JSON
- Minify JSON
- Query with path expressions (like jq)
- Validate JSON
- Convert JSON ↔ YAML

**Concepts learned:**
- `encoding/json` deeply
- Interfaces (`io.Reader`, `io.Writer`)
- Streaming vs buffered processing
- Building composable CLI tools

**Extensions:**
- JQ-like query language
- Color syntax highlighting
- Diff two JSON files

---

### Level 2: Concurrency

#### Project 2.1: `gowatch`
**File watcher with command execution**

Features:
- Watch files/directories for changes
- Run commands when changes detected
- Debounce rapid changes
- Configurable via file or flags

**Concepts learned:**
- fsnotify for file watching
- Goroutines for async operations
- Channels for communication
- Context for cancellation

**Extensions:**
- Process management (restart on crash)
- WebSocket for browser refresh
- Regex pattern matching

---

#### Project 2.2: `gocrawl`
**Concurrent web crawler**

Features:
- Crawl a website following links
- Respect robots.txt
- Rate limiting per domain
- Configurable depth and concurrency

**Concepts learned:**
- Worker pools
- Semaphores for limiting concurrency
- sync.Map for concurrent state
- Context cancellation

**Extensions:**
- Store results in SQLite
- Extract specific content (title, meta)
- Generate sitemap

---

#### Project 2.3: `goqueue`
**In-memory job queue**

Features:
- Submit jobs to queue
- Worker pool processes jobs
- Priority queues
- Job status tracking
- Graceful shutdown

**Concepts learned:**
- Channel patterns (fan-out, fan-in)
- sync.WaitGroup
- Graceful shutdown patterns
- Heap for priority queue

**Extensions:**
- Persistence with BoltDB
- Retry with exponential backoff
- Dead letter queue
- REST API for job submission

---

### Level 3: Networking

#### Project 3.1: `goproxy`
**HTTP reverse proxy**

Features:
- Forward requests to backend
- Load balancing (round-robin)
- Health checks
- Request/response logging

**Concepts learned:**
- net/http deeply
- Reverse proxy patterns
- Middleware pattern
- HTTP headers and body handling

**Extensions:**
- Weighted load balancing
- Circuit breaker
- Rate limiting
- TLS termination

---

#### Project 3.2: `gocache`
**Redis-compatible cache server**

Features:
- TCP server with RESP protocol
- GET, SET, DEL, EXPIRE commands
- TTL-based expiration
- Memory limits with LRU eviction

**Concepts learned:**
- TCP server patterns
- Protocol parsing
- Concurrent map access
- Time-based goroutines (for expiration)

**Extensions:**
- Persistence (RDB/AOF)
- Pub/Sub
- Clustering (consistent hashing)
- More Redis commands

---

#### Project 3.3: `goapi`
**Production-ready REST API**

Build a complete API (pick your domain: todos, bookmarks, notes):

Features:
- CRUD operations
- Authentication (JWT)
- Input validation
- Database (PostgreSQL)
- Structured logging
- Metrics endpoint
- Graceful shutdown

**Concepts learned:**
- HTTP handlers and routing
- Middleware (auth, logging, recovery)
- Database patterns (repository)
- Configuration management
- Testing (unit, integration)

**Extensions:**
- OpenAPI documentation
- Rate limiting
- Caching layer
- WebSocket for real-time

---

### Level 4: Distributed Systems

#### Project 4.1: `gokv`
**Distributed key-value store**

Features:
- Multi-node cluster
- Consistent hashing for key distribution
- Replication for fault tolerance
- Gossip protocol for membership

**Concepts learned:**
- Distributed systems fundamentals
- Consistent hashing
- Replication strategies
- Network partition handling

**Resources:**
- Read about Dynamo, Cassandra
- Study etcd's design

---

#### Project 4.2: `goraft`
**Raft consensus implementation**

Implement the Raft protocol:
- Leader election
- Log replication
- Safety guarantees
- Cluster membership changes

**Concepts learned:**
- Consensus algorithms
- State machines
- RPC patterns
- Persistence and recovery

**Resources:**
- The Raft paper (raft.github.io)
- etcd's Raft implementation
- Hashicorp's Raft library

---

#### Project 4.3: `gomesh`
**Service mesh sidecar proxy**

Features:
- Intercept service traffic
- Load balancing
- Retry with backoff
- Circuit breaking
- Observability (metrics, tracing)

**Concepts learned:**
- Sidecar pattern
- Resilience patterns
- Observability
- gRPC proxying

**Resources:**
- Study Envoy, Linkerd
- Read about service mesh patterns

---

### Level 5: Infrastructure Tools

#### Project 5.1: `goterraform`
**Declarative infrastructure tool for Docker**

Features:
- YAML/HCL configuration for desired state
- Plan → Apply workflow
- State management
- Diff visualization

**Concepts learned:**
- Declarative vs imperative
- State reconciliation
- Graph-based execution
- Docker API

---

#### Project 5.2: `gok8s`
**Mini Kubernetes**

Build a simplified container orchestrator:
- Schedule containers across nodes
- Service discovery
- Health checks and restarts
- Basic networking

**Concepts learned:**
- Container orchestration concepts
- Scheduling algorithms
- etcd for state
- API server patterns

---

#### Project 5.3: `goci`
**CI/CD pipeline runner**

Features:
- YAML pipeline definition
- Step execution with Docker
- Parallel and sequential stages
- Artifact handling
- Webhook triggers

**Concepts learned:**
- Pipeline patterns
- Docker-in-Docker or rootless
- Webhook servers
- Concurrent execution

---

## Open Source Study

### Projects to Read (In Order of Complexity)

#### Beginner
| Project | Why Study It |
|---------|--------------|
| **cobra** | CLI patterns, widely used |
| **viper** | Configuration management |
| **logrus/zap** | Structured logging patterns |
| **testify** | Testing patterns |

#### Intermediate - Web Development
| Project | Why Study It |
|---------|--------------|
| **chi** | HTTP router, middleware patterns |
| **gin** | Full web framework design |
| **gqlgen** | Code generation, GraphQL patterns |
| **gorilla/websocket** | WebSocket implementation |
| **sqlx** | Database patterns |

#### Intermediate - Kubernetes
| Project | Why Study It |
|---------|--------------|
| **controller-runtime** | Operator framework internals |
| **kubebuilder** | Scaffolding and code generation |
| **client-go** | Raw K8s API patterns |
| **kustomize** | Config transformation |

#### Advanced
| Project | Why Study It |
|---------|--------------|
| **etcd** | Raft, distributed KV |
| **prometheus** | Metrics, time series |
| **traefik** | Reverse proxy, dynamic config |
| **containerd** | Container runtime |
| **cert-manager** | Production K8s operator |
| **external-dns** | External resource management |

#### Expert
| Project | Why Study It |
|---------|--------------|
| **kubernetes** | Everything (start with small components) |
| **ArgoCD** | GitOps, complex operator |
| **istio** | Service mesh |
| **cockroachdb** | Distributed SQL |
| **vitess** | MySQL scaling |
| **dgraph** | Graph database |

### How to Study Open Source

1. **Start with main.go** - Trace the entry point
2. **Find the core abstraction** - What interfaces drive the design?
3. **Study tests** - They show intended usage
4. **Read issues** - Understand design decisions
5. **Make a small contribution** - Documentation or tests first

---

## Common Pitfalls

### Concurrency Mistakes

**1. Goroutine leaks**
```go
// Bad: Goroutine never exits
go func() {
    for {
        doWork()
    }
}()

// Good: Respect context
go func() {
    for {
        select {
        case <-ctx.Done():
            return
        default:
            doWork()
        }
    }
}()
```

**2. Race conditions**
```go
// Bad: Race on shared variable
for _, item := range items {
    go func() {
        process(item)  // item changes!
    }()
}

// Good: Capture variable
for _, item := range items {
    go func(i Item) {
        process(i)
    }(item)
}
```

**3. Deadlocks**
```go
// Bad: Blocking on unbuffered channel with no receiver
ch := make(chan int)
ch <- 1  // Blocks forever

// Good: Buffered or guaranteed receiver
ch := make(chan int, 1)
ch <- 1
```

### Error Handling

**1. Ignoring errors**
```go
// Bad
result, _ := doSomething()

// Good
result, err := doSomething()
if err != nil {
    return fmt.Errorf("doing something: %w", err)
}
```

**2. Not wrapping errors**
```go
// Bad: Lost context
if err != nil {
    return err
}

// Good: Add context
if err != nil {
    return fmt.Errorf("opening database connection: %w", err)
}
```

### Interface Mistakes

**1. Over-interfacing**
```go
// Bad: Interface for one implementation
type UserRepository interface {
    GetUser(id int) (*User, error)
    SaveUser(u *User) error
}

// If there's only one implementation, just use the concrete type
// Interfaces are for polymorphism, not abstraction

// Good: Interface when you have multiple implementations
// or need to mock for testing
```

**2. Large interfaces**
```go
// Bad: Kitchen sink interface
type Storage interface {
    Read(key string) ([]byte, error)
    Write(key string, value []byte) error
    Delete(key string) error
    List(prefix string) ([]string, error)
    Watch(key string) <-chan Event
    Transaction(func(tx Tx) error) error
}

// Good: Small, focused interfaces
type Reader interface {
    Read(key string) ([]byte, error)
}

type Writer interface {
    Write(key string, value []byte) error
}
```

### Performance

**1. Unnecessary allocations in loops**
```go
// Bad: Allocates every iteration
for _, item := range items {
    data, _ := json.Marshal(item)
    // use data
}

// Good: Reuse encoder
var buf bytes.Buffer
enc := json.NewEncoder(&buf)
for _, item := range items {
    buf.Reset()
    enc.Encode(item)
    // use buf.Bytes()
}
```

**2. String concatenation in loops**
```go
// Bad: Creates new string each time
var result string
for _, s := range strings {
    result += s
}

// Good: Use strings.Builder
var b strings.Builder
for _, s := range strings {
    b.WriteString(s)
}
result := b.String()
```

---

## Daily Habits

### The 2-Hour Daily Practice

| Time | Activity |
|------|----------|
| 30 min | Read Go code (stdlib or open source) |
| 60 min | Write code (project or exercises) |
| 15 min | Read Go blog posts or watch talks |
| 15 min | Review Go community (Reddit, Discord, Twitter) |

### Weekly Goals

- **Monday-Friday:** Work on current project
- **Saturday:** Code review session (read others' code)
- **Sunday:** Plan next week, review learnings

### Reading Code Practice

Each week, deep-read one package:

**Week 1-4:** Standard library
- `strings`, `bytes`, `strconv`
- `fmt`, `log`
- `encoding/json`, `encoding/xml`
- `net/http` (client and server)

**Week 5-8:** Popular libraries
- `chi` (router)
- `zap` (logging)
- `cobra` (CLI)
- `testify` (testing)

**Week 9+:** Infrastructure projects
- Pick a component of Docker, K8s, Prometheus
- Trace a request through the system
- Understand the key abstractions

---

## 12-Month Schedule

### Core Path (Months 1-6) - Foundations

| Month | Focus | Books | Projects |
|-------|-------|-------|----------|
| 1 | Go fundamentals | GOPL Ch 1-6 | gofetch, godu |
| 2 | Interfaces & methods | GOPL Ch 7, Effective Go | gojson |
| 3 | Concurrency basics | GOPL Ch 8-9 | gowatch |
| 4 | Concurrency patterns | Concurrency in Go | gocrawl, goqueue |
| 5 | Best practices | 100 Go Mistakes (1-50) | Refactor previous projects |
| 6 | Best practices cont. | 100 Go Mistakes (51-100) | goproxy |

### Launchpad Project (Months 7-12) - Combined Web + K8s

| Month | Focus | Books | Launchpad Phase |
|-------|-------|-------|-----------------|
| 7 | Web fundamentals | Let's Go | **Phase 1:** Foundation API (auth, teams, projects) |
| 8 | REST APIs | Let's Go Further | **Phase 2:** App Deployment API (apps, deployments, env) |
| 9 | K8s controllers | kubebuilder book, Programming K8s Ch 1-6 | **Phase 3:** First Kubernetes Controller (CRD, reconciliation) |
| 10 | K8s + Web integration | Programming K8s Ch 7-10, client-go examples | **Phase 4:** Connect API to Operator (WebSocket, log streaming) |
| 11 | Advanced operators | Kubernetes Operators book | **Phase 5:** Advanced Features (webhooks, finalizers, HPA) |
| 12 | Production | Cloud Native Go, CLI book | **Phase 6:** CLI & Production (cobra, observability, Helm) |

### Skills Progression

| Month | Web Skills | K8s Skills |
|-------|------------|------------|
| 7 | HTTP handlers, middleware, JWT, PostgreSQL | - |
| 8 | Domain modeling, validation, OpenAPI | - |
| 9 | - | CRD design, reconciliation, owner refs, envtest |
| 10 | WebSocket, real-time events | Informers, watches, pod logs API |
| 11 | - | Admission webhooks, finalizers, multi-tenant |
| 12 | CLI (cobra), GraphQL | Helm charts, Prometheus metrics, tracing |

---

## The Path to Cracked

### Beginner (Months 1-3)
You can:
- Write correct Go code
- Use goroutines and channels
- Handle errors properly
- Write tests
- Build CLI tools

### Intermediate (Months 4-6)
You can:
- Design clean interfaces
- Build concurrent systems
- Profile and optimize
- Write production services
- Read standard library code

### Advanced (Months 7-9)
After Launchpad Phases 1-3, you can:
- Build production REST APIs with auth
- Design complex domain models
- Write Kubernetes controllers
- Understand reconciliation patterns
- Test with envtest

### Cracked (Months 10-12+)
After completing Launchpad, you can:
- Architect API + operator systems
- Build production-grade operators
- Implement real-time features
- Add admission webhooks
- Ship observable, production-ready systems
- Build CLIs that developers love
- Contribute to the K8s ecosystem

---

## Resources Quick Reference

### Bookmarks

```
# Official
go.dev/doc                    # Official docs
go.dev/blog                   # Go blog
go.dev/play                   # Playground

# Learning
gobyexample.com              # Examples
quii.gitbook.io/learn-go-with-tests  # TDD approach
yourbasic.org/golang         # Tutorials

# Reference
pkg.go.dev                   # Package docs
github.com/golang/go/wiki    # Community wiki
gopl.io                      # Book exercises

# Web Development
alexedwards.net/blog         # Alex Edwards' blog (author of Let's Go)
grafana.com/blog/go          # Go patterns at scale
pace.dev/blog                # Mat Ryer's blog

# Kubernetes Development
book.kubebuilder.io          # Kubebuilder book
kubernetes.io/docs/concepts  # K8s concepts
github.com/kubernetes/client-go/examples  # client-go examples
github.com/kubernetes-sigs/controller-runtime  # controller-runtime

# Community
reddit.com/r/golang          # Reddit
gophers.slack.com            # Slack
twitter.com/golang           # Official Twitter
kubernetes.slack.com         # K8s Slack (#sig-api-machinery, #kubebuilder)
```

### Key People to Follow

**Go Core:**
- **Rob Pike** - Go creator, philosophy
- **Russ Cox** - Go team lead
- **Dave Cheney** - Performance, practices
- **Bill Kennedy** - Training, deep dives

**Web Development:**
- **Mat Ryer** - Web patterns, podcasts
- **Alex Edwards** - Author of Let's Go books
- **Francesc Campoy** - Tutorials, talks
- **Peter Bourgon** - Go kit, microservices

**Kubernetes:**
- **Tim Hockin** - K8s core contributor
- **Stefan Schimanski** - Programming Kubernetes author
- **Michael Hausenblas** - Programming Kubernetes author
- **Ahmet Alp Balkan** - K8s tooling (kubectx, etc.)

### Podcasts

- **Go Time** - Weekly Go podcast
- **Cup o' Go** - News and discussions
- **Ardan Labs Podcast** - Technical deep dives
- **Kubernetes Podcast** - K8s news and interviews
- **The Changelog** - General dev, often Go content

---

## Final Words

Go is a language that rewards depth over breadth. The syntax is simple, but mastery comes from:

1. **Understanding concurrency deeply** - Not just how, but when and why
2. **Reading a lot of code** - The stdlib is your textbook
3. **Building real systems** - That handle failure, scale, and ship
4. **Embracing simplicity** - The best Go code looks almost boring

### The Launchpad Advantage

By building one comprehensive project that spans both web development and Kubernetes, you'll:

- **See how pieces connect** - APIs create CRDs, operators reconcile, WebSockets stream status
- **Build production patterns** - Auth, validation, webhooks, observability
- **Have a portfolio piece** - A complete PaaS you can demo and extend
- **Learn both ecosystems** - Web and K8s skills that work together

Most tutorials teach web OR Kubernetes. Building Launchpad teaches you how real platforms work - where the API server talks to the cluster, where status flows back to users, and where operators do the heavy lifting.

### What Comes After

Once you've completed Launchpad, you can:
- **Extend it** - Add build pipelines, custom domains, databases-as-a-service
- **Contribute** - Apply these patterns to open source operators
- **Build at work** - These skills transfer directly to internal platforms
- **Go deeper** - Study ArgoCD, Crossplane, or Cluster API for advanced patterns

The infrastructure that runs the modern internet is largely written in Go. Kubernetes, Docker, Terraform, Prometheus - the people who built these systems understand APIs, controllers, and production operations deeply.

Your goal is to join that group.

Start today. Build something. Read code. Ship it.

---

*Generated: January 2026*
