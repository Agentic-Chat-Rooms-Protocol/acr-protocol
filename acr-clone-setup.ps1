# ACR Fusion Workspace - PowerShell 5.1 compatible
$ErrorActionPreference = "Stop"

$Root = Join-Path $HOME "acr-fusion-workspace"
New-Item -ItemType Directory -Force -Path $Root | Out-Null
Set-Location $Root

$Dirs = @(
    "01-session-identity",
    "02-mcp-tool-skeleton",
    "03-did-vc-identity",
    "04-human-bridge-cli",
    "05-message-bus",
    "06-service-topology-ref",
    "07-acp-registry-clients",
    "vendor-notes"
)
foreach ($d in $Dirs) {
    New-Item -ItemType Directory -Force -Path (Join-Path $Root $d) | Out-Null
}

function Clone-Repo {
    param(
        [string]$Url,
        [string]$Dest
    )
    Write-Host "Cloning $Url -> $Dest"
    git clone --depth 1 $Url $Dest
    if ($LASTEXITCODE -ne 0) {
        throw "git clone failed for $Url"
    }
}

Clone-Repo "https://github.com/a2aproject/a2a-python.git" "01-session-identity\a2a-python"
Clone-Repo "https://github.com/appboypov/group-chat-mcp.git" "02-mcp-tool-skeleton\group-chat-mcp"
Clone-Repo "https://gitee.com/WeBank/WeIdentity.git" "03-did-vc-identity\WeIdentity"
Clone-Repo "https://github.com/Open-ACP/OpenACP.git" "04-human-bridge-cli\OpenACP"
Clone-Repo "https://github.com/rivulet-io/hub.git" "05-message-bus\hub"
Clone-Repo "https://github.com/mjaracz/poll-vote-counter.git" "06-service-topology-ref\poll-vote-counter"
Clone-Repo "https://github.com/Cosmos-Sapiens/openacp-telegram-adapter.git" "07-acp-registry-clients\openacp-telegram-adapter"
Clone-Repo "https://github.com/Cosmos-Sapiens/openacp-whatsapp-adapter.git" "07-acp-registry-clients\openacp-whatsapp-adapter"
Clone-Repo "https://github.com/Cosmos-Sapiens/openacp-mattermost-adapter.git" "07-acp-registry-clients\openacp-mattermost-adapter"
Clone-Repo "https://github.com/Cosmos-Sapiens/openacp-signal-adapter.git" "07-acp-registry-clients\openacp-signal-adapter"
Clone-Repo "https://github.com/norwayforthemoon/OpenACP-Cowork.git" "07-acp-registry-clients\OpenACP-Cowork"
Clone-Repo "https://github.com/xiwan/acp-bridge.git" "07-acp-registry-clients\acp-bridge"
Clone-Repo "https://github.com/agentclientprotocol/agent-client-protocol.git" "07-acp-registry-clients\agent-client-protocol"

$FusionMapContent = @'
01-session-identity/a2a-python/src/a2a/{server,client,auth,migrations} -> ACR session/roster/audit persistence
02-mcp-tool-skeleton/group-chat-mcp/src/{schemas,services,hooks,index.ts} -> ACR MCP tool surface (swap services/ backend to hub)
03-did-vc-identity/WeIdentity -> DID issuance + selective-disclosure VC engine for buddy/capability credentials
04-human-bridge-cli/OpenACP/{core.ts,agent-instance.ts} -> Human dashboard/CLI core; add new RoomChannelAdapter
05-message-bus/hub/{hub.go,jetstream.go,kv_store.go,object_store.go,auth.go,core.go} -> durable pub/sub + object store
06-service-topology-ref/poll-vote-counter -> DDD/NATS/Postgres/SSE/OTel scaffold for Room Engine service
07-acp-registry-clients/* -> platform adapter templates, multi-agent mesh references, ACP core spec
'@

Set-Content -Path (Join-Path $Root "vendor-notes\FUSION_MAP.md") -Value $FusionMapContent -Encoding UTF8

Write-Host "ACR fusion workspace ready at $Root"
Get-ChildItem -Path $Root -Recurse -Depth 1 -Directory | Select-Object FullName | Sort-Object FullName
