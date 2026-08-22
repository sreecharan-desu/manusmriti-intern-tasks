import nodemailer from "nodemailer";

const PLACEHOLDERS = new Set(["", "CHANGE_ME", "replace-me", "placeholder"]);

function secret(name) {
  const value = (process.env[name] || "").trim();
  return PLACEHOLDERS.has(value) ? "" : value;
}

export function mailConfigured() {
  const user = secret("EMAIL_USER");
  const pass = secret("EMAIL_PASS");
  return Boolean(user && pass && user.includes("@"));
}

function transporter() {
  const user = secret("EMAIL_USER");
  const pass = secret("EMAIL_PASS");
  if (!user || !pass) {
    throw new Error("EMAIL_USER and EMAIL_PASS are required");
  }
  const host = secret("SMTP_HOST") || "smtp.gmail.com";
  const port = Number(process.env.SMTP_PORT || 465);
  return nodemailer.createTransport({
    host,
    port,
    secure: port === 465,
    auth: { user, pass },
  });
}

export async function sendMail({ to, subject, text, html }) {
  if (!to || !subject || !text) {
    throw new Error("to, subject, and text are required");
  }
  const from = secret("EMAIL_FROM") || secret("EMAIL_USER");
  const info = await transporter().sendMail({
    from,
    to,
    subject,
    text,
    html: html || undefined,
  });
  return { ok: true, provider: "nodemailer", id: info.messageId || "" };
}
