# Email Setup Instructions

To enable sending meeting minutes to participants via email, you need to configure SMTP email settings.

## Quick Setup with Gmail (Recommended)

### Step 1: Get a Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** in the left sidebar
3. Enable **2-Step Verification** if not already enabled
4. Go to **App passwords** (search for it in the Security page)
5. Select **Mail** and **Other (Custom name)**
6. Name it "Meeting Minutes App"
7. Click **Generate**
8. Copy the 16-character password (it will look like: `xxxx xxxx xxxx xxxx`)

### Step 2: Add Secrets in Replit

1. Click the **🔒 Secrets** icon in the left sidebar
2. Add these secrets:

   **Secret 1:**
   - Key: `SMTP_USER`
   - Value: `your.email@gmail.com` (your full Gmail address)

   **Secret 2:**
   - Key: `SMTP_PASSWORD`
   - Value: `xxxx xxxx xxxx xxxx` (the 16-character app password from Step 1)

   **Secret 3:**
   - Key: `FROM_EMAIL`
   - Value: `your.email@gmail.com` (same as SMTP_USER)

   **Secret 4:**
   - Key: `FROM_NAME`
   - Value: `AI Meeting Minutes` (or any name you want to appear in emails)

3. Restart your application

### Step 3: Test It Out

1. Upload a meeting audio file
2. In the **Participants** field, include email addresses like:
   ```
   John Doe john@example.com, Jane Smith jane@example.com
   ```
3. After processing, click **"Send to Participants"** button
4. Participants will receive:
   - A nicely formatted HTML email
   - Meeting summary in the email body
   - PDF attachment with full meeting minutes

---

## Alternative: Use Other Email Services

### Outlook/Office 365

Add these secrets:
- `SMTP_HOST`: `smtp.office365.com`
- `SMTP_PORT`: `587`
- `SMTP_USER`: `your.email@outlook.com`
- `SMTP_PASSWORD`: `your-password`
- `FROM_EMAIL`: `your.email@outlook.com`

### Yahoo Mail

Add these secrets:
- `SMTP_HOST`: `smtp.mail.yahoo.com`
- `SMTP_PORT`: `587`
- `SMTP_USER`: `your.email@yahoo.com`
- `SMTP_PASSWORD`: `your-app-password` (generate from Yahoo Account Security)
- `FROM_EMAIL`: `your.email@yahoo.com`

### Custom SMTP Server

Add these secrets:
- `SMTP_HOST`: Your SMTP server address
- `SMTP_PORT`: Your SMTP port (usually 587 or 465)
- `SMTP_USER`: Your SMTP username
- `SMTP_PASSWORD`: Your SMTP password
- `FROM_EMAIL`: The email address to send from

---

## Troubleshooting

### "Email service not configured" error
- Make sure you've added `SMTP_USER` and `SMTP_PASSWORD` secrets
- Restart the application after adding secrets

### "Authentication failed" error
- For Gmail: Make sure you're using an App Password, not your regular password
- Check that your email and password are correct
- Ensure 2-Step Verification is enabled for Gmail

### "No valid email addresses found" error
- Make sure to include email addresses in the Participants field
- Format: `Name email@example.com` or just `email@example.com`
- Multiple participants: separate with commas

### Email not received
- Check spam/junk folder
- Verify the email addresses are correct
- Check Replit logs for any error messages

---

## Email Format

Participants will receive:

**Subject:** Meeting Minutes: [Meeting Title]

**Body:**
- Professional HTML-formatted email with your meeting summary
- Clean, easy-to-read layout with company branding
- Full meeting details including date and participants

**Attachment:**
- PDF file with complete meeting minutes
- Includes full transcript and summary
- Ready to archive or forward

---

## Local Development

If running locally, set environment variables:

**Windows:**
```batch
set SMTP_USER=your.email@gmail.com
set SMTP_PASSWORD=your-app-password
set FROM_EMAIL=your.email@gmail.com
```

**Mac/Linux:**
```bash
export SMTP_USER=your.email@gmail.com
export SMTP_PASSWORD=your-app-password
export FROM_EMAIL=your.email@gmail.com
```
