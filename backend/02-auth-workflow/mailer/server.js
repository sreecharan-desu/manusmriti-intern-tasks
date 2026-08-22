import http from "node:http";
import { mailConfigured, sendMail } from "./src/send.js";

const PORT = Number(process.env.PORT || 8010);
const HOST = process.env.HOST || (process.env.VERCEL ? "0.0.0.0" : "127.0.0.1");

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (chunk) => chunks.push(chunk));
    req.on("end", () => {
      if (!chunks.length) {
        resolve({});
        return;
      }
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString("utf8")));
      } catch (error) {
        reject(error);
      }
    });
    req.on("error", reject);
  });
}

function json(res, status, body) {
  res.writeHead(status, { "Content-Type": "application/json", "Cache-Control": "no-store" });
  res.end(JSON.stringify(body));
}

const server = http.createServer(async (req, res) => {
  const path = new URL(req.url || "/", "http://localhost").pathname;
  if (req.method === "GET" && (path === "/" || path === "/health")) {
    json(res, 200, { ok: true, provider: "nodemailer", configured: mailConfigured() });
    return;
  }
  if (req.method === "POST" && path === "/mail") {
    const secret = (process.env.MAIL_API_SECRET || "").trim();
    if (secret && req.headers.authorization !== `Bearer ${secret}`) {
      json(res, 401, { ok: false, error: "unauthorized" });
      return;
    }
    try {
      const body = await readBody(req);
      json(res, 200, await sendMail(body));
    } catch (error) {
      json(res, 502, { ok: false, error: error.message || "send failed" });
    }
    return;
  }
  json(res, 404, { ok: false, error: "not found" });
});

server.listen(PORT, HOST, () => {
  process.stdout.write(`auth mailer on http://${HOST}:${PORT}\n`);
});
