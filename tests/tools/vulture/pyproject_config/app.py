from collections.abc import Callable


class App:
    def get(self, _path: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
        return lambda func: func

    def post(self, _path: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
        return lambda func: func


app = App()


@app.get("/items")
def read_items() -> list[object]:
    return []


@app.post("/items")
def create_item() -> dict[str, object]:
    return {}


def keep_me() -> int:
    return 1


def truly_unused() -> int:
    return 2
