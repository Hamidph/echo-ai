---
description: How to setup Stripe for billing and subscriptions
---

1. **Business Profile & Public Details**
   - **Industry/Category**: Software > SaaS
   - **Website**: `https://www.echoai.uk`
   - **Product Description**: "AI analytics platform helping brands measure visibility in LLM responses."
   - **Statement Descriptor**: `ECHO AI`
   - **Short Descriptor**: `ECHOAI`
   - **Customer Support Website**: `https://www.echoai.uk`

2. **Create Products (Tiers)**
   - Go to **Product Catalog** -> **Add Product**.
   - Create the following 3 products (Recurring, Monthly):

   | Product Name | Price (Monthly) | Description |
   | :--- | :--- | :--- |
   | **Starter** | £25 (example) | 5,000 Prompts / Month |
   | **Pro** | £80 (example) | 50,000 Prompts / Month |
   | **Enterprise** | £400 (example) | 1,000,000 Prompts / Month |

   - **Important**: After creating each, copy the **Price ID** (starts with `price_...`).

3. **Get API Keys**
   - Click the **Developers** tab (usually at the top right of the dashboard).
   - Go to **API keys**.
   - Copy the **Secret key** (`sk_live_...` or `sk_test_...`).

4. **Setup Webhook (Workbench)**
   - Go to the **Webhooks** tab (you are already there).
   - Click **Add destination** (or "Add endpoint").
   - **Endpoint URL**: `https://www.echoai.uk/api/v1/billing/webhook`
   - **Select events**:
     - `checkout.session.completed`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
   - Click **Add destination**.
   - **Reveal Signing Secret**: Click "Reveal" on the signing secret (top right) and copy it (`whsec_...`).

5. **Update Railway Variables**
   - Go to Railway -> `echo-ai` service -> **Variables**.
   - Add/Update the following:
     - `STRIPE_API_KEY`: (Your Secret Key)
     - `STRIPE_WEBHOOK_SECRET`: (Your Webhook Signing Secret)
     - `STRIPE_PRICE_ID_STARTER`: (Price ID for Starter)
     - `STRIPE_PRICE_ID_PRO`: (Price ID for Pro)
     - `STRIPE_PRICE_ID_ENTERPRISE`: (Price ID for Enterprise)

6.  **Redeploy**
    - Redeploy the service for changes to take effect.
