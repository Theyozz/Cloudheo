"""Rate limiting for unauthenticated, abusable endpoints (login, register).

In-memory storage — fine for a single backend process; would need a shared
backend (e.g. Redis) behind `storage_uri` if Cloudheo ever runs multiple
API processes/workers.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
