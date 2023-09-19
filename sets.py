class Item:
    def __init__(self, set_: 'Set', value):
        self.set = set_
        self.value = value
    
    def __call__(self, foreign: 'Set') -> 'ForeignSet':
        return ForeignSet(self, foreign)
    
    def __eq__(self, other: 'Item') -> 'Relation':
        if self.set == other.set:
            raise Exception(f'Cannot create equality constraint on two items of same set {self} == {other}')
        return Relation(self, other, 'eq')
    
    def __ne__(self, other: 'Item') -> 'Relation':
        if self.set == other.set:
            raise Exception(f'Cannot create inequality constraint on two items of same set {self} != {other}')
        return Relation(self, other, 'ne')
    
    def __lt__(self, other: 'Item') -> 'Relation':
        if self.set == other.set:
            raise Exception(f'Cannot create comparative constraint on two items of same set {self} < {other}')
        if not isinstance(other.set, OrderedSet):
            raise Exception(f'Cannot create comparative constraint on an unordered right hand side {self} < {other}')
        return Relation(self, other, 'lt')
    
    def __le__(self, other: 'Item') -> 'Relation':
        if self.set == other.set:
            raise Exception(f'Cannot create comparative constraint on two items of same set {self} <= {other}')
        if not isinstance(other.set, OrderedSet):
            raise Exception(f'Cannot create comparative constraint on an unordered right hand side {self} <= {other}')
        return Relation(self, other, 'le')
    
    def __gt__(self, other: 'Item') -> 'Relation':
        if self.set == other.set:
            raise Exception(f'Cannot create comparative constraint on two items of same set {self} > {other}')
        if not isinstance(other.set, OrderedSet):
            raise Exception(f'Cannot create comparative constraint on an unordered right hand side {self} > {other}')
        return Relation(self, other, 'gt')
    
    def __ge__(self, other: 'Item') -> 'Relation':
        if self.set == other.set:
            raise Exception(f'Cannot create comparative constraint on two items of same set {self} >= {other}')
        if not isinstance(other.set, OrderedSet):
            raise Exception(f'Cannot create comparative constraint on an unordered right hand side {self} >= {other}')
        return Relation(self, other, 'ge')

    def __repr__(self) -> str:
        return f'{self.set.name}[{self.value}]'
        

class ForeignSet:
    def __init__(self, item: Item, set_: 'Set'):
        self.item = item
        self.set = set_

    def __eq__(self, other: 'ForeignSet') -> 'Relation':
        if self.set != other.set:
            raise Exception(f'Cannot create equality constraint on two different foreign sets {self} == {other}')
        # since no item may be shared, this actually means that the two native items must correspond, resulting in a normal item equality (immediate relation)
        return Relation(self.item, other.item, 'eq')
    
    def __ne__(self, other: 'ForeignSet') -> 'Relation':
        if self.set != other.set:
            raise Exception(f'Cannot create equality constraint on two different foreign sets {self} != {other}')
        # since no item may be shared, this actually means that the two native items must be disjoint, resulting in a normal item inequality (immediate relation)
        return Relation(self.item, other.item, 'ne')

    def __lt__(self, other: 'ForeignSet') -> 'Relation':
        if self.set != other.set:
            raise Exception(f'Cannot create comparative constraint on two different foreign sets {self} < {other}')
        # since no item may be shared, this additionally means that the two native items must be disjoint, resulting in an additional item inequality (immediate relation)
        return [Relation(self, other, 'lt'), Relation(self.item, other.item, 'ne')]
    
    def __le__(self, other: 'ForeignSet') -> 'Relation':
        if self.set != other.set:
            raise Exception(f'Cannot create comparative constraint on two different foreign sets {self} <= {other}')
        # since no item may be shared, this additionally means that the two native items must be disjoint, resulting in an additional item inequality (immediate relation)
        return [Relation(self, other, 'le'), Relation(self.item, other.item, 'ne')]
    
    def __gt__(self, other: 'ForeignSet') -> 'Relation':
        if self.set != other.set:
            raise Exception(f'Cannot create comparative constraint on two different foreign sets {self} > {other}')
        # since no item may be shared, this additionally means that the two native items must be disjoint, resulting in an additional item inequality (immediate relation)
        return [Relation(self, other, 'gt'), Relation(self.item, other.item, 'ne')]
    
    def __ge__(self, other: 'ForeignSet') -> 'Relation':
        if self.set != other.set:
            raise Exception(f'Cannot create comparative constraint on two different foreign sets {self} >= {other}')
        # since no item may be shared, this additionally means that the two native items must be disjoint, resulting in an additional item inequality (immediate relation)
        return [Relation(self, other, 'ge'), Relation(self.item, other.item, 'ne')]

    def __repr__(self) -> str:
        return f'{self.item.set.name}[{self.item.value}]({self.set.name})'

RELATION_TYPES = {'eq': '==', 'ne': '!=', 'lt': '<', 'le': '<=', 'gt': '>', 'ge': '>='}

