import logging
import requests

from fastmcp import Context, FastMCP


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("my_custom_logger")

class CustomLogger:
    def info(self, *args, **kwargs):
        logger.info(*args, **kwargs)
    
    def error(self, *args, **kwargs):
        logger.error(*args, **kwargs)


class PokeApi:
    url: str = "https://pokeapi.co/api/v2/"

    def __make_request(
        self, endpoint: str = "pokemon", verb: str = "GET", **kwargs
    ) -> dict:
        url: str = f"{self.url}{endpoint}"
        response: requests.Response = requests.request(verb, url, timeout=30, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_pokemon(self, offset: int = 20, limit: int = 20) -> dict:
        params: dict = {"offset": offset, "limit": limit}
        return self.__make_request(endpoint="pokemon", params=params)


mcp = FastMCP("PokeMCP", version="0.0.1")


@mcp.tool()
def get_pokemon(offset: int, limit: int, ctx: Context) -> dict:
    logging.info(f"Getting pokemon with offset={offset} and limit={limit}")
    logging.info(f"Context: {ctx}")
    pokemon_service: PokeApi = PokeApi()
    return pokemon_service.get_pokemon(offset=offset, limit=limit)


if __name__ == "__main__":
    mcp.run(transport="http")
