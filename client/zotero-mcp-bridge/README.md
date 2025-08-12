Zotero MCP Write Bridge (Plugin)

Status: experimental scaffold. This plugin will expose a minimal local interface inside Zotero to safely write tags and notes using Zotero's Client JavaScript API (no direct sqlite writes).

What it does (goal)
- POST-like actions for:
  - tag upsert/remove on an item
  - note upsert/replace on an item (idempotent via a marker)
- health/init handshake: one-time token, then token-required access
- loopback only; runs when Zotero is open

Current state
- WebExtension manifest and background script with storage and message-based stubs
- Handlers: health, init, and placeholder tag/note message routes
- HTTP endpoint layer not yet implemented (requires Zotero-specific APIs beyond pure WebExtensions)

Install (dev)
1) Build: currently just load the folder into Zotero's Add-ons (Tools → Add-ons → cog → Install Add-on From File…) after you zip the folder contents.
2) After install, restart Zotero if prompted.

Handshake from MCP (planned)
- `zotero-mcp write-bridge init` will probe for the plugin, then POST a random shared token to the plugin's init endpoint. The plugin will store it and require `X-ZMCP-Token` for future calls.

Development notes
- Directory:
  - `manifest.json` — WebExtension manifest
  - `src/background.js` — background script (message handlers, token storage)
- We will add a thin HTTP layer using Zotero's internal APIs in a follow-up step. For now, message handlers allow quick validation of storage and basic routing.
