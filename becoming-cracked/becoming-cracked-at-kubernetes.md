# Becoming Cracked at Kubernetes

A comprehensive guide to mastering Kubernetes — from deploying workloads to building operators to understanding the internals of the system that orchestrates the modern internet.

---

## Table of Contents

1. [Why Kubernetes](#why-kubernetes)
2. [Core Mental Models](#core-mental-models)
3. [Books: The Foundation](#books-the-foundation)
4. [Structured Reading Path](#structured-reading-path)
5. [Video Resources](#video-resources)
6. [Tools: Your Arsenal](#tools-your-arsenal)
7. [Development Setup](#development-setup)
8. [The Kubernetes Internals Deep Dive](#the-kubernetes-internals-deep-dive)
9. [The CloudForge Project](#the-cloudforge-project)
   - [Phase 1: Cluster Foundation & GitOps](#phase-1-cluster-foundation--gitops-month-7)
   - [Phase 2: Multi-Tenant Platform](#phase-2-multi-tenant-platform-month-8)
   - [Phase 3: Custom Operator](#phase-3-custom-operator-month-9)
   - [Phase 4: Observability Stack](#phase-4-observability-stack-month-10)
   - [Phase 5: Service Mesh & Security](#phase-5-service-mesh--security-month-11)
   - [Phase 6: Production Hardening & Chaos](#phase-6-production-hardening--chaos-month-12)
10. [Project Progression](#project-progression)
11. [Open Source Study](#open-source-study)
12. [Common Pitfalls](#common-pitfalls)
13. [Daily Habits](#daily-habits)
14. [12-Month Schedule](#12-month-schedule)
15. [The Path to Cracked](#the-path-to-cracked)

---

## Why Kubernetes

Kubernetes won. Full stop. It is the operating system of the cloud.

- **Declarative infrastructure** — You describe what you want, not how to get there
- **Self-healing** — Failed containers restart, unhealthy nodes drain, desired state converges automatically
- **Portable** — Runs on AWS, GCP, Azure, bare metal, your laptop
- **Extensible** — CRDs and operators let you teach Kubernetes about any resource
- **Ecosystem** — Helm, ArgoCD, Istio, Prometheus, Crossplane — the CNCF landscape is enormous
- **Industry standard** — Every major company uses it; it's table stakes for infrastructure roles

Kubernetes orchestrates: Docker containers, stateless web apps, stateful databases, ML training jobs, batch processing, edge computing, and increasingly the entire lifecycle of cloud-native applications.

**The honest truth:** Kubernetes is complex. The learning curve is steep. You'll fight YAML, scratch your head at networking, and wonder why your pod won't start. But once the mental model clicks — desired state, reconciliation loops, the API server as the single source of truth — you gain the ability to operate, debug, and build systems at a level most engineers never reach.

---

## Core Mental Models

### 1. Desired State vs. Actual State

This is THE fundamental concept. Everything in Kubernetes is a reconciliation loop.

```yaml
# You declare desired state:
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3  # "I want 3 pods"

# Kubernetes makes it so.
# If a pod dies, the controller creates a new one.
# If you change to replicas: 5, the controller adds 2 more.
# You never say "start a pod" — you say "I want N pods."
```

This is declarative. You are not writing scripts to start/stop processes. You are stating what the world should look like, and Kubernetes converges reality to match.

### 2. Everything is an API Object

Every resource in Kubernetes — Pods, Services, Deployments, ConfigMaps, your custom CRDs — is an object stored in etcd, accessible through the API server.

```
apiVersion: <group>/<version>   # Which API group and version
kind: <type>                    # What type of resource
metadata:                       # Identity (name, namespace, labels, annotations)
  name: my-thing
  namespace: default
spec:                           # Desired state (what you want)
status:                         # Actual state (what Kubernetes reports back)
```

Every object follows this pattern. `spec` is your input, `status` is Kubernetes' output.

### 3. Labels and Selectors are the Glue

Kubernetes components find each other through labels, not hardcoded names.

```yaml
# A Deployment creates Pods with these labels:
spec:
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app

# A Service finds Pods through the same labels:
spec:
  selector:
    app: my-app
  ports:
    - port: 80
```

Services don't know about Deployments. They know about labels. This loose coupling is what makes the system composable.

### 4. Controllers are the Brains

A controller is a loop: watch desired state, observe actual state, take action to reconcile.

```
┌─────────────────────────────────────────┐
│           Controller Loop               │
│                                         │
│  1. Watch: What does the user want?     │
│  2. Observe: What exists right now?     │
│  3. Diff: What's different?             │
│  4. Act: Create/Update/Delete to match  │
│  5. Repeat forever                      │
└─────────────────────────────────────────┘
```

The Deployment controller watches Deployments and creates ReplicaSets. The ReplicaSet controller watches ReplicaSets and creates Pods. The scheduler watches unscheduled Pods and assigns them to nodes. The kubelet watches Pods assigned to its node and runs containers.

Every component is a controller. Once you internalize this, Kubernetes makes sense.

### 5. Namespaces are Soft Boundaries

Namespaces partition resources within a cluster. They are NOT security boundaries by themselves.

```bash
kubectl get pods -n production    # Only see production pods
kubectl get pods -n staging       # Only see staging pods
kubectl get pods --all-namespaces # See everything
```

Use namespaces for: organizing teams/environments, applying ResourceQuotas, scoping RBAC policies. Don't rely on them alone for true isolation — that requires NetworkPolicies, RBAC, and potentially separate clusters.

### 6. The Network is Flat (By Default)

Every Pod gets its own IP. Every Pod can reach every other Pod by default. There's no NAT between Pods.

```
Pod A (10.244.1.5) ──── can talk to ────→ Pod B (10.244.2.8)
                                          Pod C (10.244.3.12)
                                          Any other Pod
```

Services provide stable endpoints (ClusterIP, NodePort, LoadBalancer) in front of ephemeral Pods. NetworkPolicies restrict traffic when you need isolation.

### 7. Storage is a First-Class Citizen

Kubernetes abstracts storage through PersistentVolumes (PV) and PersistentVolumeClaims (PVC).

```yaml
# "I need 10Gi of fast storage"
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-data
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 10Gi
```

The CSI (Container Storage Interface) lets any storage provider plug into Kubernetes — AWS EBS, GCP PD, Ceph, local NVMe.

---

## Books: The Foundation

### Essential (Read in Order)

| Order | Book | Focus | Why |
|-------|------|-------|-----|
| 1 | **"Kubernetes in Action, 2nd Ed"** by Marko Lukša | Complete K8s coverage | THE Kubernetes book. Covers everything from Pods to internals with depth and clarity. |
| 2 | **"Kubernetes Up & Running, 3rd Ed"** by Burns, Beda, Hightower, Tracey | Practical operations | Written by K8s co-founders. Concise, opinionated, production-focused. |
| 3 | **"Production Kubernetes"** by Rosso, Lander, Brand, Harris | Real-world patterns | How to actually run K8s in production. Networking, storage, security, multi-tenancy. |

### Operators & Extensions

| Book | Focus | When to Read |
|------|-------|--------------|
| **"Programming Kubernetes"** by Hausenblas & Schimanski | Controllers, operators, CRDs | When building operators |
| **"Kubernetes Operators"** by Dobies & Wood | Operator pattern deep dive | When building operators |
| **"Kubernetes Patterns, 2nd Ed"** by Ibryam & Huß | Design patterns | After basics, for architecture |

### Networking & Security

| Book | Focus | When to Read |
|------|-------|--------------|
| **"Networking and Kubernetes"** by Halpern & Woods | CNI, Services, Ingress deep dive | When debugging networking issues |
| **"Kubernetes Security and Observability"** by Rao & Dua | Security, Falco, eBPF | When hardening clusters |
| **"Hacking Kubernetes"** by Martin & Hausenblas | Threat modeling, attack vectors | When securing production |

### Platform Engineering & GitOps

| Book | Focus | When to Read |
|------|-------|--------------|
| **"GitOps and Kubernetes"** by Yuen, Matyushentsev, Ekenstam, Shortridge | ArgoCD, Flux patterns | When implementing GitOps |
| **"Platform Engineering on Kubernetes"** by Salatino | Building internal platforms | When building developer platforms |
| **"The Kubernetes Book"** by Nigel Poulton | Quick, accessible reference | Good refresher or intro |

### Supporting Books (Not K8s-specific but essential)

| Book | Focus |
|------|-------|
| **"Designing Data-Intensive Applications"** by Kleppmann | Distributed systems bible |
| **"Site Reliability Engineering"** by Beyer, Jones, Petoff, Murphy | SRE practices, monitoring, incident response |
| **"Designing Distributed Systems"** by Brendan Burns | Patterns for containers and microservices |
| **"The Linux Programming Interface"** by Kerrisk | Understanding containers at the OS level |
| **"Container Security"** by Liz Rice | Namespaces, cgroups, seccomp, capabilities |

---

## Structured Reading Path

### Phase 1: Kubernetes Fundamentals (Weeks 1-6)

**Primary: "Kubernetes in Action, 2nd Ed"**

| Week | Chapters | Focus | Hands-On |
|------|----------|-------|----------|
| 1 | Ch 1-3 | Intro, Pods, containers | Deploy first app to kind cluster |
| 2 | Ch 4-6 | ReplicaSets, Deployments, Services | Deploy multi-tier app, expose services |
| 3 | Ch 7-9 | ConfigMaps, Secrets, storage | Configure apps, attach persistent storage |
| 4 | Ch 10-12 | StatefulSets, Jobs, DaemonSets | Deploy stateful workload (Postgres/Redis) |
| 5 | Ch 13-15 | Scheduling, resource management, autoscaling | Set resource limits, configure HPA |
| 6 | Ch 16-18 | RBAC, NetworkPolicies, internals | Lock down a namespace, trace API request |

**Supplement with:**
- Kubernetes official docs tutorials (kubernetes.io/docs/tutorials)
- `kubectl explain` for every resource you encounter
- kubectl cheat sheet (kubernetes.io/docs/reference/kubectl/cheatsheet)

### Phase 2: Production Operations (Weeks 7-10)

**Primary: "Kubernetes Up & Running, 3rd Ed"**

| Week | Chapters | Focus |
|------|----------|-------|
| 7 | Ch 1-5 | Pods, labels, services, HTTP load balancing |
| 8 | Ch 6-10 | Deployments, DaemonSets, Jobs, ConfigMaps |
| 9 | Ch 11-14 | Service meshes, storage, Operators |
| 10 | Ch 15-18 | RBAC, admission control, policy, multi-cluster |

**Projects during this phase:**
- Deploy a production-style app (frontend + backend + database)
- Set up Ingress with TLS (cert-manager)
- Implement blue/green and canary deployments

### Phase 3: Production Patterns (Weeks 11-14)

**Primary: "Production Kubernetes"**

Read one chapter per day. For each:
1. Understand the problem it solves
2. Implement it in your test cluster
3. Break it intentionally and observe failure

**Key sections:**
- Networking deep dive (CNI, DNS, Service meshes)
- Storage and stateful workloads
- Security and multi-tenancy
- Observability (metrics, logs, traces)
- Cluster operations and upgrades

### Phase 4: Operators & Extensions (Weeks 15-20)

**Primary: "Programming Kubernetes"**

| Week | Chapters | Focus |
|------|----------|-------|
| 15 | Ch 1-3 | API server, API machinery |
| 16 | Ch 4-5 | client-go, informers, work queues |
| 17 | Ch 6-7 | Custom resources, operator patterns |
| 18 | Ch 8-9 | Admission webhooks, custom API servers |

**Supplement with:**
- kubebuilder book (book.kubebuilder.io)
- operator-sdk tutorials
- "Kubernetes Patterns" for design inspiration

### Phase 5: Networking & Security Deep Dive (Weeks 21-24)

**Primary: "Networking and Kubernetes" + "Hacking Kubernetes"**

- CNI plugins (how Pod networking actually works)
- Service mesh internals (Envoy, sidecar injection)
- NetworkPolicy design
- Pod Security Standards
- RBAC design patterns
- Supply chain security (signing, scanning, admission)

---

## Video Resources

### YouTube Channels

| Channel | Content |
|---------|---------|
| **KubeCon / CloudNativeCon** | Conference talks, the single best resource |
| **CNCF** | Technical deep dives, end-user stories |
| **Rawkode Academy** | Hands-on K8s tutorials |
| **That DevOps Guy (Marcel Dempers)** | Practical infrastructure |
| **Nana Janashia (TechWorld with Nana)** | Clear explanations of complex topics |
| **Viktor Farcic (DevOps Toolkit)** | Opinionated tooling comparisons |
| **Liz Rice** | Container security, eBPF |

### Must-Watch Talks

**Fundamentals:**
- "Kubernetes Deconstructed: Understanding Kubernetes by Breaking It Down" - Carson Anderson
- "The Illustrated Children's Guide to Kubernetes" - Deis/Microsoft
- "Life of a Packet" - Michael Rubin (KubeCon)
- "How the Kubernetes Scheduler Works" - various KubeCon talks

**Internals:**
- "A Journey into Kubernetes Controller Runtime" - KubeCon
- "Deep Dive into the API Server" - various KubeCon
- "etcd Deep Dive" - various KubeCon
- "Writing a Kubernetes Operator from Scratch" - various KubeCon
- "The Life of a Kubernetes Watch Event" - Wenjia Zhang (KubeCon)

**Networking:**
- "Understanding Kubernetes Networking" - Jeff Poole
- "Deep Dive into Kubernetes Networking" - various KubeCon
- "A Deep Dive into Service Mesh and Envoy" - Matt Klein
- "Everything You Need to Know About CNI" - various KubeCon

**Security:**
- "Hacking and Hardening Kubernetes Clusters by Example" - various KubeCon
- "Kubernetes Security Best Practices" - Ian Lewis
- "Container Security: Theory and Practice" - Liz Rice
- "Attacking and Defending Kubernetes" - various KubeCon

**Production:**
- "Failure Stories from the Field" - various KubeCon
- "Scaling Kubernetes to 7,500 Nodes" - OpenAI (KubeCon)
- "How Spotify Manages 4,000+ Kubernetes Clusters" - KubeCon
- "Lessons Learned from Running Kubernetes at Scale" - various

**GitOps:**
- "Introduction to GitOps with ArgoCD" - various
- "Flux vs ArgoCD: A Practical Comparison" - various
- "GitOps at Scale" - various KubeCon

### Courses

| Course | Platform | Focus |
|--------|----------|-------|
| **CKA with Practice Tests** | Udemy (Mumshad Mannambeth / KodeKloud) | Best exam prep, excellent labs |
| **CKAD with Practice Tests** | Udemy (Mumshad Mannambeth / KodeKloud) | Developer-focused K8s |
| **Kubernetes the Hard Way** | GitHub (Kelsey Hightower) | Build a cluster from scratch — essential |
| **Kubernetes Fundamentals (LFS258)** | Linux Foundation | Official training |
| **killer.sh** | killer.sh | CKA/CKAD exam simulator |

---

## Tools: Your Arsenal

### Essential CLI Tools

| Tool | Purpose | Install |
|------|---------|---------|
| **kubectl** | The K8s CLI — you'll live here | brew install kubectl |
| **kind** | Kubernetes IN Docker, local clusters | brew install kind |
| **minikube** | Local K8s cluster alternative | brew install minikube |
| **k3d** | Lightweight K8s with k3s in Docker | brew install k3d |
| **helm** | Package manager for K8s | brew install helm |
| **kustomize** | Template-free config management | brew install kustomize |

### Productivity Tools

| Tool | Purpose | Install |
|------|---------|---------|
| **kubectx / kubens** | Switch contexts/namespaces fast | brew install kubectx |
| **k9s** | Terminal UI for K8s clusters | brew install k9s |
| **stern** | Multi-pod log tailing | brew install stern |
| **kubectl-neat** | Clean up YAML output | kubectl krew install neat |
| **kubecolor** | Colorized kubectl output | brew install kubecolor |
| **fzf** | Fuzzy finder (pairs with kubectx) | brew install fzf |
| **krew** | kubectl plugin manager | see krew.sigs.k8s.io |

### Debugging & Troubleshooting

| Tool | Purpose |
|------|---------|
| **kubectl debug** | Ephemeral debug containers (built-in) |
| **kubectl-trace** | bpftrace programs in your cluster |
| **inspektor-gadget** | eBPF-based debugging tools for K8s |
| **kubeshark** | API traffic viewer (Wireshark for K8s) |
| **netshoot** | Network troubleshooting container image |
| **kubectl-who-can** | RBAC analysis |

### GitOps & Deployment

| Tool | Purpose |
|------|---------|
| **ArgoCD** | GitOps continuous delivery |
| **Flux** | GitOps toolkit alternative |
| **Kargo** | GitOps promotion pipelines |
| **Skaffold** | Dev-to-deploy workflow |
| **Tilt** | Local dev environment for K8s |
| **Telepresence** | Local-to-remote development |

### Security

| Tool | Purpose |
|------|---------|
| **trivy** | Container image vulnerability scanning |
| **kube-bench** | CIS benchmark checker |
| **kubescape** | Security posture scanning |
| **Falco** | Runtime security monitoring |
| **OPA / Gatekeeper** | Policy enforcement |
| **Kyverno** | Policy engine (simpler than OPA) |
| **cosign** | Container image signing |

### Observability

| Tool | Purpose |
|------|---------|
| **Prometheus** | Metrics collection |
| **Grafana** | Dashboarding and visualization |
| **Loki** | Log aggregation |
| **Jaeger / Tempo** | Distributed tracing |
| **OpenTelemetry** | Unified observability framework |
| **kube-state-metrics** | K8s object metrics |
| **metrics-server** | Resource metrics for HPA/VPA |

### Operator Development

| Tool | Purpose |
|------|---------|
| **kubebuilder** | Scaffold K8s operators (Go) |
| **operator-sdk** | Build operators (Go, Ansible, Helm) |
| **controller-runtime** | Library for building controllers |
| **envtest** | Test controllers without a real cluster |
| **ko** | Build and deploy Go apps to K8s |
| **kopf** | Kubernetes operator framework (Python) |

---

## Development Setup

### Local Cluster (kind)

```bash
# Install kind
brew install kind

# Create a multi-node cluster
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    kubeadmConfigPatches:
      - |
        kind: InitConfiguration
        nodeRegistration:
          kubeletExtraArgs:
            node-labels: "ingress-ready=true"
    extraPortMappings:
      - containerPort: 80
        hostPort: 80
        protocol: TCP
      - containerPort: 443
        hostPort: 443
        protocol: TCP
  - role: worker
  - role: worker
  - role: worker
EOF

# Verify
kubectl get nodes
kubectl cluster-info
```

### Shell Setup

```bash
# Add to ~/.zshrc or ~/.bashrc

# kubectl autocomplete
source <(kubectl completion zsh)

# Alias kubectl (you'll type it thousands of times)
alias k=kubectl
complete -o default -F __start_kubectl k

# Useful aliases
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgd='kubectl get deployments'
alias kgn='kubectl get nodes'
alias kga='kubectl get all'
alias kd='kubectl describe'
alias kl='kubectl logs'
alias kx='kubectl exec -it'
alias kns='kubens'
alias kctx='kubectx'

# Watch mode
alias kw='kubectl get pods -w'

# Show current context/namespace in prompt (add to PS1)
export KUBE_PS1_SYMBOL_ENABLE=false
source "/opt/homebrew/opt/kube-ps1/share/kube-ps1.sh"
PROMPT='$(kube_ps1) '$PROMPT
```

### kubectl Muscle Memory

```bash
# The commands you'll use most:
kubectl get <resource> -o wide                # List resources with extra info
kubectl describe <resource> <name>            # Detailed info + events
kubectl logs <pod> -f --tail=100              # Stream logs
kubectl logs <pod> -c <container>             # Specific container logs
kubectl exec -it <pod> -- /bin/sh             # Shell into a pod
kubectl port-forward svc/<name> 8080:80       # Local access to a service
kubectl apply -f <file>                       # Apply configuration
kubectl delete -f <file>                      # Remove configuration
kubectl get events --sort-by=.lastTimestamp   # Recent cluster events
kubectl top pods                              # Resource usage
kubectl explain <resource>.spec               # API docs in your terminal
kubectl diff -f <file>                        # Preview changes before apply

# Debugging flow:
# 1. kubectl get pods              → Is the pod running?
# 2. kubectl describe pod <name>   → What do the events say?
# 3. kubectl logs <pod>            → What does the app say?
# 4. kubectl exec -it <pod> -- sh  → Get inside and investigate
```

### Project Structure for K8s Manifests

```
my-platform/
├── base/                      # Base configurations
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── kustomization.yaml
├── overlays/                  # Environment-specific
│   ├── dev/
│   │   ├── kustomization.yaml
│   │   └── patches/
│   ├── staging/
│   │   ├── kustomization.yaml
│   │   └── patches/
│   └── production/
│       ├── kustomization.yaml
│       └── patches/
├── charts/                    # Helm charts
│   └── my-app/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
└── operators/                 # Custom operators
    └── my-operator/
```

---

## The Kubernetes Internals Deep Dive

Understanding what happens beneath `kubectl apply` separates operators from engineers.

### The API Server: The Front Door

Every interaction goes through the API server (`kube-apiserver`). It is the only component that talks to etcd.

```
kubectl apply -f deploy.yaml
       │
       ▼
┌──────────────┐
│  API Server  │
│              │
│ 1. AuthN     │  ← Who are you? (certs, tokens, OIDC)
│ 2. AuthZ     │  ← Can you do this? (RBAC)
│ 3. Admission │  ← Should we allow this? (webhooks)
│ 4. Validate  │  ← Is this well-formed?
│ 5. Persist   │  ← Write to etcd
│ 6. Notify    │  ← Tell watchers something changed
└──────────────┘
```

**Key insight:** Admission webhooks run BEFORE the object is stored. This is where policy engines (OPA, Kyverno) intercept and modify/reject requests.

### etcd: The Source of Truth

etcd is a distributed key-value store. All cluster state lives here.

```
/registry/deployments/default/my-app    → Deployment JSON
/registry/pods/default/my-app-abc123    → Pod JSON
/registry/services/default/my-service   → Service JSON
```

**Key insight:** etcd has a watch API. Controllers watch for changes to specific keys, which is how they react in real-time.

### The Scheduler: Where Do Pods Go?

```
Unscheduled Pod (nodeName is empty)
       │
       ▼
┌──────────────────────┐
│     Scheduler        │
│                      │
│ 1. Filter            │  ← Which nodes CAN run this? (resources, taints, affinity)
│ 2. Score             │  ← Which node is BEST? (balance, locality)
│ 3. Bind              │  ← Assign pod to winner
└──────────────────────┘
```

**Key insight:** The scheduler is just another controller. You can run multiple schedulers or write your own.

### The Kubelet: The Node Agent

Every node runs a kubelet. It watches for Pods assigned to its node and ensures containers are running.

```
API Server says: "Pod X should run on this node"
       │
       ▼
┌──────────────┐
│   Kubelet    │
│              │
│ 1. Pull image│  ← Via container runtime (containerd)
│ 2. Create    │  ← Create containers via CRI
│ 3. Monitor   │  ← Health checks (liveness, readiness, startup)
│ 4. Report    │  ← Update Pod status back to API server
└──────────────┘
```

### kube-proxy: The Network Plumber

kube-proxy programs iptables (or IPVS, or eBPF) rules so that Service ClusterIPs route to healthy Pod IPs.

```
Client → Service ClusterIP (10.96.0.1:80)
                │
        iptables/IPVS rules (written by kube-proxy)
                │
       ┌────────┼────────┐
       ▼        ▼        ▼
   Pod A     Pod B     Pod C
```

**Key insight:** Cilium and other CNIs can replace kube-proxy entirely with eBPF, which is faster and more observable.

### The Full Request Flow

When you run `kubectl apply -f deployment.yaml`:

```
1. kubectl sends HTTPS request to API server
2. API server authenticates (TLS client cert)
3. API server authorizes (RBAC check)
4. Mutating admission webhooks run (inject sidecars, set defaults)
5. Object is validated
6. Validating admission webhooks run (policy checks)
7. Object is stored in etcd
8. Deployment controller sees new Deployment → creates ReplicaSet
9. ReplicaSet controller sees new ReplicaSet → creates Pods
10. Scheduler sees unscheduled Pods → assigns to nodes
11. Kubelet sees new Pods assigned → pulls images, starts containers
12. kube-proxy updates iptables for any Services
13. Endpoints controller updates Endpoint objects
14. Pod becomes Ready → starts receiving traffic
```

This takes seconds. 14 steps. Multiple controllers. All converging on desired state.

---

## The CloudForge Project

**What you're building:** A production-grade internal developer platform on Kubernetes — a simplified version of what companies like Spotify, Airbnb, and Shopify run internally.

**Why this project:** It naturally combines cluster operations, GitOps, custom operators, observability, service mesh, security, and chaos engineering. Every phase teaches skills that compound.

**Architecture Overview:**
```
┌─────────────────────────────────────────────────────────────────┐
│                         CloudForge                              │
├─────────────────────────────────────────────────────────────────┤
│  Developer Portal    │  CLI (cfctl)       │  GitOps (ArgoCD)   │
├─────────────────────────────────────────────────────────────────┤
│                    Platform Services                            │
│  - Tenant Operator   - App Operator      - Database Operator   │
│  - Certificate Mgmt  - Secret Rotation   - Backup Controller   │
├─────────────────────────────────────────────────────────────────┤
│                    Observability                                │
│  - Prometheus/Grafana - Loki/Promtail    - Jaeger/Tempo        │
├─────────────────────────────────────────────────────────────────┤
│                    Service Mesh (Istio/Linkerd)                 │
│  - mTLS             - Traffic shifting    - Circuit breaking    │
├─────────────────────────────────────────────────────────────────┤
│                    Kubernetes Cluster(s)                        │
│  Multi-zone   │   Network Policies   │   Pod Security          │
└─────────────────────────────────────────────────────────────────┘
```

---

### Phase 1: Cluster Foundation & GitOps (Month 7)

**Build:** A production-like cluster with GitOps-driven configuration management

**Features:**
- Multi-node kind cluster with proper configuration
- ArgoCD installed and managing all cluster resources
- Git repository structure for cluster configuration
- Ingress controller (ingress-nginx) with TLS
- cert-manager for automatic certificate management
- External-DNS simulation
- Sealed Secrets for secret management in Git

**Skills Learned:**
- Cluster bootstrapping and configuration
- GitOps principles and ArgoCD
- Kustomize for environment management
- Ingress and TLS configuration
- Secret management patterns

**Git Repository Structure:**
```
cloudforge-platform/
├── clusters/
│   ├── dev/
│   │   ├── kustomization.yaml
│   │   └── cluster-config.yaml
│   └── production/
│       ├── kustomization.yaml
│       └── cluster-config.yaml
├── infrastructure/
│   ├── base/
│   │   ├── ingress-nginx/
│   │   │   ├── namespace.yaml
│   │   │   ├── helmrelease.yaml
│   │   │   └── kustomization.yaml
│   │   ├── cert-manager/
│   │   │   ├── namespace.yaml
│   │   │   ├── helmrelease.yaml
│   │   │   ├── clusterissuer.yaml
│   │   │   └── kustomization.yaml
│   │   ├── argocd/
│   │   │   ├── namespace.yaml
│   │   │   ├── helmrelease.yaml
│   │   │   └── kustomization.yaml
│   │   └── sealed-secrets/
│   │       └── ...
│   └── overlays/
│       ├── dev/
│       └── production/
├── apps/
│   ├── base/
│   └── overlays/
└── operators/
    └── ...
```

**ArgoCD App of Apps:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: infrastructure
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/you/cloudforge-platform
    targetRevision: main
    path: infrastructure/overlays/dev
  destination:
    server: https://kubernetes.default.svc
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

**Reading:**
- "GitOps and Kubernetes" chapters 1-6
- ArgoCD documentation
- Kustomize documentation

---

### Phase 2: Multi-Tenant Platform (Month 8)

**Build:** A multi-tenant system where each team gets an isolated namespace with quotas and policies

**Features:**
- Tenant CRD that provisions namespaces
- ResourceQuotas and LimitRanges per tenant
- NetworkPolicies for namespace isolation
- RBAC roles per tenant (admin, developer, viewer)
- Namespace-scoped Ingress
- Default Pod Security Standards

**Skills Learned:**
- Multi-tenancy patterns
- RBAC design
- NetworkPolicy authoring
- ResourceQuota and LimitRange
- Pod Security Admission
- Kyverno/OPA policies

**Tenant CRD:**
```yaml
apiVersion: cloudforge.io/v1alpha1
kind: Tenant
metadata:
  name: team-payments
spec:
  owner: payments-team@company.com
  tier: standard   # standard, premium, enterprise
  resourceQuota:
    cpu: "20"
    memory: "40Gi"
    pods: "50"
  networkPolicy:
    allowInternetEgress: true
    allowedNamespaces:
      - team-shared-services
  members:
    - name: alice
      role: admin
    - name: bob
      role: developer
status:
  phase: Active
  namespace: tenant-team-payments
  resourceUsage:
    cpu: "8"
    memory: "16Gi"
    pods: "23"
```

**NetworkPolicy for Tenant Isolation:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: tenant-team-payments
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              cloudforge.io/tenant: team-payments
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: ingress-nginx
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              cloudforge.io/tenant: team-payments
    - to:  # Allow DNS
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
```

**Kyverno Policy (Enforce Labels):**
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-labels
spec:
  validationFailureAction: Enforce
  rules:
    - name: require-team-label
      match:
        any:
          - resources:
              kinds:
                - Deployment
                - StatefulSet
      validate:
        message: "The label 'cloudforge.io/team' is required."
        pattern:
          metadata:
            labels:
              cloudforge.io/team: "?*"
```

**Reading:**
- "Production Kubernetes" chapters on multi-tenancy
- "Hacking Kubernetes" for security context
- Kyverno documentation

---

### Phase 3: Custom Operator (Month 9)

**Build:** A full Kubernetes operator in Go that manages application deployments with advanced lifecycle management

**Features:**
- CloudForgeApp CRD with full lifecycle
- Reconciler creates Deployment, Service, Ingress, HPA
- Health checks and readiness gates
- Canary deployments (traffic splitting)
- Automatic rollback on failed health checks
- Status conditions with detailed reporting
- Finalizers for cleanup

**Skills Learned:**
- kubebuilder scaffolding
- Reconciliation patterns
- Status conditions
- Owner references and garbage collection
- Finalizer patterns
- envtest for integration testing
- Controller metrics

**CRD Design:**
```yaml
apiVersion: cloudforge.io/v1alpha1
kind: CloudForgeApp
metadata:
  name: payment-service
  namespace: tenant-team-payments
spec:
  image: registry.company.com/payments:v2.1.0
  replicas: 3
  port: 8080
  resources:
    requests:
      cpu: "100m"
      memory: "128Mi"
    limits:
      cpu: "500m"
      memory: "512Mi"
  healthCheck:
    path: /healthz
    port: 8080
    initialDelaySeconds: 10
  ingress:
    host: payments.dev.company.com
    tls: true
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilization: 70
  deployment:
    strategy: canary
    canary:
      steps:
        - setWeight: 20
        - pause: {duration: 5m}
        - setWeight: 50
        - pause: {duration: 5m}
        - setWeight: 100
status:
  phase: Running
  currentVersion: v2.1.0
  previousVersion: v2.0.0
  replicas: 3
  readyReplicas: 3
  conditions:
    - type: Available
      status: "True"
      reason: DeploymentAvailable
      message: "All replicas are ready"
    - type: Progressing
      status: "False"
      reason: DeploymentComplete
      message: "Deployment has completed"
```

**Reconciler Skeleton:**
```go
func (r *CloudForgeAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    log := log.FromContext(ctx)

    // 1. Fetch the CloudForgeApp
    var app cloudforcev1.CloudForgeApp
    if err := r.Get(ctx, req.NamespacedName, &app); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // 2. Handle deletion
    if !app.DeletionTimestamp.IsZero() {
        return r.handleDeletion(ctx, &app)
    }

    // 3. Ensure finalizer
    if err := r.ensureFinalizer(ctx, &app); err != nil {
        return ctrl.Result{}, err
    }

    // 4. Reconcile owned resources
    if err := r.reconcileDeployment(ctx, &app); err != nil {
        return ctrl.Result{RequeueAfter: 30 * time.Second}, err
    }
    if err := r.reconcileService(ctx, &app); err != nil {
        return ctrl.Result{}, err
    }
    if err := r.reconcileIngress(ctx, &app); err != nil {
        return ctrl.Result{}, err
    }
    if err := r.reconcileHPA(ctx, &app); err != nil {
        return ctrl.Result{}, err
    }

    // 5. Handle canary rollout
    if app.Spec.Deployment.Strategy == "canary" {
        result, err := r.reconcileCanary(ctx, &app)
        if err != nil {
            return result, err
        }
        if result.RequeueAfter > 0 {
            return result, nil
        }
    }

    // 6. Update status
    if err := r.updateStatus(ctx, &app); err != nil {
        return ctrl.Result{}, err
    }

    return ctrl.Result{}, nil
}
```

**Testing with envtest:**
```go
var _ = Describe("CloudForgeApp Controller", func() {
    ctx := context.Background()

    It("should create a Deployment for a new CloudForgeApp", func() {
        app := &cloudforcev1.CloudForgeApp{
            ObjectMeta: metav1.ObjectMeta{
                Name:      "test-app",
                Namespace: "default",
            },
            Spec: cloudforcev1.CloudForgeAppSpec{
                Image:    "nginx:latest",
                Replicas: 2,
                Port:     80,
            },
        }
        Expect(k8sClient.Create(ctx, app)).To(Succeed())

        // Wait for reconciliation
        Eventually(func() error {
            var deployment appsv1.Deployment
            return k8sClient.Get(ctx, types.NamespacedName{
                Name:      "test-app",
                Namespace: "default",
            }, &deployment)
        }, timeout, interval).Should(Succeed())

        // Verify Deployment spec
        var deployment appsv1.Deployment
        Expect(k8sClient.Get(ctx, types.NamespacedName{
            Name: "test-app", Namespace: "default",
        }, &deployment)).To(Succeed())
        Expect(*deployment.Spec.Replicas).To(Equal(int32(2)))
    })
})
```

**Reading:**
- kubebuilder book (book.kubebuilder.io)
- "Programming Kubernetes" chapters 6-9
- controller-runtime documentation

---

### Phase 4: Observability Stack (Month 10)

**Build:** Full observability pipeline — metrics, logs, traces — deployed and managed via GitOps

**Features:**
- Prometheus + Grafana for metrics
- Loki + Promtail for log aggregation
- Jaeger or Tempo for distributed tracing
- Custom Grafana dashboards per tenant
- Alerting rules (PrometheusRule CRDs)
- SLO monitoring
- Operator-exported custom metrics

**Skills Learned:**
- Prometheus architecture and PromQL
- Grafana dashboard design
- Log aggregation patterns
- Distributed tracing with OpenTelemetry
- Alert design (symptoms vs causes)
- Service Level Objectives

**Prometheus Stack (kube-prometheus-stack):**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: monitoring
  namespace: argocd
spec:
  source:
    repoURL: https://prometheus-community.github.io/helm-charts
    chart: kube-prometheus-stack
    targetRevision: 55.0.0
    helm:
      values: |
        prometheus:
          prometheusSpec:
            serviceMonitorSelectorNilUsesHelmValues: false
            podMonitorSelectorNilUsesHelmValues: false
            ruleSelectorNilUsesHelmValues: false
            retention: 30d
            storageSpec:
              volumeClaimTemplate:
                spec:
                  storageClassName: standard
                  resources:
                    requests:
                      storage: 50Gi
        grafana:
          adminPassword: changeme
          dashboardProviders:
            dashboardproviders.yaml:
              apiVersion: 1
              providers:
                - name: cloudforge
                  folder: CloudForge
                  type: file
                  options:
                    path: /var/lib/grafana/dashboards/cloudforge
```

**Custom Metrics from Your Operator:**
```go
var (
    appReconcileTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "cloudforge_app_reconcile_total",
            Help: "Total number of CloudForgeApp reconciliations",
        },
        []string{"namespace", "name", "result"},
    )

    appReconcileDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "cloudforge_app_reconcile_duration_seconds",
            Help:    "Duration of CloudForgeApp reconciliation",
            Buckets: prometheus.DefBuckets,
        },
        []string{"namespace", "name"},
    )

    appReadyReplicas = prometheus.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "cloudforge_app_ready_replicas",
            Help: "Number of ready replicas per CloudForgeApp",
        },
        []string{"namespace", "name"},
    )
)
```

**PrometheusRule for Alerts:**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: cloudforge-alerts
spec:
  groups:
    - name: cloudforge.rules
      rules:
        - alert: CloudForgeAppNotReady
          expr: |
            cloudforge_app_ready_replicas < cloudforge_app_desired_replicas
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "CloudForgeApp {{ $labels.name }} has insufficient replicas"
            description: "{{ $labels.name }} in {{ $labels.namespace }} has {{ $value }} ready replicas"

        - alert: CloudForgeAppReconcileErrors
          expr: |
            rate(cloudforge_app_reconcile_total{result="error"}[5m]) > 0
          for: 10m
          labels:
            severity: critical
          annotations:
            summary: "CloudForgeApp reconcile errors for {{ $labels.name }}"

        - alert: HighPodRestartRate
          expr: |
            rate(kube_pod_container_status_restarts_total[15m]) * 60 * 15 > 3
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "Pod {{ $labels.pod }} is restarting frequently"
```

**Reading:**
- Prometheus documentation (prometheus.io/docs)
- "Prometheus: Up & Running" by Brian Brazil
- Grafana dashboard best practices
- OpenTelemetry documentation

---

### Phase 5: Service Mesh & Security (Month 11)

**Build:** Service mesh for mTLS and traffic management, plus comprehensive security hardening

**Features:**
- Istio or Linkerd installation and configuration
- Automatic mTLS between all services
- Traffic shifting for canary deployments
- Circuit breaking and retries
- Pod Security Admission (restricted profile)
- Network segmentation with mesh policies
- Image signature verification (cosign + Kyverno)
- Audit logging

**Skills Learned:**
- Service mesh architecture
- mTLS and zero-trust networking
- Traffic management (VirtualService, DestinationRule)
- Pod Security Standards
- Supply chain security
- Kubernetes audit logging

**Istio Traffic Shifting (Canary):**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: payment-service
spec:
  hosts:
    - payment-service
  http:
    - match:
        - headers:
            x-canary:
              exact: "true"
      route:
        - destination:
            host: payment-service
            subset: canary
    - route:
        - destination:
            host: payment-service
            subset: stable
          weight: 90
        - destination:
            host: payment-service
            subset: canary
          weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: payment-service
spec:
  host: payment-service
  subsets:
    - name: stable
      labels:
        version: v1
    - name: canary
      labels:
        version: v2
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: DEFAULT
        http1MaxPendingRequests: 100
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 60s
```

**Pod Security (Restricted):**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: tenant-team-payments
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

**Image Verification Policy:**
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signatures
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-cosign
      match:
        any:
          - resources:
              kinds:
                - Pod
      verifyImages:
        - imageReferences:
            - "registry.company.com/*"
          attestors:
            - entries:
                - keys:
                    publicKeys: |-
                      -----BEGIN PUBLIC KEY-----
                      ...
                      -----END PUBLIC KEY-----
```

**Reading:**
- Istio or Linkerd documentation
- "Hacking Kubernetes" (full book)
- Kubernetes Pod Security Standards
- NIST Container Security Guide

---

### Phase 6: Production Hardening & Chaos (Month 12)

**Build:** Battle-hardened platform with chaos engineering, disaster recovery, and operational runbooks

**Features:**
- Chaos engineering with Litmus or Chaos Mesh
- Pod disruption budgets
- Priority classes and preemption
- Cluster autoscaler simulation
- Velero for backup and disaster recovery
- Operational runbooks (as code)
- Load testing with k6
- Full end-to-end deployment pipeline

**Skills Learned:**
- Chaos engineering methodology
- Disaster recovery planning
- Capacity planning
- PodDisruptionBudgets
- Priority and preemption
- Backup and restore patterns
- Performance testing

**Chaos Experiments:**
```yaml
# Pod Kill Experiment
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pod-kill-payment-service
spec:
  action: pod-kill
  mode: one
  selector:
    namespaces:
      - tenant-team-payments
    labelSelectors:
      app: payment-service
  scheduler:
    cron: "@every 2h"
---
# Network Delay Experiment
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: network-delay-test
spec:
  action: delay
  mode: all
  selector:
    namespaces:
      - tenant-team-payments
    labelSelectors:
      app: payment-service
  delay:
    latency: "200ms"
    correlation: "25"
    jitter: "50ms"
  duration: "5m"
```

**PodDisruptionBudget:**
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payment-service-pdb
spec:
  minAvailable: 2    # OR maxUnavailable: 1
  selector:
    matchLabels:
      app: payment-service
```

**Priority Classes:**
```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: platform-critical
value: 1000000
globalDefault: false
description: "For platform-level components that must not be preempted"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: tenant-high
value: 100000
globalDefault: false
description: "For high-priority tenant workloads"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: tenant-default
value: 10000
globalDefault: true
description: "Default priority for tenant workloads"
```

**Velero Backup Schedule:**
```yaml
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: daily-backup
  namespace: velero
spec:
  schedule: "0 2 * * *"
  template:
    includedNamespaces:
      - "tenant-*"
    includedResources:
      - "*"
    storageLocation: default
    ttl: 720h  # 30 days
    snapshotVolumes: true
```

**Reading:**
- "Chaos Engineering" by Casey Rosenthal & Nora Jones
- Litmus / Chaos Mesh documentation
- Velero documentation
- Kubernetes reliability best practices

---

## Project Progression

Projects are ordered by complexity. Each builds on concepts from the previous.

### Level 1: Deploy & Operate

#### Project 1.1: Multi-Tier Application
**Deploy a frontend + backend + database stack**

Deploy:
- React/Nginx frontend (Deployment + Service)
- Node.js or Go API (Deployment + Service)
- PostgreSQL (StatefulSet + PVC)
- ConfigMaps for configuration
- Secrets for database credentials

**Concepts learned:**
- Deployments, Services, StatefulSets
- ConfigMaps and Secrets
- PersistentVolumeClaims
- Inter-service communication via DNS

**Extensions:**
- Add Ingress with TLS
- Set up health checks (liveness, readiness)
- Add resource requests and limits

---

#### Project 1.2: Blue/Green & Canary Deployments
**Implement deployment strategies without a service mesh**

Features:
- Blue/green deployment using label switching
- Canary deployment with multiple Deployments
- Rollback procedures
- Zero-downtime verification

**Concepts learned:**
- Service label selectors
- Rolling update strategies
- kubectl rollout commands
- Deployment history and rollback

**Extensions:**
- Automate with a shell script
- Add health check gates
- Measure deployment metrics

---

#### Project 1.3: CronJob Pipeline
**Build a data processing pipeline with Jobs and CronJobs**

Features:
- CronJob that fetches data
- Job that processes data
- Job that generates reports
- Shared storage between jobs (PVC)

**Concepts learned:**
- Jobs and CronJobs
- Init containers
- Shared volumes
- Job completion and failure handling

---

### Level 2: Configure & Secure

#### Project 2.1: RBAC Security Model
**Design a complete RBAC system for a fictional company**

Features:
- Cluster roles: cluster-admin, namespace-admin, developer, viewer
- Per-namespace RoleBindings
- ServiceAccount for each application
- Audit which permissions each role has

**Concepts learned:**
- Roles vs ClusterRoles
- RoleBindings vs ClusterRoleBindings
- ServiceAccounts
- `kubectl auth can-i` for verification

**Extensions:**
- OIDC integration design
- Aggregate ClusterRoles
- Automate with scripts

---

#### Project 2.2: NetworkPolicy Firewall
**Implement microsegmentation with NetworkPolicies**

Features:
- Default deny all traffic
- Allow frontend → backend
- Allow backend → database
- Allow monitoring → all
- Block all egress except DNS and specific APIs

**Concepts learned:**
- NetworkPolicy syntax and semantics
- Ingress vs Egress policies
- Namespace selectors
- Port-level controls
- Testing with `netshoot` and `curl`

---

#### Project 2.3: Secret Management Pipeline
**Manage secrets across environments**

Features:
- Sealed Secrets for Git-stored secrets
- External Secrets Operator for cloud provider secrets
- Secret rotation strategy
- Integration with cert-manager for TLS

**Concepts learned:**
- Secret types (Opaque, TLS, docker-registry)
- Sealed Secrets workflow
- External Secrets Operator
- Volume mounts vs env vars for secrets

---

### Level 3: Extend & Automate

#### Project 3.1: First Operator (Go)
**Build a simple operator that manages a custom resource**

Build an operator that manages a "Website" CRD:
- Creates a Deployment with nginx
- Creates a ConfigMap with HTML content
- Creates a Service and Ingress
- Updates when spec changes

**Concepts learned:**
- kubebuilder scaffolding
- CRD design
- Reconciliation loop
- Owner references
- envtest

---

#### Project 3.2: GitOps Everything
**Full GitOps setup with ArgoCD**

Features:
- ArgoCD managing multiple apps
- App of Apps pattern
- ApplicationSets for multi-environment
- Automated sync with self-heal
- Notifications (Slack/webhook)

**Concepts learned:**
- ArgoCD architecture
- Sync policies and waves
- Health checks
- ApplicationSets and generators
- Diff and drift detection

---

#### Project 3.3: Custom Scheduler
**Write a custom Kubernetes scheduler**

Build a scheduler that:
- Schedules based on custom node labels
- Implements a custom scoring algorithm
- Falls back to default scheduler

**Concepts learned:**
- Scheduler framework
- Scheduling plugins
- Node affinity vs custom scheduling
- Multi-scheduler setups

---

### Level 4: Observe & Debug

#### Project 4.1: Observability Platform
**Deploy and configure full monitoring stack**

Features:
- Prometheus with custom scrape configs
- Grafana dashboards (RED method)
- Alert rules for SLOs
- Loki for log aggregation
- Jaeger for tracing

**Concepts learned:**
- PromQL
- ServiceMonitor and PodMonitor CRDs
- Grafana dashboard JSON
- Log aggregation patterns
- Trace propagation

---

#### Project 4.2: Debugging Gauntlet
**Intentionally break things and practice debugging**

Create a cluster with intentional problems:
- Pod in CrashLoopBackOff (bad command)
- Pod stuck in Pending (resource limits)
- Service with wrong selector (no endpoints)
- PVC stuck in Pending (no StorageClass)
- ImagePullBackOff (wrong image name)
- OOMKilled containers
- Failing readiness probes

**Concepts learned:**
- Systematic debugging methodology
- `kubectl describe`, `kubectl logs`, `kubectl events`
- Common failure modes and resolutions
- Container runtime debugging

---

### Level 5: Platform Engineering

#### Project 5.1: Internal Developer Platform
**Build a self-service platform for developers**

Features:
- Tenant provisioning (namespace, quotas, RBAC)
- Application deployment via CRD
- Database provisioning (operator creates PG instances)
- Environment promotion (dev → staging → prod)

**Concepts learned:**
- Platform engineering patterns
- Multi-tenancy at scale
- Self-service abstractions
- Environment management

---

#### Project 5.2: Multi-Cluster Management
**Manage workloads across multiple clusters**

Features:
- Multiple kind clusters
- Cluster API or vcluster for cluster provisioning
- Cross-cluster service discovery
- Federated deployments

**Concepts learned:**
- Multi-cluster patterns
- Cluster API concepts
- Cross-cluster networking
- Federated resources

---

## Open Source Study

### Projects to Read (In Order of Complexity)

#### Beginner
| Project | Why Study It |
|---------|--------------|
| **ingress-nginx** | How ingress controllers work |
| **metrics-server** | Simple K8s component, good entry point |
| **kube-state-metrics** | How to export K8s state as metrics |
| **sealed-secrets** | Simple controller pattern |

#### Intermediate
| Project | Why Study It |
|---------|--------------|
| **cert-manager** | Production-quality operator, excellent code |
| **external-dns** | External resource management from K8s |
| **ArgoCD** | GitOps implementation, complex reconciliation |
| **kustomize** | Configuration transformation patterns |
| **Kyverno** | Policy engine, admission webhooks |

#### Advanced
| Project | Why Study It |
|---------|--------------|
| **Prometheus Operator** | Operator managing complex stateful systems |
| **Istio** | Service mesh, control plane design |
| **Linkerd** | Simpler service mesh, excellent Go code |
| **Crossplane** | Extending K8s to manage cloud resources |
| **Cluster API** | Managing K8s clusters with K8s |
| **Knative** | Serverless on K8s |

#### Expert
| Project | Why Study It |
|---------|--------------|
| **Kubernetes itself** | The scheduler, API server, controller-manager |
| **etcd** | The database backing all of K8s |
| **containerd** | Container runtime |
| **Cilium** | eBPF-based networking |
| **Vitess** | MySQL scaling on K8s (used by Slack, GitHub) |
| **Tekton** | Cloud-native CI/CD pipelines |

### How to Study Open Source Kubernetes Projects

1. **Start with the CRD/API types** — What resources does it define? What's in `spec` vs `status`?
2. **Find the reconciler** — The `Reconcile()` function is the heart of any operator
3. **Trace a resource lifecycle** — Create → Reconcile → Update → Delete
4. **Read the tests** — envtest tests show expected behavior
5. **Read the issues and design docs** — Understand WHY decisions were made
6. **Run it locally** — Deploy to kind, create resources, watch what happens

---

## Common Pitfalls

### Resource Management

**1. No resource requests/limits**
```yaml
# Bad: No limits — your pod can eat the whole node
containers:
  - name: app
    image: my-app

# Good: Always set requests (for scheduling) and limits (for protection)
containers:
  - name: app
    image: my-app
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "500m"
        memory: "512Mi"
```

**Key insight:** Requests are for scheduling (how much the scheduler reserves). Limits are for enforcement (the container is killed/throttled beyond this). Always set requests. Set memory limits. CPU limits are debated — they cause throttling that can be hard to diagnose.

**2. Liveness probe that checks dependencies**
```yaml
# Bad: Liveness checks database — if DB is down, K8s kills ALL your pods
livenessProbe:
  httpGet:
    path: /health    # This checks DB connection
    port: 8080

# Good: Liveness checks only if the PROCESS is alive
livenessProbe:
  httpGet:
    path: /livez     # Only checks if the server responds
    port: 8080
readinessProbe:
  httpGet:
    path: /readyz    # This checks dependencies (DB, cache, etc.)
    port: 8080
```

Liveness = "Is the process stuck?" (restart if failing). Readiness = "Can this pod serve traffic?" (remove from service if failing). Confusing them causes cascading outages.

**3. Missing PodDisruptionBudgets**
```yaml
# Without PDB: A node drain can kill ALL your pods at once
# With PDB: K8s ensures minimum availability during voluntary disruptions

apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: my-app
```

### Networking

**4. Hardcoding Pod IPs**
```yaml
# Bad: Pod IPs are ephemeral — they change on every restart
env:
  - name: BACKEND_URL
    value: "http://10.244.1.15:8080"

# Good: Use Service DNS names
env:
  - name: BACKEND_URL
    value: "http://backend-service.my-namespace.svc.cluster.local:8080"
  # Or simply:
  - name: BACKEND_URL
    value: "http://backend-service:8080"    # Same namespace
```

**5. Exposing services incorrectly**
```
LoadBalancer → Creates a cloud LB per service ($$$)
NodePort     → Exposes on every node (security risk, port conflicts)
ClusterIP    → Internal only (what you usually want)
Ingress      → Single entry point, route by host/path (usually best)
```

### Security

**6. Running as root**
```yaml
# Bad: Container runs as root
containers:
  - name: app
    image: my-app

# Good: Non-root with read-only filesystem
containers:
  - name: app
    image: my-app
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
      readOnlyRootFilesystem: true
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
```

**7. Using `latest` tag**
```yaml
# Bad: "latest" is mutable — you don't know what you're running
image: my-app:latest

# Good: Use immutable tags or digests
image: my-app:v2.1.0
# Best: Use digest
image: my-app@sha256:abc123...
```

### Configuration

**8. Environment-specific values in base manifests**
```yaml
# Bad: Hardcoded values
env:
  - name: DATABASE_URL
    value: "postgres://prod-db:5432/myapp"

# Good: Use ConfigMaps/Secrets with Kustomize overlays
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: database-credentials
        key: url
```

**9. Not using namespaces**
```bash
# Bad: Everything in default namespace
kubectl get pods  # 200 pods from 15 different teams

# Good: Namespace per team/environment
kubectl get pods -n team-payments  # Only payment team's pods
```

### Operational

**10. Not monitoring etcd**

etcd is the most critical component. If etcd is slow or unhealthy, the entire cluster degrades. Monitor:
- `etcd_disk_wal_fsync_duration_seconds` — disk latency
- `etcd_server_proposals_failed_total` — consensus failures
- `etcd_mvcc_db_total_size_in_bytes` — database size

**11. Ignoring events**
```bash
# Events tell you WHY things are broken
kubectl get events --sort-by=.lastTimestamp -n my-namespace

# Common events you'll see:
# FailedScheduling    → Not enough resources or node affinity mismatch
# FailedMount         → Volume couldn't be attached
# BackOff             → Container keeps crashing
# Unhealthy           → Probe failing
# FailedCreate        → Couldn't create pod (quota, admission)
```

---

## Daily Habits

### The 2-Hour Daily Practice

| Time | Activity |
|------|----------|
| 30 min | Operate: Deploy, debug, and break things in your kind cluster |
| 45 min | Study: Read book chapters or documentation |
| 30 min | Build: Work on current project |
| 15 min | Community: Read K8s blog, KubeCon talks, or CNCF news |

### Weekly Goals

- **Monday-Friday:** Work on current project phase
- **Saturday:** Break something intentionally and practice debugging
- **Sunday:** Review the week, plan next week, watch a KubeCon talk

### Cluster Practice

Every day, practice something in your local cluster:

**Week 1-4:** Core operations
- Deploy apps, scale them, update them, roll back
- Create ConfigMaps, Secrets, mount them
- Set up Ingress with TLS
- Debug common failure modes

**Week 5-8:** Security and networking
- Implement RBAC for multiple teams
- Write NetworkPolicies
- Set up Pod Security Standards
- Practice with `kubectl auth can-i`

**Week 9-12:** Advanced operations
- Deploy monitoring stack
- Set up ArgoCD
- Build a simple operator
- Practice cluster upgrades

**Week 13+:** Platform building
- Deploy multi-tenant configurations
- Implement chaos experiments
- Build custom controllers
- Study production patterns

### Certification Path

| Cert | Focus | When |
|------|-------|------|
| **CKAD** | Application developer skills | Month 4-5 |
| **CKA** | Cluster administration | Month 7-8 |
| **CKS** | Security specialist | Month 10-11 |

These are hands-on exams in a live cluster. The daily practice above directly prepares you.

---

## 12-Month Schedule

### Core Path (Months 1-6) — Foundations

| Month | Focus | Books | Projects |
|-------|-------|-------|----------|
| 1 | K8s fundamentals: Pods, Deployments, Services | K8s in Action Ch 1-6 | Multi-tier app deployment |
| 2 | Storage, StatefulSets, config | K8s in Action Ch 7-12 | Stateful workload, Blue/Green deploy |
| 3 | Scheduling, resources, autoscaling, RBAC | K8s in Action Ch 13-18 | RBAC model, CronJob pipeline |
| 4 | Production operations | K8s Up & Running (full) | NetworkPolicy firewall, CKAD prep |
| 5 | Production patterns | Production Kubernetes (first half) | Secret management, Debugging gauntlet |
| 6 | Networking & security deep dive | Production K8s (second half), Networking and K8s | Observability platform, CKA prep |

### CloudForge Project (Months 7-12) — Platform Engineering

| Month | Focus | Books | CloudForge Phase |
|-------|-------|-------|------------------|
| 7 | GitOps & cluster foundation | GitOps and Kubernetes | **Phase 1:** GitOps cluster bootstrap (ArgoCD, Ingress, certs) |
| 8 | Multi-tenancy | Hacking Kubernetes | **Phase 2:** Multi-tenant platform (CRD, RBAC, NetworkPolicy, quotas) |
| 9 | Operator development | Programming Kubernetes, kubebuilder book | **Phase 3:** Custom operator (CloudForgeApp, canary, envtest) |
| 10 | Observability | Prometheus: Up & Running | **Phase 4:** Full observability stack (metrics, logs, traces, alerts) |
| 11 | Service mesh & security | Istio/Linkerd docs, Container Security | **Phase 5:** Service mesh, mTLS, image verification, CKS prep |
| 12 | Production hardening | Chaos Engineering | **Phase 6:** Chaos engineering, DR, backup, load testing |

### Skills Progression

| Month | Operations Skills | Platform Skills |
|-------|-------------------|-----------------|
| 1-2 | Deploy, configure, expose workloads | - |
| 3-4 | RBAC, scheduling, resource management, autoscaling | - |
| 5-6 | Networking, security, monitoring, debugging | - |
| 7 | - | GitOps, Kustomize, ArgoCD, cluster bootstrapping |
| 8 | - | Multi-tenancy, policy engines, namespace isolation |
| 9 | - | Operator development (Go), CRD design, envtest |
| 10 | - | Prometheus, Grafana, Loki, tracing, alerting |
| 11 | - | Service mesh, mTLS, supply chain security |
| 12 | - | Chaos engineering, DR, capacity planning |

---

## The Path to Cracked

### Beginner (Months 1-3)
You can:
- Deploy applications to Kubernetes
- Expose services with Ingress and TLS
- Configure apps with ConfigMaps and Secrets
- Manage storage with PVCs
- Set up RBAC for basic access control
- Debug common Pod failures
- Use `kubectl` fluently

### Intermediate (Months 4-6)
You can:
- Run production workloads with proper resource management
- Design NetworkPolicies for microsegmentation
- Set up monitoring and alerting
- Perform cluster upgrades safely
- Debug complex networking issues
- Pass the CKA/CKAD exams
- Read and understand Kubernetes source code

### Advanced (Months 7-9)
After CloudForge Phases 1-3, you can:
- Bootstrap clusters with GitOps
- Design multi-tenant platforms
- Build Kubernetes operators in Go
- Implement custom reconciliation logic
- Write CRDs with proper status and conditions
- Test controllers with envtest

### Cracked (Months 10-12+)
After completing CloudForge, you can:
- Architect production Kubernetes platforms
- Implement full observability with custom metrics and SLOs
- Deploy and configure service meshes
- Harden clusters against real attack vectors
- Design chaos experiments and run game days
- Plan and execute disaster recovery
- Understand Kubernetes internals deeply enough to debug anything
- Build and ship operators that other teams depend on
- Contribute to the CNCF ecosystem

---

## Resources Quick Reference

### Bookmarks

```
# Official
kubernetes.io/docs              # Official documentation
kubernetes.io/blog              # K8s blog
kubernetes.io/docs/reference    # API reference

# Learning
kubernetes.io/docs/tutorials    # Official tutorials
killercoda.com                  # Interactive K8s scenarios (free)
killer.sh                       # CKA/CKAD exam simulator
play-with-k8s.com              # Browser-based K8s playground

# Tools
book.kubebuilder.io            # Kubebuilder book (operators)
helm.sh/docs                   # Helm documentation
argoproj.github.io/argo-cd     # ArgoCD documentation
kustomize.io                   # Kustomize documentation

# Deep Dives
github.com/kelseyhightower/kubernetes-the-hard-way  # Build K8s from scratch
learnk8s.io/blog               # Excellent technical articles
iximiuz.com/en                  # Containers and K8s internals
arthurchiao.art/blog            # Deep networking posts

# CNCF Ecosystem
landscape.cncf.io              # The full CNCF landscape
cncf.io/blog                   # CNCF blog
youtube.com/c/cloudnativefdn   # KubeCon talks

# Community
kubernetes.slack.com           # Official Slack
reddit.com/r/kubernetes        # Reddit
discuss.kubernetes.io          # Forums
github.com/kubernetes/community  # SIGs and working groups
```

### Key People to Follow

**Kubernetes Core:**
- **Kelsey Hightower** — K8s evangelist, Kubernetes the Hard Way
- **Tim Hockin** — K8s co-founder, networking lead
- **Brendan Burns** — K8s co-founder, author
- **Joe Beda** — K8s co-founder
- **Clayton Coleman** — OpenShift, K8s API

**Platform & Operations:**
- **Liz Rice** — Container security, eBPF, Isovalent/Cilium
- **Jessie Frazelle** — Containers, security
- **Charity Majors** — Observability, operations
- **Cindy Sridharan** — Distributed systems, observability
- **Nana Janashia** — K8s education, TechWorld with Nana

**Operators & Extensions:**
- **Stefan Schimanski** — Programming Kubernetes author, API machinery
- **Michael Hausenblas** — Programming Kubernetes author
- **Viktor Farcic** — GitOps, DevOps Toolkit
- **Daniel Bryant** — Platform engineering

### Podcasts

- **Kubernetes Podcast from Google** — Weekly K8s news and interviews
- **The POPCAST with Dan POP** — Cloud native discussions
- **Cloud Native Live** — CNCF webinars
- **DevOps Paradox** — Viktor Farcic's podcast
- **The Changelog** — General dev, often cloud native content
- **Software Engineering Daily** — Deep technical interviews

---

## Final Words

Kubernetes is not just a tool — it's a platform for building platforms. The engineers who truly understand it don't just deploy YAML; they understand WHY the system works the way it does.

The path to cracked follows three stages:

1. **User** — You can deploy and operate workloads. You know the resources, the commands, the patterns. This is months 1-6.
2. **Builder** — You can extend Kubernetes. You write operators, design platforms, implement GitOps. You teach Kubernetes about your domain. This is months 7-9.
3. **Expert** — You understand the internals. You can debug anything. You design production platforms. You know the trade-offs. This is months 10-12+.

### The CloudForge Advantage

By building one comprehensive platform project, you'll:

- **See how everything connects** — GitOps deploys operators that manage tenants that run workloads that are observed by monitoring that triggers alerts
- **Build production patterns** — Multi-tenancy, security, observability, chaos engineering
- **Have a portfolio piece** — A complete internal developer platform you can demo
- **Learn the full stack** — From YAML to Go operators to PromQL to chaos experiments

Most tutorials teach you to deploy a pod. CloudForge teaches you to build the platform that thousands of pods run on.

### What Comes After

Once you've completed CloudForge, you can:
- **Go multi-cluster** — Cluster API, Federation, service mesh across clusters
- **Build a real platform** — Apply these patterns at work
- **Contribute upstream** — K8s SIGs, CNCF projects
- **Specialize** — Security (CKS), networking (Cilium/eBPF), ML platforms (Kubeflow), edge (KubeEdge)

The infrastructure that runs the modern internet runs on Kubernetes. Every major company, every cloud provider, every startup building at scale depends on it. The engineers who deeply understand this system — who can build operators, design platforms, debug networking, and harden security — are the most valuable infrastructure engineers in the industry.

Your goal is to join that group.

Start a kind cluster. Deploy something. Break it. Fix it. Build on it.

---

*Generated: February 2026*
