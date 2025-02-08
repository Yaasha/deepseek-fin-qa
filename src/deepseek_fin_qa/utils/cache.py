import hashlib
import json
from pathlib import Path


class ChatCache:
    """A class for caching chat queries and their corresponding values."""

    def __init__(self, path: Path) -> None:
        """Initialize the ChatCache object.

        Args:
            path (Path): The path to the cache file.

        """
        self.path = path

        if self.path.exists():
            with self.path.open("r") as file:
                self.cache = json.load(file)
        else:
            self.cache = {}

    def get(self, query: str) -> str | None:
        """Retrieve the cached value for a given query.

        Args:
            query (str): The query to retrieve the value for.

        Returns:
            str | None: The cached value if found, None otherwise.

        """
        key = hashlib.sha256(query.encode()).hexdigest()
        return self.cache.get(key)

    def set(self, query: str, value: str) -> None:
        """Set the cached value for a given query.

        Args:
            query (str): The query to set the value for.
            value (str): The value to be cached.

        """
        key = hashlib.sha256(query.encode()).hexdigest()
        self.cache[key] = value

        with self.path.open("w") as file:
            json.dump(self.cache, file)
