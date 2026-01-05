---
description: Deploy the Echo AI application to Railway
---

1. Link your local project to the Railway project (if not already linked) or ensure you are in the correct directory.
   ```bash
   cd /Users/hamid/Documents/ai-visibility
   # If not linked yet:
   # railway link -p 83f16003-87ba-455b-bfaf-7e1fb639344c
   ```

2. Deploy the service using the Railway CLI. This will trigger a new build with the updated Dockerfile.
   ```bash
   railway up --service echo-ai --detach
   ```

3. Monitor the deployment logs to ensure the build succeeds and the health check passes.
   ```bash
   railway logs --service echo-ai
   ```

4. Once the service is healthy (Active), run the database migrations.
   ```bash
   railway run alembic upgrade head
   ```

5. Verify the deployment.
   ```bash
   railway domain
   curl $(railway domain)/health
   ```
