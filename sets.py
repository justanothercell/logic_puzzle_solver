from typing import Callable, Any
from itertools import combinations

RELATION_TYPES = {'eq': '==', 'ne': '!=', 'lt': '<', 'le': '<=', 'gt': '>', 'ge': '>='}

class Item:
    def relation(self, other: 'Item', call: Callable, op: str):
        if self.listing:
            if op == 'eq':
                raise Exception('Cannot relate multiple items to one with equality')
            return [call(item, other) for item in self.listing]
        if other.listing:
            if op == 'eq':
                raise Exception('Cannot relate multiple items to one with equality')
            return [call(self, item) for item in other.listing]
        if self.set == other.set:
            raise Exception(f'Cannot create constraint on two items of same set {self} {RELATION_TYPES[op]} {other}')
        return Relation(self, other, op)
        
    def __init__(self, set_: 'Set', value, listing = None):
        self.set = set_
        self.value = value
        self.listing = listing
    
    def __call__(self, foreign: 'Set') -> 'ForeignSet':
        return ForeignSet(self, foreign)
    
    def __and__(self, other: 'Set') -> 'Set':
        listing = []
        if self.listing:
            listing += self.listing
        else:
            listing.append(self)
        if other.listing:
            listing += other.listing
        else:
            listing.append(other)
        return Item(None, None, listing=listing)
    
    def __eq__(self, other: 'Item') -> 'Relation':
        return self.relation(other, lambda a, b: a == b, 'eq')
    
    def __ne__(self, other: 'Item') -> 'Relation':
        return self.relation(other, lambda a, b: a != b, 'ne')
    
    def __lt__(self, other: 'Item') -> 'Relation':
        if not isinstance(other.set, OrderedSet):
            raise Exception(f'Cannot create comparative constraint on an unordered right hand side {self} < {other}')
        return self.relation(other, lambda a, b: a < b, 'lt')
    
    def __le__(self, other: 'Item') -> 'Relation':
        if not isinstance(other.set, OrderedSet):
            raise Exception(f'Cannot create comparative constraint on an unordered right hand side {self} <= {other}')
        return self.relation(other, lambda a, b: a <= b, 'le')
    
    def __gt__(self, other: 'Item') -> 'Relation':
        if not isinstance(other.set, OrderedSet):
            raise Exception(f'Cannot create comparative constraint on an unordered right hand side {self} > {other}')
        return self.relation(other, lambda a, b: a > b, 'gt')
    
    def __ge__(self, other: 'Item') -> 'Relation':
        if not isinstance(other.set, OrderedSet):
            raise Exception(f'Cannot create comparative constraint on an unordered right hand side {self} >= {other}')
        return self.relation(other, lambda a, b: a >= b, 'ge')

    def __repr__(self) -> str:
        return f'{self.set.name}[{self.value}]'
        

class ForeignSet:
    def __init__(self, item: Item, set_: 'Set'):
        self.item = item
        self.set = set_

    def __eq__(self, other: 'ForeignSet|Any') -> 'Relation':
        if not isinstance(other, ForeignSet):
            return self.item == self.set[other]
        if self.set != other.set:
            raise Exception(f'Cannot create equality constraint on two different foreign sets {self} == {other}')
        # since no item may be shared, this actually means that the two native items must correspond, resulting in a normal item equality (immediate relation)
        return Relation(self.item, other.item, 'eq')
    
    def __ne__(self, other: 'ForeignSet|Any') -> 'Relation':
        if not isinstance(other, ForeignSet):
            return self.item != self.set[other]
        if self.set != other.set:
            raise Exception(f'Cannot create equality constraint on two different foreign sets {self} != {other}')
        # since no item may be shared, this actually means that the two native items must be disjoint, resulting in a normal item inequality (immediate relation)
        return Relation(self.item, other.item, 'ne')

    def __lt__(self, other: 'ForeignSet|Any') -> 'Relation':
        if not isinstance(other, ForeignSet):
            return self.item < self.set[other]
        if self.set != other.set:
            raise Exception(f'Cannot create comparative constraint on two different foreign sets {self} < {other}')
        # since no item may be shared, this additionally means that the two native items must be disjoint, resulting in an additional item inequality (immediate relation)
        return [Relation(self, other, 'lt'), Relation(self.item, other.item, 'ne')]
    
    def __le__(self, other: 'ForeignSet|Any') -> 'Relation':
        if not isinstance(other, ForeignSet):
            return self.item <= self.set[other]
        if self.set != other.set:
            raise Exception(f'Cannot create comparative constraint on two different foreign sets {self} <= {other}')
        # since no item may be shared, this additionally means that the two native items must be disjoint, resulting in an additional item inequality (immediate relation)
        return [Relation(self, other, 'le'), Relation(self.item, other.item, 'ne')]
    
    def __gt__(self, other: 'ForeignSet|Any') -> 'Relation':
        if not isinstance(other, ForeignSet):
            return self.item > self.set[other]
        if self.set != other.set:
            raise Exception(f'Cannot create comparative constraint on two different foreign sets {self} > {other}')
        # since no item may be shared, this additionally means that the two native items must be disjoint, resulting in an additional item inequality (immediate relation)
        return [Relation(self, other, 'gt'), Relation(self.item, other.item, 'ne')]
    
    def __ge__(self, other: 'ForeignSet|Any') -> 'Relation':
        if not isinstance(other, ForeignSet):
            return self.item >= self.set[other]
        if self.set != other.set:
            raise Exception(f'Cannot create comparative constraint on two different foreign sets {self} >= {other}')
        # since no item may be shared, this additionally means that the two native items must be disjoint, resulting in an additional item inequality (immediate relation)
        return [Relation(self, other, 'ge'), Relation(self.item, other.item, 'ne')]

    def __repr__(self) -> str:
        return f'{self.item.set.name}[{self.item.value}]({self.set.name})'

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
            if self.b.value in set_ab:
                set_ab.remove(self.b.value)
            if self.a.value in super_sets[self.b.set.name].foreign_sets[self.b.value].foreigns[self.a.set.name]:
                super_sets[self.b.set.name].foreign_sets[self.b.value].foreigns[self.a.set.name].remove(self.a.value)
        elif self.ty == 'gt':
            while set_ab[0] <= self.b.value:
                k = set_ab.pop(0)
                if k in super_sets[self.b.set.name].foreign_sets[k].foreigns[self.a.set.name]:
                    super_sets[self.b.set.name].foreign_sets[k].foreigns[self.a.set.name].remove(self.a.value)
        elif self.ty == 'ge':
            while set_ab[0] < self.b.value:
                k = set_ab.pop(0)
                if k in super_sets[self.b.set.name].foreign_sets[k].foreigns[self.a.set.name]:
                    super_sets[self.b.set.name].foreign_sets[k].foreigns[self.a.set.name].remove(self.a.value)
        elif self.ty == 'lt':
            while set_ab[-1] >= self.b.value:
                k = set_ab.pop()
                if k in super_sets[self.b.set.name].foreign_sets[k].foreigns[self.a.set.name]:
                    super_sets[self.b.set.name].foreign_sets[k].foreigns[self.a.set.name].remove(self.a.value)
        elif self.ty == 'le':
            while set_ab[-1] > self.b.value:
                k = set_ab.pop()
                if k in super_sets[self.b.set.name].foreign_sets[k].foreigns[self.a.set.name]:
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