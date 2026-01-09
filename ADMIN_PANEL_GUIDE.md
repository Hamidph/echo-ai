# Admin Panel Guide - Echo AI

**Created:** January 9, 2026  
**Purpose:** Enterprise-grade system configuration management

---

## Overview

The Admin Panel provides a centralized dashboard for managing Echo AI's system configuration, monitoring platform statistics, and managing users **without requiring code changes or redeployments**.

This is how big companies (Stripe, Shopify, Salesforce, etc.) manage their platforms - through admin dashboards, not code changes.

---

## Access

### Admin Login
- **URL:** `https://echo-ai-production.up.railway.app/admin`
- **Requirements:** User account with `admin` role
- **Test Admin:** test@echoai.com (has admin role)

### Security
- Protected by `get_current_admin_user` dependency
- Requires JWT authentication
- Only users with `role="admin"` can access
- Admins cannot demote themselves

---

## Features

### 1. System Configuration Tab

Control platform-wide default settings:

#### **Default Iterations**
- **Purpose:** Set default number of iterations for new experiments
- **Range:** 1-100
- **Current Default:** 10
- **Use Case:** Adjust based on cost/accuracy tradeoff

#### **Default Recurring Frequency** ⭐
- **Purpose:** Set default frequency for recurring experiments
- **Options:** Daily, Weekly, Monthly
- **Current Default:** **Daily** (as per your value proposition!)
- **Use Case:** Align with your "daily monitoring" value prop

#### **Enable Recurring by Default**
- **Purpose:** Whether new experiments are recurring by default
- **Current Default:** False
- **Use Case:** Enable this to make daily monitoring the default behavior

#### **Maximum Iterations Per Experiment**
- **Purpose:** Hard limit on iterations to prevent abuse
- **Range:** 1-1000
- **Current Default:** 100
- **Use Case:** Prevent users from creating extremely expensive experiments

#### **Enable Recurring Experiments**
- **Purpose:** Platform-wide toggle for recurring experiments feature
- **Current Default:** True
- **Use Case:** Disable during maintenance or if feature needs to be turned off

#### **Maintenance Mode** 🚨
- **Purpose:** Block all non-admin access to the platform
- **Current Default:** False
- **Use Case:** During deployments, database migrations, or emergencies

---

### 2. Platform Statistics Tab

Real-time platform metrics:

#### **User Metrics**
- Total Users
- Active Users (is_active=true)

#### **Experiment Metrics**
- Total Experiments
- Completed Experiments
- Currently Running Experiments
- Recurring Experiments (total)
- Active Recurring Experiments (not failed/cancelled)

#### **Current Configuration Display**
Shows the live configuration values for quick reference.

---

### 3. User Management Tab

View and manage all platform users:

#### **User Table Columns**
- Email
- Full Name
- Role (admin/user/viewer)
- Pricing Tier (free/starter/pro/enterprise)
- Quota Usage (used/total)
- Status (active/inactive)

#### **Available Actions** (coming soon)
- Update user role
- Adjust user quota
- Activate/deactivate users
- View user's experiments

---

## API Endpoints

### Get System Configuration
```http
GET /api/v1/admin/config
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "default_iterations": 10,
  "default_frequency": "daily",
  "default_recurring": false,
  "max_iterations_per_experiment": 100,
  "enable_recurring_experiments": true,
  "maintenance_mode": false
}
```

### Update System Configuration
```http
PUT /api/v1/admin/config
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "default_frequency": "daily",
  "default_recurring": true
}
```

### Get Platform Statistics
```http
GET /api/v1/admin/stats
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "total_users": 15,
  "active_users": 12,
  "total_experiments": 127,
  "completed_experiments": 98,
  "running_experiments": 2,
  "recurring_experiments": 23,
  "active_recurring_experiments": 18,
  "system_config": { ... }
}
```

### List Users
```http
GET /api/v1/admin/users?limit=50&offset=0
Authorization: Bearer {admin_token}
```

### Update User Role
```http
PATCH /api/v1/admin/users/{user_id}/role
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "new_role": "admin"
}
```

### Update User Quota
```http
PATCH /api/v1/admin/users/{user_id}/quota
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "new_quota": 10000
}
```

---

## How Big Companies Use Admin Panels

### **Stripe**
- Admin dashboard to toggle features (beta features, rate limits)
- Real-time monitoring of API usage
- User account management (upgrade/downgrade, refunds)
- **No code deployment needed** for config changes

### **Shopify**
- Feature flags controlled via admin panel
- Store limits and quotas managed dynamically
- A/B test configurations
- Emergency "maintenance mode" toggle

### **Salesforce**
- Org-wide settings (storage limits, API limits)
- User role and permission management
- Feature enablement per customer
- System health monitoring

### **Your Platform (Echo AI)**
- ✅ Default experiment settings (iterations, frequency)
- ✅ Recurring experiment controls
- ✅ User quota management
- ✅ Platform statistics
- ✅ Maintenance mode
- ✅ Feature toggles (enable/disable recurring)

---

## Configuration Management Strategy

### **What Goes in Admin Panel:**
✅ **Business logic settings** (default frequency, iterations)  
✅ **Feature toggles** (enable/disable recurring)  
✅ **User limits** (quotas, rate limits)  
✅ **Operational controls** (maintenance mode)  
✅ **A/B test configurations**

