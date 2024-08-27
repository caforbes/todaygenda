import os
import pugsql  # type: ignore


_this_dir = os.path.dirname(os.path.abspath(__file__))
_query_module_path = os.path.join(_this_dir, "queries")


def query_connect(url: str):
    queries = pugsql.module(_query_module_path)
    queries.connect(url)
    return queries
