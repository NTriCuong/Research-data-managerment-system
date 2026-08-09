from functools import lru_cache

from elasticsearch import Elasticsearch

from app.core.config import settings


def create_elasticsearch_client() -> Elasticsearch:
    options: dict = {
        "basic_auth": (settings.ELASTIC_USERNAME, settings.ELASTIC_PASSWORD),
        "verify_certs": settings.ELASTIC_VERIFY_CERTS,
        "request_timeout": settings.ELASTIC_REQUEST_TIMEOUT_SECONDS,
    }
    if settings.ELASTIC_CA_CERT:
        options["ca_certs"] = str(settings.ELASTIC_CA_CERT)
    return Elasticsearch(settings.ELASTIC_HOST, **options)


@lru_cache(maxsize=1)
def get_elasticsearch_client() -> Elasticsearch:
    return create_elasticsearch_client()