class Relation:
    def __init__(self, a: Item, b: Item, ty: str) -> None:
        self.a = a
        self.b = b
        self.ty = ty

    def __repr__(self) -> str:
        return f'{self.a} {RELATION_TYPES[self.ty]} {self.b}'
    
    def evalulate_immediate(self, super_sets):
        if isinstance(self.a, ForeignSet):
            raise Exception(f'Cannot only evaluate foreign relation recurringly')
        set_ab = super_sets[self.a.set.name].foreign_sets[self.a.value].foreigns[self.b.set.name]
        if self.ty == 'eq':
            set_ab.clear()
            set_ab.append(self.b.value)
            super_sets[self.b.set.name].foreign_sets[self.b.value].foreigns[self.a.set.name] = [self.a.value]
        elif self.ty == 'ne':
            set_ab.remove(self.b.value)
            super_sets[self.b.set.name].foreign_sets[self.b.value].foreigns[self.a.set.name].remove(self.a.value)
        elif self.ty == 'gt':
            i = set_ab.index(self.b.value)
            for _ in range(i + 1):
                k = set_ab.pop(0)
                super_sets[self.b.set.name].foreign_sets[k].foreigns[self.a.set.name].remove(self.a.value)
        elif self.ty == 'ge':
            i = set_ab.index(self.b.value)
            for _ in range(i):
                k = set_ab.pop(0)
                super_sets[self.b.set.name].foreign_sets[k].foreigns[self.a.set.name].remove(self.a.value)
        elif self.ty == 'lt':
            i = set_ab.index(self.b.value)
            for _ in range(len(set_ab) - i):
                k = set_ab.pop()
                super_sets[self.b.set.name].foreign_sets[k].foreigns[self.a.set.name].remove(self.a.value)
        elif self.ty == 'le':
            i = set_ab.index(self.b.value)
            for _ in range(len(set_ab) - i - 1):
                k = set_ab.pop()
                super_sets[self.b.set.name].foreign_sets[k].foreigns[self.a.set.name].remove(self.a.value)
        else:
            Exception(f'Invalid or unreachable immediate relation type `{self.ty}`')
    
    def evalulate_recurring(self, super_sets):
        if isinstance(self.a, Item):
            raise Exception(f'Cannot only evaluate item relation immediately')
        set_a = super_sets[self.a.item.set.name].foreign_sets[self.a.item.value].foreigns[self.a.set.name]
        set_b = super_sets[self.b.item.set.name].foreign_sets[self.b.item.value].foreigns[self.b.set.name]
        if self.ty == 'gt':
            m = min(set_b)
            while set_a[0] <= m:
                k = set_a.pop(0)
                if self.a.item.value in super_sets[self.a.set.name].foreign_sets[k].foreigns[self.a.item.set.name]:
                    super_sets[self.a.set.name].foreign_sets[k].foreigns[self.a.item.set.name].remove(self.a.item.value)
            m = max(set_a)
            while set_b[-1] >= m:
                k = set_b.pop()
                if self.b.item.value in super_sets[self.b.set.name].foreign_sets[k].foreigns[self.b.item.set.name]:
                    super_sets[self.b.set.name].foreign_sets[k].foreigns[self.b.item.set.name].remove(self.b.item.value)
        elif self.ty == 'ge':
            m = min(set_b)
            while set_a[0] < m:
                k = set_a.pop(0)
                if self.a.item.value in super_sets[self.a.set.name].foreign_sets[k].foreigns[self.a.item.set.name]:
                    super_sets[self.a.set.name].foreign_sets[k].foreigns[self.a.item.set.name].remove(self.a.item.value)
            m = max(set_a)
            while set_b[-1] > m:
                k = set_b.pop()
                if self.b.item.value in super_sets[self.b.set.name].foreign_sets[k].foreigns[self.b.item.set.name]:
                    super_sets[self.b.set.name].foreign_sets[k].foreigns[self.b.item.set.name].remove(self.b.item.value)
        elif self.ty == 'lt':
            m = max(set_b)
            while set_a[-1] >= m:
                k = set_a.pop()
                if self.a.item.value in super_sets[self.a.set.name].foreign_sets[k].foreigns[self.a.item.set.name]:
                    super_sets[self.a.set.name].foreign_sets[k].foreigns[self.a.item.set.name].remove(self.a.item.value)
            m = min(set_a)
            while set_b[0] <= m:
                k = set_b.pop(0)
                if self.b.item.value in super_sets[self.b.set.name].foreign_sets[k].foreigns[self.b.item.set.name]:
                    super_sets[self.b.set.name].foreign_sets[k].foreigns[self.b.item.set.name].remove(self.b.item.value)
        elif self.ty == 'le':
            m = max(set_b)
            while set_a[-1] > m:
                k = set_a.pop()
                if self.a.item.value in super_sets[self.a.set.name].foreign_sets[k].foreigns[self.a.item.set.name]:
                    super_sets[self.a.set.name].foreign_sets[k].foreigns[self.a.item.set.name].remove(self.a.item.value)
            m = min(set_a)
            while set_b[0] < m:
                k = set_b.pop(0)
                if self.b.item.value in super_sets[self.b.set.name].foreign_sets[k].foreigns[self.b.item.set.name]:
                    super_sets[self.b.set.name].foreign_sets[k].foreigns[self.b.item.set.name].remove(self.b.item.value)
        else:
            Exception(f'Invalid or unreachable recurring relation type `{self.ty}`')

class Set:
    def __init__(self, name: str, items: list):
        self.name = name
        self.items = items
    
    def __getitem__(self, item) -> Item:
        if item in self.items:
            return Item(self, item)
        raise KeyError
    
    def copy(self) -> 'Set':
        return Set(self.name, self.items.copy())

    def __repr__(self) -> str: 
        return f'{self.name}: {{{", ".join(str(i) for i in self.items)}}}'

class OrderedSet(Set):
    def __init__(self, name: str, items: list):
        super().__init__(name, sorted(items))

    def copy(self) -> 'OrderedSet':
        return OrderedSet(self.name, self.items.copy())

    def __repr__(self) -> str:
        return f'{self.name}: {{{" < ".join(str(i) for i in self.items)}}}'