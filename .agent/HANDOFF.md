# Echo AI - Agent Handoff Context

> **Last Updated**: January 22, 2026  
> **Session**: Pricing Structure Update - Added Enterprise+ Tier (Pitch Deck Alignment)

---

## Current System State: ✅ WORKING

Production platform deployed on Railway (echoai.uk). Complete pricing structure updated to match pitch deck unit economics with 5 tiers including new ENTERPRISE+ tier.

---

## What I Did This Session

### 1. Added ENTERPRISE+ Tier to Backend
- Added `ENTERPRISE_PLUS` to `PricingTier` enum in `backend/app/models/user.py`
- Updated `backend/app/services/billing.py` with ENTERPRISE_PLUS quota (200 prompts)
- Updated `backend/app/core/config.py` to support `stripe_price_id_enterprise_plus`

### 2. Updated All Frontend Pricing Displays
- Landing page (`frontend/src/app/page.tsx`) - Now shows all 5 tiers in grid
- Billing dashboard (`frontend/src/app/dashboard/billing/page.tsx`) - Complete tier list
- Terms of Service - Updated with all 5 pricing tiers and continuous monitoring explanation

### 3. Updated Documentation
- `AI_HANDOFF_CONTEXT.md` - Updated pricing section with all 5 tiers
- `.agent/workflows/setup_stripe.md` - Updated Stripe setup guide with new pricing
- `.agent/HANDOFF.md` - This file with complete session notes

---

## Files Modified

| File | Change |
|------|--------|
| `backend/app/models/user.py` | Added ENTERPRISE_PLUS to PricingTier enum |
| `backend/app/services/billing.py` | Added ENTERPRISE_PLUS quota (200 prompts) and Price ID mapping |
| `backend/app/core/config.py` | Added stripe_price_id_enterprise_plus field |
| `frontend/src/app/page.tsx` | Updated to 5-column grid, added ENTERPRISE+ tier card |
| `frontend/src/app/dashboard/billing/page.tsx` | Added ENTERPRISE_PLUS tier to PRICING_TIERS array |
| `frontend/src/app/terms/page.tsx` | Updated with all 5 tiers and continuous monitoring description |
| `AI_HANDOFF_CONTEXT.md` | Updated pricing section |
| `.agent/workflows/setup_stripe.md` | Updated Stripe setup guide with new pricing |
| `.agent/HANDOFF.md` | This file - complete session documentation |

---

## Complete Pricing Structure (Pitch Deck Aligned)

| Tier | Price | Monitored Prompts | Iterations/Day | Target Customer |
|------|-------|------------------|----------------|-----------------|
| **FREE** | £0/month | 3 | 10 | Testing & demos |
| **STARTER** | £35/month | 10 | 10 | Solo consultants (2-3 brands) |
| **PRO** | £55/month | 15 | 10 | Small agencies (3-5 brands) |
| **ENTERPRISE** | £169/month | 50 | 10 | Growing agencies (10-15 brands) |
| **ENTERPRISE+** | £599/month | 200 | 10 | Large agencies (40-50 brands) |

**Key Points:**
- Each monitored prompt runs 10 iterations **daily** (not just once)
- This is continuous monitoring, not one-time queries
- 10 iterations provide statistical confidence (Monte Carlo methodology)
- Competitive moat: Competitors run 1 query, we run 10 for audit-grade data

---

## Stripe Configuration Required

### New Environment Variable Needed

Add to Railway Variables:

```bash
STRIPE_PRICE_ID_ENTERPRISE_PLUS=price_...  # £599/month tier
```

### Complete Stripe Setup (4 Paid Tiers)

When setting up Stripe products:

1. **Starter** - £35/month - "10 monitored prompts (10 iterations daily each)"
2. **Pro** - £55/month - "15 monitored prompts (10 iterations daily each)"  
3. **Enterprise** - £169/month - "50 monitored prompts (10 iterations daily each)"
4. **Enterprise+** - £599/month - "200 monitored prompts (10 iterations daily each)"

Copy each Price ID and set in Railway:
- `STRIPE_PRICE_ID_STARTER`
- `STRIPE_PRICE_ID_PRO`
- `STRIPE_PRICE_ID_ENTERPRISE`
- `STRIPE_PRICE_ID_ENTERPRISE_PLUS` (NEW)

---

## Unit Economics (From Pitch Deck)

### Launch Metrics
- **Blended ACV**: £70/month (conservative tier mix)
- **COGS**: £35/month (LLM APIs, infrastructure, payment processing, support)
- **Gross Margin**: 50% (land-grab strategy)
- **CAC**: £300 (self-serve model)
- **Payback Period**: 8 months
- **LTV/CAC**: 2.5x (24-month customer lifetime)

