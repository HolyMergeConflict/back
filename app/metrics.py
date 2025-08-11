from prometheus_client import Counter, Histogram

REQUESTS = Counter(
    "http_requests_total", "Total HTTP requests", ["method","route","status_family"]
)
TASKS_CREATED = Counter("tasks_created_total", "Tasks created", ["subject","difficulty"])
AUTH_LOGINS   = Counter("auth_login_total", "Auth login attempts", ["result"])
RECO_LATENCY  = Histogram("recommendation_latency_seconds", "Reco latency",
                          buckets=(0.01,0.05,0.1,0.2,0.5,1,2))

def status_family(code: int) -> str:
    return f"{code//100}xx"