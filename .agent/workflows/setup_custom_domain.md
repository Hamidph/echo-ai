---
description: How to setup a custom domain for the application using Railway and Cloudflare/Squarespace
---

1. **Purchase Domain**
   - Buy a domain from a registrar (Cloudflare, Namecheap, Google Domains/Squarespace).

2. **Configure Railway Service**
   - Navigate to the [Railway Project Dashboard](https://railway.app/dashboard).
   - Open the `echo-ai` (or `backend`) service.
   - Go to **Settings** -> **Networking**.
   - Under **Custom Domain**, enter the domain (e.g., `www.echoai.uk`).
   - Click **Add Domain**.
   - **Critical**: Copy the "Value/Target" provided by Railway (e.g., `b3bnuah4.up.railway.app`).

3. **Configure DNS Records**
   - Log in to your DNS provider (e.g., Cloudflare).
   - Add a `CNAME` record:
     - **Type**: `CNAME`
     - **Name**: `www` (or `app`)
     - **Target**: Paste the value from Railway.
     - **Proxy Status** (Cloudflare): Proxied (Orange Cloud) is recommended.
   - Save the record.

4. **Verify DNS Propagation**
   - Wait for the status in Railway Networking to turn Green (`Cloudflare proxy detected`).

5. **Update Environment Variables**
   - In Railway, go to the **Variables** tab of the `echo-ai` service.
   - Add or Update `NEXT_PUBLIC_API_URL`:
     - Value: `https://YOUR_DOMAIN` (e.g., `https://www.echoai.uk`).
   - Add or Update `FRONTEND_URL`:
     - Value: `https://YOUR_DOMAIN`.

6. **Redeploy Service**
   - Go to the **Deployments** tab in Railway.
   - Click **Redeploy** on the latest commit to apply the environment variables.

7. **Verification**
   - Visit the new domain.
   - Verify the site loads and API requests (Network tab) are directed to the new domain.
