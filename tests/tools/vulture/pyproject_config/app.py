class App:
    def get(self, path: str):
        return lambda func: func

    def post(self, path: str):
        return lambda func: func


app = App()


@app.get("/items")
def read_items():
    return []


@app.post("/items")
def create_item():
    return {}


def keep_me():
    return 1


def truly_unused():
    return 2
