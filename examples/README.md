# kslack Helm Configuration Examples

This directory contains example Helm values files for different deployment scenarios.

## Available Examples

### 1. `basic.yaml` - Getting Started

Minimal configuration for testing and development.

**Use case**: Local testing, development environment

**Deploy**:
```bash
helm install kslack ./chart -f examples/basic.yaml \
  --set secrets.slackBotToken="xoxb-..." \
  --set secrets.slackAppToken="xapp-..." \
  --set secrets.slackSigningSecret="..."
```

**Features**:
- Single replica
- Minimal resources
- No autoscaling
- Basic configuration

---

### 2. `production.yaml` - Production Deployment

Comprehensive production configuration with high availability and resource optimization.

**Use case**: Production environment with high availability requirements

**Deploy**:
```bash
helm install kslack ./chart -f examples/production.yaml \
  --namespace kagent \
  --create-namespace \
  --set secrets.slackBotToken="xoxb-..." \
  --set secrets.slackAppToken="xapp-..." \
  --set secrets.slackSigningSecret="..."
```

**Features**:
- Autoscaling (2-5 replicas)
- Pod anti-affinity for HA
- Node selectors and tolerations
- Production-grade resources
- Pod disruption budget
- Custom service account with IAM role

**Recommendations**:
- Use external secrets management (e.g., external-secrets, sealed-secrets)
- Configure monitoring and alerting
- Set up log aggregation
- Review resource limits based on your workload

---

### 3. `with-rbac.yaml` - With RBAC Permissions

Configuration demonstrating Slack user group-based RBAC for agent access control.

**Use case**: Organizations requiring fine-grained access control to specific agents

**Deploy**:
```bash
helm install kslack ./chart -f examples/with-rbac.yaml \
  --set secrets.slackBotToken="xoxb-..." \
  --set secrets.slackAppToken="xapp-..." \
  --set secrets.slackSigningSecret="..."
```

**Features**:
- Agent-level permissions
- Slack user group integration
- Custom denial messages
- User email allowlists

**Setup Steps**:

1. **Find Slack User Group IDs**:
   ```bash
   # In your Slack workspace, go to People & user groups
   # Click on a user group
   # The URL will show the group ID: /admin/user_groups/S0T8FCWSB
   ```

2. **Update permissions in values file**:
   ```yaml
   permissions:
     agent_permissions:
       kagent/k8s-agent:
         user_groups:
           - S0T8FCWSB  # Replace with your group ID
   ```

3. **Ensure bot has `usergroups:read` scope**:
   - Go to https://api.slack.com/apps
   - Select your app
   - Go to OAuth & Permissions
   - Verify `usergroups:read` is in Bot Token Scopes
   - Reinstall app if needed

---

## Common Patterns

### Using External Secrets

For production, use external secrets management:

```yaml
# Don't set secrets directly in values file
secrets:
  slackBotToken: ""
  slackAppToken: ""
  slackSigningSecret: ""

# Instead, create a Kubernetes secret separately
# Then reference it in your deployment
```

**Create secret**:
```bash
kubectl create secret generic kslack-secrets \
  --from-literal=slack-bot-token="xoxb-..." \
  --from-literal=slack-app-token="xapp-..." \
  --from-literal=slack-signing-secret="..." \
  --namespace kagent
```

### Environment-Specific Overrides

Combine base configuration with environment-specific overrides:

```bash
helm install kslack ./chart \
  -f examples/production.yaml \
  -f my-overrides.yaml
```

### Dry Run and Validation

Before deploying, validate your configuration:

```bash
# Render templates without installing
helm template kslack ./chart -f examples/production.yaml

# Validate syntax
helm lint ./chart -f examples/production.yaml

# Dry run
helm install kslack ./chart -f examples/production.yaml --dry-run
```

---

## Next Steps

After deployment:

1. **Verify installation**:
   ```bash
   kubectl get pods -n kagent -l app.kubernetes.io/name=kslack
   kubectl logs -f -n kagent -l app.kubernetes.io/name=kslack
   ```

2. **Test in Slack**:
   - Invite bot to channel: `/invite @kagent-bot`
   - Test: `@kagent-bot hello`
   - List agents: `/agents`

3. **Configure permissions** (if using RBAC):
   - Update user groups in values file
   - Upgrade deployment: `helm upgrade kslack ./chart -f examples/with-rbac.yaml`

4. **Monitor**:
   - Access metrics: `kubectl port-forward svc/kslack 8080:8080`
   - View metrics: `curl http://localhost:8080/metrics`

---

## Troubleshooting

### Bot doesn't respond
- Check logs: `kubectl logs -f -n kagent deployment/kslack`
- Verify Socket Mode connection in logs
- Ensure bot is invited to channel

### Permission denied errors
- Verify user group IDs are correct
- Check user is member of required group
- Ensure bot has `usergroups:read` scope

### High memory usage
- Review autoscaling settings
- Adjust resource limits
- Check for memory leaks in logs

---

## Additional Resources

- [kslack Documentation](../README.md)
- [Slack Setup Guide](../SLACK_SETUP.md)
- [Kagent Documentation](https://kagent.dev/docs)
- [Helm Chart Reference](../chart/README.md)
