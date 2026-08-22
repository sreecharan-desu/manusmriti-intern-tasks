import { mailConfigured, sendMail } from "../src/send.js";

function json(res, status, body) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json");
  res.setHeader("Cache-Control", "no-store");
  res.end(JSON.stringify(body));
}

function authorized(req) {
  const secret = (process.env.MAIL_API_SECRET || "").trim();
  if (!secret) return true;
  return (req.headers.authorization || "") === `Bearer ${secret}`;
}

function pathOf(req) {
  try {
    return new URL(req.url || "/", "http://localhost").pathname;
  } catch {
    return req.url || "/";
  }
}

export default async function handler(req, res) {
  const path = pathOf(req);
  if (req.method === "GET" && (path === "/" || path === "/health" || path === "/api" || path === "/api/health")) {
    json(res, 200, { ok: true, provider: "nodemailer", configured: mailConfigured() });
    return;
  }

  if (req.method !== "POST" || (path !== "/mail" && path !== "/api" && path !== "/api/mail" && path !== "/")) {
    json(res, 405, { ok: false, error: "method not allowed" });
    return;
  }

  if (!authorized(req)) {
    json(res, 401, { ok: false, error: "unauthorized" });
    return;
  }

  const body = typeof req.body === "object" && req.body ? req.body : {};
  try {
    const result = await sendMail({
      to: body.to,
      subject: body.subject,
      text: body.text,
      html: body.html,
    });
    json(res, 200, result);
  } catch (error) {
    json(res, 502, { ok: false, error: error.message || "send failed" });
  }
}
