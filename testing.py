class Foo:
    def __init__(self, v):
        self.v = v

    def __eq__(self, other):
        return f'{self.v} {other.v}'


a = Foo(1)
b = Foo(2)

print(a == b)