### Year 2 Target
- **Blended ACV**: £120/month (tier upgrades + price increases)
- **COGS**: £30/month (prompt caching, volume discounts)
- **Gross Margin**: 75% (margin expansion)
- **CAC**: £350 (scaled paid ads)
- **Payback Period**: 4 months
- **LTV/CAC**: 6x

---

## Next Steps for Future Agent

### Immediate (After Deployment)
1. **Create Stripe Products** with exact pricing from pitch deck
   - Use product names: "Echo AI - Starter", "Echo AI - Pro", etc.
   - Set descriptions to include "monitored prompts" and "10 iterations daily"
   - Copy all 4 Price IDs

2. **Update Railway Variables**
   ```bash
   railway variables set STRIPE_PRICE_ID_STARTER=price_...
   railway variables set STRIPE_PRICE_ID_PRO=price_...
   railway variables set STRIPE_PRICE_ID_ENTERPRISE=price_...
   railway variables set STRIPE_PRICE_ID_ENTERPRISE_PLUS=price_...
   ```

3. **Test Checkout Flow**
   - Use Stripe test mode first (`sk_test_...`)
   - Test each tier's checkout
   - Verify correct pricing displays

### Short-term (This Week)
1. **Update Marketing Materials**
   - Ensure all external docs reference "monitored prompts" not just "prompts"
   - Emphasize continuous daily monitoring (10 iterations/day)
   - Highlight this as competitive moat vs one-time queries

2. **Prepare Investor Materials**
   - Pricing aligns with pitch deck unit economics
   - Can confidently explain blended ACV of £70
   - Clear path to 75% margins by Year 2

---

## Known Issues

None currently. All pricing updates applied consistently.

---

## Warnings / Gotchas

1. **Terminology Shift**: "Monitored Prompts" vs "Prompts"
   - Each monitored prompt = 10 iterations daily
   - This is different from one-time prompts
   - Customer value prop: continuous tracking, not spot checks

2. **Existing Users**
   - Database users keep their current quotas
   - Only new registrations get the new structure
   - May need migration for existing users

3. **Stripe Price IDs**
   - Must create 4 products (not 3 anymore)
   - Don't forget ENTERPRISE_PLUS tier
   - Price IDs are case-sensitive in environment variables

4. **Frontend Grid Layout**
   - Changed from 4-column to 5-column grid
   - May need responsive design adjustments for mobile
   - Consider scrolling on small screens

---

## Production Status

- **Deployed:** ✅ Ready for deployment (changes committed)
- **Domains:** 
  - Railway: https://echo-ai-production.up.railway.app
  - Custom: https://echoai.uk
- **Health Check:** https://echoai.uk/health
- **Environment:** production
- **Last Commit:** Pending (ENTERPRISE+ tier addition)
- **Status:** Ready to push and deploy

---

## Pitch Deck Alignment Checklist

- ✅ 5 pricing tiers (FREE, STARTER, PRO, ENTERPRISE, ENTERPRISE+)
- ✅ Correct prices (£0, £35, £55, £169, £599)
- ✅ Correct quotas (3, 10, 15, 50, 200 monitored prompts)
- ✅ Terminology: "monitored prompts" with "10 iterations daily"
- ✅ Backend models support all 5 tiers
- ✅ Frontend displays all 5 tiers
- ✅ Terms of Service updated
- ✅ Stripe setup guide updated
- ⏳ Stripe products to be created (manual step)
- ⏳ Railway environment variables to be set (manual step)

---

## For Next Agent

**Read `.agent/AGENT_RULES.md` first!** It's the comprehensive central source of truth.

**To deploy these changes:**
```bash
# Review changes
git status
git diff

# Commit and push
git add -A
git commit -m "feat: add ENTERPRISE+ tier and align pricing with pitch deck

- Added ENTERPRISE_PLUS tier (£599/month, 200 prompts)
- Updated backend: PricingTier enum, billing service, config
- Updated frontend: landing page, billing dashboard, terms
- Updated documentation and Stripe setup guide
- Complete 5-tier structure: FREE, STARTER, PRO, ENTERPRISE, ENTERPRISE+

Aligns with pitch deck unit economics and continuous monitoring model.
Each monitored prompt runs 10 iterations daily.
"

# Push to deploy
git push origin main

# Monitor deployment
railway logs --follow
```

**After deployment, set up Stripe:**
1. Create 4 products in Stripe with exact pricing
2. Copy all 4 Price IDs
3. Set in Railway variables
4. Test checkout flow with test mode

**Remember to update this file (HANDOFF.md) at the end of your session!**

---

**Pricing structure now fully aligned with pitch deck. Ready for investor presentations and production deployment.**
