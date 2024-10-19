import os


class Greeter:
    def greet(self):
        print("Hi")


def hello_world():
    message = "Hello, world!"
    greeter = Greeter()
    greet_func = getattr(greeter, "greet")
    greet_func()


if __name__ == "__main__":
    hello_world()
