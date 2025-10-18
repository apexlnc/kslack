<div align="center">
  <h1>kslack</h1>
  <p><strong>Slack Bot for Kagent Multi-Agent Platform</strong></p>

  <div>
    <a href="https://github.com/kagent-dev/kslack/releases">
      <img src="https://img.shields.io/github/v/release/kagent-dev/kslack?style=flat&label=Latest%20version" alt="Release">
    </a>
    <a href="https://opensource.org/licenses/Apache-2.0">
      <img src="https://img.shields.io/badge/License-Apache2.0-brightgreen.svg?style=flat" alt="License: Apache 2.0">
    </a>
    <a href="https://github.com/kagent-dev/kslack">
      <img src="https://img.shields.io/github/stars/kagent-dev/kslack.svg?style=flat&logo=github&label=Stars" alt="Stars">
    </a>
    <a href="https://discord.gg/Fu3k65f2k3">
      <img src="https://img.shields.io/discord/1346225185166065826?style=flat&label=Join%20Discord&color=6D28D9" alt="Discord">
    </a>
  </div>
</div>

---

**kslack** is a production-ready Slack bot for the [Kagent](https://github.com/kagent-dev/kagent) multi-agent platform. It provides a unified interface to interact with multiple AI agents through Slack, featuring dynamic agent discovery, intelligent routing, and rich Block Kit formatting with human-in-the-loop (HITL) support.

---

## Get Started

- [Quick Start](#quick-start) - Run kslack locally in 5 minutes
- [Helm Installation](#option-1-helm-recommended) - Deploy to Kubernetes with Helm
- [Slack Setup Guide](./SLACK_SETUP.md) - Configure your Slack app

---

## Features

- **Dynamic Agent Discovery**: Automatically discovers agents from Kagent via `/api/agents`
- **Intelligent Routing**: Keyword-based matching to route messages to appropriate agents
- **Streaming Responses**: Real-time updates for declarative agents with human-in-the-loop approval
- **Loading States**: Native Slack loading indicators show agent processing status (Slack Bolt 1.26+)
- **Feedback Buttons**: Thumbs up/down on responses for tracking agent performance
- **RBAC**: Slack user group integration with agent-level permissions
- **Rich Formatting**: Professional Slack Block Kit responses with metadata
- **Session Management**: Maintains conversation context across multiple turns
- **Async Architecture**: Built with modern slack-bolt AsyncApp for high performance
- **Production Ready**: Prometheus metrics, health checks, structured logging
- **Kubernetes Native**: Complete K8s manifests with HPA, PDB, and security contexts

## Architecture

```
User in Slack
    ↓
@mention / slash command
    ↓
Kagent Slackbot (AsyncApp)
    ├── Agent Discovery (cache agents from /api/agents)
    ├── Agent Router (keyword matching)
    └── A2A Client (JSON-RPC 2.0)
        ↓
Kagent Controller (/api/a2a/{namespace}/{name})
    ↓
    ┌─────────┬─────────┬──────────┐
    │ k8s     │ security│ research │
    │ agent   │ agent   │ agent    │
    └─────────┴─────────┴──────────┘
```

## Quick Start

### Prerequisites

- Python 3.13+
- Slack workspace with bot app configured
- Kagent instance running and accessible

### Installation

1. Clone the repository:
```bash
git clone https://github.com/kagent-dev/kslack.git
cd kslack
```

2. Create virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Slack tokens and Kagent URL
```

Required environment variables:
- `SLACK_BOT_TOKEN`: Bot user OAuth token (xoxb-*)
- `SLACK_APP_TOKEN`: App-level token for Socket Mode (xapp-*)
- `SLACK_SIGNING_SECRET`: Signing secret for request verification
- `KAGENT_BASE_URL`: Kagent API base URL (e.g., http://localhost:8083)

### Running Locally

```bash
source .venv/bin/activate
python -m kslack.main
```

The bot will:
1. Connect to Slack via Socket Mode (WebSocket)
2. Start health server on port 8080
3. Discover available agents from Kagent
4. Begin processing messages

### Slack App Configuration

Your Slack app needs these OAuth scopes:
- `app_mentions:read` - Receive @mentions
- `chat:write` - Send messages
- `commands` - Handle slash commands
- `reactions:write` - Add emoji reactions

Required features:
- **Socket Mode**: Enabled (no public HTTP endpoint needed)
- **Event Subscriptions**: `app_mention`
- **Slash Commands**: `/agents`, `/agent-switch`

## Usage

### Interacting with Agents

**@mention the bot** with your question:
```
@kagent show me failing pods
```

The bot will:
1. Extract keywords from your message ("pods" → k8s-agent)
2. Route to the appropriate agent
3. Respond with formatted blocks showing:
   - Which agent responded
   - Why that agent was selected
   - Response time and session ID

### Slash Commands

**List available agents**:
```
/agents
```

Shows all agents with:
- Namespace and name
- Description
- Ready status

**Switch to specific agent**:
```
/agent-switch kagent/security-agent
```

All subsequent @mentions will use this agent until you reset.

**Reset to automatic routing**:
```
/agent-switch reset
```

Returns to keyword-based agent selection.

### Human-in-the-Loop (HITL) Approvals

When agents request approval for sensitive operations (like deleting pods), the bot displays an interactive approval UI:

```
@kagent delete pod my-app-xyz in namespace prod
```

The bot shows:
- Tool name and arguments requiring approval
- **Approve** and **Deny** buttons
- Session and task context

**Workflow**:
1. Agent detects sensitive operation and requests approval
2. Slackbot displays approval buttons in Slack
3. User clicks Approve or Deny
4. Slackbot sends structured decision (DataPart + TextPart) to agent
5. Agent resumes execution with user's decision
6. Completion message shown to user

**Technical Details**:
- Uses A2A protocol `input_required` state for interrupts
- Sends DataPart with `decision_type: tool_approval` for reliable parsing
- Tracks contextId and taskId for proper task resumption
- Streams completion responses in real-time

## Development

### Project Structure

```
src/kslack/
├── main.py                 # Entry point, AsyncApp initialization
├── config.py               # Configuration management
├── constants.py            # Application constants
├── handlers/               # Slack event handlers
│   ├── mentions.py        # @mention handling
│   ├── commands.py        # Slash command handling
│   ├── actions.py         # Button action handling (HITL approvals)
│   └── middleware.py      # Prometheus metrics
├── services/               # Business logic
│   ├── a2a_client.py      # Kagent A2A protocol client (JSON-RPC 2.0)
│   ├── agent_discovery.py # Agent discovery from API
│   └── agent_router.py    # Agent routing logic
├── auth/                   # Authorization
│   ├── permissions.py     # RBAC permissions checker
│   └── slack_groups.py    # Slack user group integration
└── slack/                  # Slack utilities
    ├── formatters.py      # Block Kit formatting
    └── validators.py      # Input validation
```

### Type Checking

```bash
.venv/bin/mypy src/kslack/
```

### Linting

```bash
.venv/bin/ruff check src/
```

Auto-fix issues:
```bash
.venv/bin/ruff check --fix src/
```

## Deployment

### Prerequisites

1. **Kagent instance** running and accessible
2. **Slack App configured** with Socket Mode (see [SLACK_SETUP.md](./SLACK_SETUP.md))
3. **Slack API tokens** obtained (Bot Token, App Token, Signing Secret)

### Option 1: Helm (Recommended)

The easiest way to deploy kslack to Kubernetes is using Helm:

```bash
# Install from the chart directory
helm install kslack ./chart \
  --namespace kagent \
  --create-namespace \
  --set secrets.slackBotToken="xoxb-your-token" \
  --set secrets.slackAppToken="xapp-your-token" \
  --set secrets.slackSigningSecret="your-secret" \
  --set config.kagentBaseUrl="http://kagent-controller.kagent.svc.cluster.local:8083"
```

Or use a values file:

```yaml
# my-values.yaml
secrets:
  slackBotToken: "xoxb-..."
  slackAppToken: "xapp-..."
  slackSigningSecret: "..."

config:
  kagentBaseUrl: "http://kagent-controller.kagent.svc.cluster.local:8083"
  logLevel: "INFO"

autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 3

nodeSelector:
  workload-type: ai-agents

tolerations:
- key: "ai-workload"
  operator: "Equal"
  value: "true"
  effect: "NoSchedule"

permissions:
  agent_permissions:
    kagent/k8s-agent:
      user_groups:
        - S0T8FCWSB
```

```bash
helm install kslack ./chart -f my-values.yaml
```

**Upgrade existing installation:**

```bash
helm upgrade kslack ./chart -f my-values.yaml
```

**Verify installation:**

```bash
# Check deployment status
helm status kslack

# View pods
kubectl get pods -n kagent -l app.kubernetes.io/name=kslack

# View logs
kubectl logs -f -n kagent -l app.kubernetes.io/name=kslack
```

### Option 2: Docker

Build and run with Docker:

```bash
# Build image
docker build -t kslack:latest .

# Run container
docker run -d \
  --name kslack \
  -e SLACK_BOT_TOKEN="xoxb-your-token" \
  -e SLACK_APP_TOKEN="xapp-your-token" \
  -e SLACK_SIGNING_SECRET="your-secret" \
  -e KAGENT_BASE_URL="http://your-kagent-url:8083" \
  -p 8080:8080 \
  kslack:latest
```

With environment file:

```bash
# Create .env file with your tokens
docker run -d --name kslack --env-file .env -p 8080:8080 kslack:latest
```

### Option 3: Kubernetes (Raw Manifests)

Deploy to Kubernetes with raw manifests (without Helm):

```yaml
# kslack-deployment.yaml
apiVersion: v1
kind: Secret
metadata:
  name: kslack-secrets
  namespace: kagent
type: Opaque
stringData:
  SLACK_BOT_TOKEN: "xoxb-your-token"
  SLACK_APP_TOKEN: "xapp-your-token"
  SLACK_SIGNING_SECRET: "your-secret"
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: kslack
  namespace: kagent
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kslack
  namespace: kagent
  labels:
    app: kslack
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kslack
  template:
    metadata:
      labels:
        app: kslack
    spec:
      serviceAccountName: kslack
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: kslack
        image: your-registry/kslack:latest
        imagePullPolicy: IfNotPresent
        ports:
        - name: health
          containerPort: 8080
          protocol: TCP
        env:
        - name: SLACK_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: kslack-secrets
              key: SLACK_BOT_TOKEN
        - name: SLACK_APP_TOKEN
          valueFrom:
            secretKeyRef:
              name: kslack-secrets
              key: SLACK_APP_TOKEN
        - name: SLACK_SIGNING_SECRET
          valueFrom:
            secretKeyRef:
              name: kslack-secrets
              key: SLACK_SIGNING_SECRET
        - name: KAGENT_BASE_URL
          value: "http://kagent-controller.kagent.svc.cluster.local:8083"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: health
          initialDelaySeconds: 5
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: health
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
          readOnlyRootFilesystem: false
      # Node selector - optional, uncomment to use
      # nodeSelector:
      #   workload-type: ai-agents

      # Tolerations - optional, uncomment to use
      # tolerations:
      # - key: "ai-workload"
      #   operator: "Equal"
      #   value: "true"
      #   effect: "NoSchedule"

      # Affinity - optional, uncomment to use
      # affinity:
      #   podAntiAffinity:
      #     preferredDuringSchedulingIgnoredDuringExecution:
      #     - weight: 100
      #       podAffinityTerm:
      #         labelSelector:
      #           matchLabels:
      #             app: kslack
      #         topologyKey: kubernetes.io/hostname
---
apiVersion: v1
kind: Service
metadata:
  name: kslack
  namespace: kagent
  labels:
    app: kslack
spec:
  type: ClusterIP
  ports:
  - port: 8080
    targetPort: health
    protocol: TCP
    name: health
  selector:
    app: kslack
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: kslack
  namespace: kagent
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: kslack
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: kslack
  namespace: kagent
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: kslack
  minReplicas: 1
  maxReplicas: 3
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

Apply to cluster:

```bash
kubectl apply -f kslack-deployment.yaml
```

### Verify Deployment

```bash
# Check pod status
kubectl get pods -n kagent -l app=kslack

# View logs
kubectl logs -f -n kagent -l app=kslack

# Check health
kubectl exec -n kagent deployment/kslack -- curl localhost:8080/health
```

### Configuration

Configure via environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SLACK_BOT_TOKEN` | Yes | - | Bot user OAuth token (xoxb-*) |
| `SLACK_APP_TOKEN` | Yes | - | App-level token (xapp-*) |
| `SLACK_SIGNING_SECRET` | Yes | - | Signing secret for verification |
| `KAGENT_BASE_URL` | No | `http://localhost:8083` | Kagent API base URL |
| `KAGENT_TIMEOUT` | No | `30` | Request timeout in seconds |
| `SERVER_HOST` | No | `0.0.0.0` | Health server bind address |
| `SERVER_PORT` | No | `8080` | Health server port |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `DEFAULT_AGENT_NAMESPACE` | No | - | Default agent namespace |
| `DEFAULT_AGENT_NAME` | No | - | Default agent name |
| `PERMISSIONS_FILE` | No | `config/permissions.yaml` | Permissions config path |

### Monitoring

**Prometheus Metrics** available at `/metrics`:
- `kagent_slackbot_messages_total{event_type, status}` - Total messages processed
- `kagent_slackbot_message_duration_seconds{event_type}` - Message processing time
- `kagent_slackbot_commands_total{command, status}` - Slash command counts
- `kagent_slackbot_agent_invocations_total{agent, status}` - Agent invocation counts
- `kagent_slackbot_agent_feedback_total{agent, sentiment}` - Agent feedback (positive/negative)

**Health Endpoints**:
- `/health` - Liveness probe
- `/ready` - Readiness probe

**Structured Logs**: JSON format with fields:
- `event`: Log message
- `level`: Log level (INFO, ERROR, etc.)
- `timestamp`: ISO 8601 timestamp
- `user`, `agent`, `session`: Contextual fields

## Troubleshooting

### Bot doesn't respond to @mentions

1. Check bot is online: `kubectl logs -n kagent deployment/slackbot`
2. Verify Socket Mode connection is established (look for "Connecting to Slack via Socket Mode")
3. Ensure Slack app has `app_mentions:read` scope
4. Check event subscription for `app_mention` is configured

### Agent discovery fails

1. Verify Kagent is accessible: `curl http://kagent-controller.kagent.svc.cluster.local:8083/api/agents`
2. Check logs for "Agent discovery failed" messages
3. Ensure `KAGENT_BASE_URL` is configured correctly

### Type errors during development

Run type checking:
```bash
.venv/bin/mypy src/kslack/
```

Common issues:
- Missing type annotations - add explicit types
- Untyped external libraries - use `# type: ignore[no-untyped-call]`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Contributors

Thanks to all contributors who are helping to make kslack better.

<a href="https://github.com/kagent-dev/kslack/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=kagent-dev/kslack" />
</a>

## References

- **Slack Bolt Docs**: https://slack.dev/bolt-python/
- **Kagent Repository**: https://github.com/kagent-dev/kagent
- **Kagent Documentation**: https://kagent.dev/docs
- **Kagent A2A Protocol**: https://github.com/kagent-dev/kagent/tree/main/go/internal/a2a
- **Agent CRD Spec**: https://github.com/kagent-dev/kagent/blob/main/go/api/v1alpha2/agent_types.go

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
