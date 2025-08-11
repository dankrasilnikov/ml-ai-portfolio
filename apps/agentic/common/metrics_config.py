from prometheus_client import Counter, Histogram, make_asgi_app


REQS = Counter("http_requests_total", "How many times the api was called", ["route"])
LAT = Histogram("http_requests_seconds", "Length of query in seconds", ["route"],
                buckets=(0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5))