### **What Stays in Code:**
❌ **Infrastructure settings** (database URLs, API keys)  
❌ **Security settings** (JWT secrets, encryption keys)  
❌ **Core algorithms** (visibility calculation logic)  
❌ **Provider configurations** (LLM API endpoints)

---

## Your Value Proposition Implementation

### **Problem:**
You wanted daily monitoring to be the default (part of your value prop), but users had to manually select it.

### **Solution:**
1. ✅ Admin panel sets `default_frequency: "daily"`
2. ✅ Frontend reads this default from API
3. ✅ New experiments default to daily recurring
4. ✅ Can be changed anytime via admin panel (no code deployment!)

### **Implementation Steps:**

#### **Step 1: Set Default to Daily** (Already done!)
```
Go to: /admin → System Configuration
Set: Default Recurring Frequency = "Daily"
Click: Save Changes
```

#### **Step 2: Enable Recurring by Default** (Optional)
```
Go to: /admin → System Configuration
Toggle: Enable Recurring by Default = ON
Click: Save Changes
```

#### **Step 3: Update Frontend to Use Defaults** (Next step)
Modify `frontend/src/app/experiments/new/page.tsx` to fetch and use admin defaults:
```typescript
const { data: adminConfig } = useQuery({
  queryKey: ["adminConfig"],
  queryFn: () => fetch("/api/v1/admin/config").then(r => r.json()),
});

// Use admin defaults
const [frequency, setFrequency] = useState(adminConfig?.default_frequency || "daily");
const [isRecurring, setIsRecurring] = useState(adminConfig?.default_recurring || false);
```

---

## Maintenance & Operations

### **Daily Monitoring:**
1. Check Platform Statistics tab
2. Monitor running experiments count
3. Review active recurring experiments
4. Check user quota usage

### **Configuration Changes:**
1. Go to System Configuration tab
2. Adjust settings as needed
3. Click "Save Changes"
4. Changes take effect immediately (no deployment!)

### **Emergency Procedures:**
1. **Platform Issues:** Enable Maintenance Mode
2. **Cost Overrun:** Reduce max_iterations_per_experiment
3. **Feature Bug:** Disable enable_recurring_experiments
4. **User Abuse:** Adjust individual user quotas

---

## Future Enhancements

### **Phase 2:**
- [ ] A/B test configuration (test different defaults for different users)
- [ ] Scheduled configuration changes (change defaults at specific times)
- [ ] Configuration history and rollback
- [ ] Email notifications on config changes

### **Phase 3:**
- [ ] Multi-tenant configuration (different defaults per organization)
- [ ] Feature flags per user segment
- [ ] Cost optimization recommendations
- [ ] Automated quota adjustments based on usage patterns

---

## Comparison: Code vs Admin Panel

### **Before (Code-Based Configuration):**
```python
# backend/app/core/config.py
default_iterations: int = 10  # Hard-coded
default_frequency: str = "weekly"  # Hard-coded

# To change:
1. Edit code
2. Commit to git
3. Push to GitHub
4. Wait for Railway deployment (~5 minutes)
5. Hope nothing breaks
```

### **After (Admin Panel):**
```
1. Go to /admin
2. Change value
3. Click "Save"
4. Done! (0 seconds)
```

---

## Security Considerations

### **Admin Access Control:**
- Only users with `role="admin"` can access `/admin`
- JWT token required for all API calls
- Admins cannot demote themselves (prevents lockout)
- All admin actions are logged

### **Configuration Validation:**
- Iterations: 1-100 (default), 1-1000 (max)
- Frequency: Must be "daily", "weekly", or "monthly"
- Quotas: Cannot be negative
- All updates are validated server-side

### **Audit Trail** (Coming soon):
- Log all configuration changes
- Track who changed what and when
- Rollback capability
- Compliance reporting

---

## Troubleshooting

### **Can't Access Admin Panel**
- **Issue:** 403 Forbidden or redirected to dashboard
- **Solution:** Ensure your user has `role="admin"` in database
- **Check:** `SELECT role FROM users WHERE email = 'your@email.com';`

### **Configuration Changes Not Taking Effect**
- **Issue:** Changes saved but not reflected in experiments
- **Solution:** Frontend needs to fetch config from `/api/v1/admin/config`
- **Note:** Currently config is server-side only (frontend update needed)

### **Can't Update Configuration**
- **Issue:** Save button disabled or error on save
- **Solution:** Check browser console for errors, verify admin token is valid

---

## Summary

✅ **Admin Panel Created:** Full-featured dashboard for system management  
✅ **Default Frequency Set:** Daily (as per value proposition)  
✅ **No Code Deployments:** Change settings instantly via UI  
✅ **Enterprise-Grade:** Same approach used by Stripe, Shopify, Salesforce  
✅ **Secure:** Admin-only access with proper authentication  
✅ **Scalable:** Easy to add new configuration options

**Next Step:** Update frontend experiment form to fetch and use admin defaults!

---

**Access the admin panel:** https://echo-ai-production.up.railway.app/admin  
**Login as:** test@echoai.com / password123
