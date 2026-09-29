// iPhone 2007 Replay as a Cloudflare Worker.
// Each request includes only the headlines whose replay time has passed,
// so readers pick each one up on their next check after it is due.
// Nothing runs between requests.
import DATA from "./data.js";

const fill = (text, values) =>
  Object.entries(values).reduce((s, [k, v]) => s.split(k).join(v), text);

const escapeHtml = (s) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

export function render(pathname, origin, now) {
  const site = origin + "/";
  const released = DATA.items.filter((i) => i.t <= now).reverse(); // newest first
  const next = DATA.items.find((i) => i.t > now);
  const lastModified = new Date(released.length ? released[0].t : DATA.items[0].t - 86400000);

  if (pathname === "/feed.xml" || pathname === "/feed" || pathname === "/rss") {
    const body =
      fill(DATA.head, { __SITE__: escapeHtml(site), __LASTBUILD__: lastModified.toUTCString() }) +
      released.map((i) => i.xml).join("") +
      DATA.tail;
    return { status: 200, type: "application/rss+xml; charset=utf-8", body, lastModified };
  }
  if (pathname === "/" || pathname === "/index.html") {
    const total = DATA.items.length;
    const status = next
      ? `${released.length} of ${total} headlines released. Next one ${next.next}.`
      : `All ${total} headlines released. The replay is over.`;
    const rows = released.map((i) => i.html).join("") || "<li>Nothing released yet.</li>\n";
    const body = fill(DATA.page, { __SITE__: escapeHtml(site), __STATUS__: escapeHtml(status), __ROWS__: rows });
    return { status: 200, type: "text/html; charset=utf-8", body, lastModified };
  }
  return { status: 404, type: "text/plain; charset=utf-8", body: "Not found\n", lastModified };
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const r = render(url.pathname, url.origin, Date.now());
    const headers = {
      "content-type": r.type,
      "cache-control": "public, max-age=300",
      "last-modified": r.lastModified.toUTCString(),
    };
    const since = Date.parse(request.headers.get("if-modified-since") || "");
    if (r.status === 200 && since && Math.floor(r.lastModified / 1000) <= Math.floor(since / 1000)) {
      return new Response(null, { status: 304, headers });
    }
    return new Response(request.method === "HEAD" ? null : r.body, { status: r.status, headers });
  },
};
