(function() {
  const TOKEN_PREF_KEY = "zoteroMcpBridge.token";
  const STATE_PREF_KEY = "zoteroMcpBridge.state"; // uninitialized|ready

  function getZoteroPrefs() {
    // Zotero provides a preferences API via Services.prefs in the chrome scope.
    // In a minimal first pass, we fallback to browser.storage.local for token storage.
    const storage = browser && browser.storage && browser.storage.local;
    return {
      async getToken() {
        const obj = await storage.get(TOKEN_PREF_KEY);
        return obj[TOKEN_PREF_KEY] || null;
      },
      async setToken(token) {
        await storage.set({ [TOKEN_PREF_KEY]: token });
        await storage.set({ [STATE_PREF_KEY]: "ready" });
      },
      async getState() {
        const obj = await storage.get(STATE_PREF_KEY);
        return obj[STATE_PREF_KEY] || "uninitialized";
      },
      async reset() {
        await storage.remove(TOKEN_PREF_KEY);
        await storage.set({ [STATE_PREF_KEY]: "uninitialized" });
      }
    };
  }

  // Very small HTTP server shim is not available in WebExtensions.
  // Instead, we rely on Zotero's built-in HTTP server registration via Components (XPCOM) in full add-ons.
  // For now, we expose minimal message passing placeholder to validate packaging.

  // Placeholder: respond to a simple ping via runtime message
  browser.runtime.onMessage.addListener(async (msg) => {
    if (msg && msg.type === "zotero-mcp-bridge.health") {
      const prefs = getZoteroPrefs();
      const state = await prefs.getState();
      const token = await prefs.getToken();
      return { ok: true, state, tokenPresent: !!token };
    }
    if (msg && msg.type === "zotero-mcp-bridge.init" && msg.token) {
      const prefs = getZoteroPrefs();
      const state = await prefs.getState();
      if (state !== "uninitialized") {
        return { ok: false, error: "already-initialized" };
      }
      await prefs.setToken(msg.token);
      return { ok: true };
    }
  });
})();
