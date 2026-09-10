# Private Local AI Infrastructure & Second Brain

**`local-ai-second-brain`** is a fully offline, high-performance RAG and agentic workflow stack for Fedora Linux. It keeps inference, retrieval, and personal knowledge on hardware you control, providing complete data sovereignty with zero subscription costs.

The stack combines local LLM inference, a vector-backed knowledge workspace, an indexed Obsidian vault, encrypted remote access, and custom agent skills for browsing files, searching the web, scraping pages, and retrieving documents.

## Goals

- **Zero data leakage:** process private prompts, documents, and embeddings locally by default.
- **No recurring API costs:** use open-weight models and self-hosted services.
- **Reliable retrieval:** turn an Obsidian vault of 200+ Markdown notes into a searchable second brain.
- **Secure remote access:** reach local services from trusted devices without public port forwarding.
- **Practical agent execution:** combine document retrieval, filesystem access, and real-time web research.
- **Hardware-aware operation:** tune context and memory usage so 7B models run smoothly within 16 GB of RAM.

## Architecture

```text
                    Tailscale WireGuard mesh
             +----------------------------------+
             |                                  |
  Mobile/Desktop clients -------- Fedora host   |
                                      |         |
                              +-------+--------+|
                              |                ||
                         Ollama :11434   AnythingLLM :3001
                         Qwen2.5 1.5B/7B       |
                                              |
                                      Obsidian Markdown vault
                                      embedded/indexed knowledge
```

### Request flow

1. A trusted desktop or mobile client connects to the Fedora host over the Tailscale mesh.
2. AnythingLLM receives the chat or agent request and performs retrieval against the indexed knowledge base.
3. AnythingLLM sends the prompt and relevant context to Ollama.
4. Ollama runs a local Qwen2.5 model and returns the response without requiring a hosted LLM API.
5. Optional agent skills browse approved files, query the web, scrape documents, or write results back to the local workspace.

Only Tailscale should expose these services beyond the host. Do **not** forward ports `11434` or `3001` from your router to the public internet.

## Technology stack

| Area | Technology | Role |
| --- | --- | --- |
| Operating system | Fedora Linux | Host operating system and service platform |
| LLM engine | Ollama | Local model runtime and API |
| Models | Qwen2.5 1.5B and 7B | Fast and higher-quality local inference profiles |
| RAG and vector database | AnythingLLM | Workspace management, embeddings, retrieval, and chat |
| Knowledge base | Obsidian | Human-maintained Markdown notes; 200+ notes indexed |
| Networking | Tailscale / WireGuard | Encrypted device-to-device access |
| Automation | Custom agent skills | Web search, filesystem hooks, web scraping, and retrieval |

## Repository structure

The repository contains reproducible configuration, scripts, and documentation. Keep private notes, model files, credentials, and generated indexes outside Git.

```text
.
+-- configs/                # Service and model configuration templates
+-- docs/                   # Architecture, operations, and security documentation
+-- scripts/                # Setup, health-check, backup, and maintenance scripts
+-- .gitignore              # Excludes secrets, local state, and generated data
+-- LICENSE
+-- README.md
```

Suggested local-only paths:

```text
~/ai/
+-- models/                 # Ollama-managed model data
+-- anythingllm/            # AnythingLLM application data and workspaces
+-- vault/                  # Obsidian vault; back up independently
```

## Prerequisites

- A current Fedora Linux installation with administrator access.
- At least 16 GB RAM; SSD storage is strongly recommended.
- Enough free disk space for the selected models, embeddings, and vault backups.
- An Obsidian vault containing Markdown notes.
- A Tailscale account and one tailnet for the devices that need access.

Commands below assume Bash and a user with `sudo` access.

## Installation

### 1. Update Fedora and install utilities

```bash
sudo dnf upgrade --refresh -y
sudo dnf install -y curl git jq policycoreutils-python-utils
```

### 2. Install and configure Ollama

Install Ollama using its official installer:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Enable the service and verify it is running:

```bash
sudo systemctl enable --now ollama
systemctl --no-pager --full status ollama
curl http://127.0.0.1:11434/api/tags
```

Pull the two recommended model profiles:

```bash
ollama pull qwen2.5:1.5b
ollama pull qwen2.5:7b
```

Run a smoke test:

```bash
ollama run qwen2.5:1.5b "Reply with: local inference is working"
```

#### Ollama tuning for 16 GB RAM

Use the smaller model for quick classification, short lookups, and mobile workflows. Use the 7B model for longer reasoning and retrieval-heavy tasks. Keep one large model loaded at a time and start with a conservative context window:

```bash
sudo systemctl edit ollama
```

Add:

```ini
[Service]
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_CONTEXT_LENGTH=4096"
```

Then reload the service:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

Increase the context length only after checking memory pressure with `free -h` and `systemd-cgtop`. Larger contexts consume substantially more RAM and can cause swapping.

