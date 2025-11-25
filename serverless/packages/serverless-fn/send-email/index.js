const sgMail = require('@sendgrid/mail');

exports.main = async function(args) {
    // Check HTTP method
    const method = args.__ow_method;
    if (method !== 'POST' && method !== 'post') {
        return {
            statusCode: 405,
            body: JSON.stringify({ error: 'Method not allowed. Use POST.' })
        };
    }

    // Environment variables
    const SENDGRID_API_KEY = process.env.SENDGRID_API_KEY;
    const API_KEY = process.env.API_KEY;
    const SENDER_EMAIL = process.env.SENDER_EMAIL;
    const TO_EMAIL = process.env.TO_EMAIL;

    // Check API key
    const authHeader = args.__ow_headers && args.__ow_headers['authorization'];
    if (!API_KEY) {
        return {
            statusCode: 500,
            body: JSON.stringify({ error: 'API key not configured on server' })
        };
    }
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return {
            statusCode: 401,
            body: JSON.stringify({ error: 'Invalid or missing API key' })
        };
    }
    const token = authHeader.split(' ')[1];
    if (token !== API_KEY) {
        return {
            statusCode: 401,
            body: JSON.stringify({ error: 'Invalid or missing API key' })
        };
    }

    // Set SendGrid API key
    if (!SENDGRID_API_KEY) {
        return {
            statusCode: 500,
            body: JSON.stringify({ error: 'SendGrid API key not configured' })
        };
    }
    sgMail.setApiKey(SENDGRID_API_KEY);

    // Extract email fields
    const subject = args.subject;
    const text = args.text;
    const html = args.html;

    if (!subject || !text) {
        return {
            statusCode: 400,
            body: JSON.stringify({ error: 'subject and text are required' })
        };
    }

    const msg = {
        to: TO_EMAIL,
        from: SENDER_EMAIL,
        subject,
        text,
        html: html || undefined,
    };

    try {
        await sgMail.send(msg);
        return {
            statusCode: 200,
            body: JSON.stringify({ success: true, message: 'Email sent' })
        };
    } catch (err) {
        return {
            statusCode: 500,
            body: JSON.stringify({ error: 'Failed to send email', details: err.message })
        };
    }
}
