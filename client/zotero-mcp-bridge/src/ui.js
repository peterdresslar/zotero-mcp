(function() {
  // Minimal options UI to show/reset token state (optional; platform-specific integration TBD)
  const TOKEN_PREF_KEY = "zoteroMcpBridge.token";
  const STATE_PREF_KEY = "zoteroMcpBridge.state";
  const storage = browser && browser.storage && browser.storage.local;

  async function getState() {
    const obj = await storage.get(STATE_PREF_KEY);
    return obj[STATE_PREF_KEY] || "uninitialized";
  }

  async function reset() {
    await storage.remove(TOKEN_PREF_KEY);
    await storage.set({ [STATE_PREF_KEY]: "uninitialized" });
  }

  // Expose simple commands via runtime messages for now
  browser.runtime.onMessage.addListener(async (msg) => {
    if (!msg || !msg.type) return;
    if (msg.type === "zotero-mcp-bridge.reset") {
      await reset();
      return { ok: true };
    }
    if (msg.type === "zotero-mcp-bridge.state") {
      return { state: await getState() };
    }
  });
})();