By default, Ollama listens on `127.0.0.1:11434`. Keep that binding unless remote clients must call Ollama directly. If direct tailnet access is required, bind deliberately to the tailnet interface or a controlled address and enforce access with Tailscale ACLs and host firewall rules.

### 3. Install AnythingLLM

Download the Fedora-compatible desktop or self-hosted package from the [AnythingLLM releases page](https://github.com/Mintplex-Labs/anything-llm/releases), then install the downloaded RPM according to the release instructions.

For a local package installation:

```bash
sudo dnf install -y ./anythingllm-*.rpm
```

Start AnythingLLM and open its local interface:

```text
http://127.0.0.1:3001
```

In AnythingLLM:

1. Select **Ollama** as the LLM provider.
2. Set the Ollama base URL to `http://127.0.0.1:11434`.
3. Select `qwen2.5:7b` as the default model.
4. Use `qwen2.5:1.5b` for a lower-memory or lower-latency workspace.
5. Configure the embedding provider supported by your AnythingLLM version. Prefer a local embedding model when available to preserve the local-only property.
6. Create a workspace for the Obsidian vault.
7. Import or connect the vault directory and run ingestion.
8. Confirm that representative notes are retrievable before enabling agent tools.

AnythingLLM stores workspace state, vector data, and configuration in its application data directory. Back up that directory together with the source vault, but never commit it if it contains private notes or credentials.

### 4. Install Tailscale

Install Tailscale using the official Fedora repository setup:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo systemctl enable --now tailscaled
sudo tailscale up
```

Confirm that the Fedora host and trusted clients are connected:

```bash
tailscale status
tailscale ip -4
```

From an enrolled client, open AnythingLLM using the host's tailnet address or MagicDNS name:

```text
http://<fedora-host-name>:3001
```

If Ollama is intentionally exposed to the tailnet, use:

```text
http://<fedora-host-name>:11434
```

Keep access limited to your tailnet. Use Tailscale ACLs, device approval, and `tailscale lock` where appropriate for your threat model. Do not replace Tailscale authentication with an unauthenticated public listener.

### 5. Connect and validate the stack

Run these checks on the Fedora host:

```bash
curl -fsS http://127.0.0.1:11434/api/tags >/dev/null
curl -I http://127.0.0.1:3001
tailscale status
free -h
```

Then validate end to end:

1. Ask AnythingLLM a question whose answer exists in an Obsidian note.
2. Confirm the response includes the expected retrieved context.
3. Switch between the 1.5B and 7B models and compare latency and quality.
4. Connect from a second trusted device over Tailscale.
5. Verify that no router port-forwarding rules are present for `11434` or `3001`.

## Agent skills and permissions

Custom skills may provide:

- **Filesystem browsing:** inspect approved directories and retrieve local documents.
- **File system hooks:** trigger indexing or workflows when notes change.
- **Web search:** fetch current information when local knowledge is insufficient.
- **Web scraping:** extract readable content for local analysis.
- **Document retrieval:** search the Obsidian vault and AnythingLLM workspaces.

Treat agent tools as privileged automation. Use explicit allowlists for directories, avoid granting write access to the vault unless required, keep secrets outside indexed paths, and review scraped content before storing it in the knowledge base. Web access is the only non-local data path in this design; disable web skills for strictly offline operation.

## Security and privacy model

- Local inference and retrieval are the default.
- Tailscale encrypts traffic between enrolled devices; it does not make an untrusted device trusted.
- Keep AnythingLLM authentication enabled and use unique credentials.
- Do not index `.env` files, SSH keys, browser profiles, tokens, or other secrets.
- Restrict filesystem skills to the smallest useful directory set.
- Keep the Fedora host patched and review active Tailscale devices regularly.
- Back up the Obsidian vault and AnythingLLM state to encrypted storage.
- Assume web search and scraping can disclose query intent and selected URLs; disable those skills when confidentiality is more important than freshness.

## Operations

Useful diagnostics:

```bash
systemctl --no-pager --full status ollama tailscaled
journalctl -u ollama -n 100 --no-pager
tailscale status
ss -ltnp | grep -E ':(11434|3001)\b'
free -h
df -h
```

If inference becomes slow, check for swapping first, reduce the context window, stop unused model processes, and run only one large model at a time. If retrieval quality drops, re-index the affected workspace and verify that the vault path, file extensions, and embedding configuration are correct.

## Backups

Back up both:

1. The source Obsidian vault.
2. AnythingLLM workspace and configuration data, including vector indexes if rebuilding them is expensive.

Use encrypted backup storage and test restoration periodically. Model files can generally be re-downloaded and do not need to be included in every backup.

## License

See [LICENSE](LICENSE) for the repository license. Model, AnythingLLM, Ollama, Tailscale, and Obsidian usage remains subject to each project's respective license and terms.
