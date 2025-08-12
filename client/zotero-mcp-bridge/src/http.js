(function() {
  // Minimal HTTP handler registration for Zotero platform is not available in plain WebExtensions.
  // This file documents the intended interface. Implementers can replace this with Zotero's platform APIs.
  // Intended endpoints (loopback only):
  //   GET  /zotero-mcp/v1/health -> { ok, state, version }
  //   POST /zotero-mcp/v1/init   -> { ok }  (accepts {token}) if state==uninitialized
  //   POST /zotero-mcp/v1/tag    -> { ok }  (accepts {itemKey, add[], remove[]})
  //   POST /zotero-mcp/v1/note   -> { ok }  (accepts {itemKey, content, mode, marker})
  // For now, we keep message-based stubs in background.js.
})();
