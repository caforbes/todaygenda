import os
import pugsql  # type: ignore


_this_dir = os.path.dirname(os.path.abspath(__file__))
_query_module_path = os.path.join(_this_dir, "queries")


class DBQueriesWrapper(pugsql.compiler.Module):
    pass


def query_connect(url: str) -> DBQueriesWrapper:
    queries = pugsql.module(_query_module_path)
    queries.connect(url)
    return queries
