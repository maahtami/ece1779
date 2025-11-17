import express from "express";
import bodyParser from "body-parser";
import sgMail from "@sendgrid/mail";

const app = express();
app.use(express.json());

// Authentication middleware: checks API key for all endpoints except /stats
const authMiddleware = (req, res, next) => {
  // Check if process.env.API_KEY is set; if not, respond with 500 and { error: "API key not configured on server" }
    const apiKey = process.env.API_KEY;
    if (!apiKey) {
    return res.status(500).json({ error: "API key not configured on server" });
  }
  // Verify Authorization header contains Bearer <API_KEY>
    const authHeader = req.headers['authorization'];
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: "Invalid or missing API key" });
  }
  // If header is missing or incorrect, respond with 401 and { error: "Invalid or missing API key" }
    const token = authHeader.split(' ')[1];
    if (token !== apiKey) {
    return res.status(401).json({ error: "Invalid or missing API key" });
  }
  // 5. Call next() if authentication passes
    next();
};

// Apply authentication middleware to all routes
app.use(authMiddleware);

// Set your SendGrid API key
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

// POST /send-email
app.post("/send-email", async (req, res) => {
  try {
    const { to, subject, text, html } = req.body;

    if (!subject || !text) {
      return res.status(400).json({ error: "to, subject, and text are required" });
    }

    const msg = {
      to: process.env.TO_EMAIL, // recipient email from environment variable
      from: process.env.SENDER_EMAIL, // verified sender
      subject,
      text,
      html: html || undefined,
    };

    await sgMail.send(msg);

    return res.json({ success: true, message: "Email sent" });
  } catch (err) {
    console.error("SendGrid error:", err);
    return res.status(500).json({ error: "Failed to send email" });
  }
});

// Health check
app.get("/", (req, res) => res.send("Email function running"));

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Server running on port ${port}`));
