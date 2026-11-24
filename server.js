const http = require("http");
const fs = require("fs");
const path = require("path");
const PORT = Number(process.env.PORT || 3000);
const ROOT = __dirname;
const MIME_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8"
};
function sendJson(res, status, data) {
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
  });
  res.end(JSON.stringify(data));
}
const server = http.createServer((req, res) => {
  if (req.method === "OPTIONS") {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    });
    return res.end();
  }
  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  if (req.method === "GET" && url.pathname === "/api/health") {
    res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
    return res.end(JSON.stringify({ ok: true, message: "VDF Games backend běží." }));
  }
  if (req.method === "POST" && url.pathname === "/chat") {
    let body = "";
    req.on("data", chunk => {
      body += chunk;
      if (body.length > 1_000_000) {
        sendJson(res, 413, { error: "Požadavek je příliš velký." });
        req.destroy();
      }
    });
    req.on("end", () => {
      let payload;
      try {
        payload = JSON.parse(body || "{}");
      } catch {
        return sendJson(res, 400, { error: "Neplatný JSON." });
      }
      const message = typeof payload.message === "string" ? payload.message.trim() : "";
      const student = typeof payload.student === "string" ? payload.student : "Neznámý student";
      const email = typeof payload.email === "string" ? payload.email : null;
      if (!message) {
        return sendJson(res, 400, { error: "Napiš prosím dotaz." });
      }
      // Lokální demonstrační odpověď. Bez AI/API klíče nejde o skutečnou AI podporu.
      return sendJson(res, 200, {
        reply:
          "Lokální backend funguje!\n\n" +          "Student: " + student + "\n" +
          "Přijatý dotaz: " + message +
          (email ? "\nE-mail: " + email : "") +
          "\n\nToto je testovací odpověď. Pro skutečné AI odpovědi je potřeba připojit AI API."
      });
    });
    return;
  }
  if (req.method === "GET" && (url.pathname === "/" || url.pathname === "/index.html")) {
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    return fs.createReadStream(path.join(ROOT, "index.html")).pipe(res);
  }
  if (req.method === "GET" && ["/style.css", "/script.js"].includes(url.pathname)) {
    const filePath = path.join(ROOT, url.pathname.slice(1));
    return fs.createReadStream(filePath)
      .on("error", () => {
        res.writeHead(404);
        res.end("Soubor nenalezen.");
      })
      .on("open", () => {
        res.writeHead(200, { "Content-Type": MIME_TYPES[path.extname(filePath)] });
      })
      .pipe(res);
  }
  sendJson(res, 404, { error: "Endpoint nenalezen." });
});
server.listen(PORT, "0.0.0.0", () => {
  console.log(`VDF Games backend běží na http://0.0.0.0:${PORT}`);
  console.log(`Web otevři na http://localhost:${PORT}`);
  console.log(`Test serveru: http://localhost:${PORT}/api/health`);
});
 