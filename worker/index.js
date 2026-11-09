// GitHub sign-in for the Decap CMS editor at /admin.
// Static pages are served straight from assets; only /api/auth and /api/callback reach this code
// (see "run_worker_first" in wrangler.jsonc).
//
// Needs two Worker secrets, set in Cloudflare (Workers & Pages > microbiome-website > Settings > Variables and Secrets):
//   GITHUB_CLIENT_ID      from the GitHub OAuth App
//   GITHUB_CLIENT_SECRET  from the GitHub OAuth App

const STATE_COOKIE = "decap_oauth_state";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/api/auth") return startLogin(url, env);
    if (url.pathname === "/api/callback") return finishLogin(request, url, env);

    return env.ASSETS.fetch(request);
  },
};

function startLogin(url, env) {
  if (!env.GITHUB_CLIENT_ID) return text("GitHub sign-in is not configured yet (GITHUB_CLIENT_ID missing).", 500);
  const state = [...crypto.getRandomValues(new Uint8Array(16))].map((b) => b.toString(16).padStart(2, "0")).join("");
  const gh = new URL("https://github.com/login/oauth/authorize");
  gh.searchParams.set("client_id", env.GITHUB_CLIENT_ID);
  gh.searchParams.set("redirect_uri", `${url.origin}/api/callback`);
  gh.searchParams.set("scope", "repo,user");
  gh.searchParams.set("state", state);
  return new Response(null, {
    status: 302,
    headers: {
      Location: gh.href,
      "Set-Cookie": `${STATE_COOKIE}=${state}; Path=/api; HttpOnly; Secure; SameSite=Lax; Max-Age=600`,
    },
  });
}

async function finishLogin(request, url, env) {
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  const cookie = (request.headers.get("Cookie") || "").split(/;\s*/).find((c) => c.startsWith(STATE_COOKIE + "="));
  const expected = cookie ? cookie.split("=")[1] : null;

  if (!code || !state || state !== expected) {
    return popup("error", { message: "Sign-in could not be verified. Close this window and try again." }, url.origin);
  }

  const res = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: { "content-type": "application/json", accept: "application/json", "user-agent": "microbiome-recipes-cms" },
    body: JSON.stringify({
      client_id: env.GITHUB_CLIENT_ID,
      client_secret: env.GITHUB_CLIENT_SECRET,
      code,
      redirect_uri: `${url.origin}/api/callback`,
    }),
  });
  const result = await res.json();
  if (result.error || !result.access_token) {
    return popup("error", { message: result.error_description || "GitHub sign-in failed." }, url.origin);
  }
  return popup("success", { token: result.access_token, provider: "github" }, url.origin);
}

// The page Decap opens in a pop-up. It hands the result back to the editor window (same origin only).
function popup(status, content, origin) {
  const msg = JSON.stringify(`authorization:github:${status}:${JSON.stringify(content)}`);
  const html = `<!doctype html><html><body><p>${status === "success" ? "Signed in. You can close this window." : "Sign-in failed. You can close this window."}</p>
<script>
  (function () {
    var origin = ${JSON.stringify(origin)};
    function receive(e) {
      if (e.origin !== origin) return;
      window.opener.postMessage(${msg}, origin);
      window.removeEventListener("message", receive, false);
    }
    window.addEventListener("message", receive, false);
    window.opener && window.opener.postMessage("authorizing:github", origin);
  })();
</script></body></html>`;
  return new Response(html, {
    headers: {
      "content-type": "text/html;charset=UTF-8",
      "Set-Cookie": `${STATE_COOKIE}=; Path=/api; HttpOnly; Secure; SameSite=Lax; Max-Age=0`,
      "Cache-Control": "no-store",
    },
  });
}

function text(body, status) {
  return new Response(body, { status, headers: { "content-type": "text/plain;charset=UTF-8" } });
}
