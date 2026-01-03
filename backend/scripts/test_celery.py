import asyncio
from backend.app.worker import celery_app

def test():
    print("Sending task...")
    # Inspect registered tasks
    i = celery_app.control.inspect()
    print(f"Registered tasks: {i.registered()}")
    
    # Send health check task
    res = celery_app.send_task("health_check")
    print(f"Task sent: {res.id}")
    try:
        val = res.get(timeout=5)
        print(f"Task result: {val}")
    except Exception as e:
        print(f"Task timed out or failed: {e}")

if __name__ == "__main__":
    test()
