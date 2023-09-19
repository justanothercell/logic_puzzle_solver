from sets import Set, Relation, Item

class Solver:
    def __init__(self, *sets: Set):
        self.sets = sets
        self.relations: list[Relation] = []
    
    def relate(self, relation: Relation):
        if isinstance(relation, list):
            self.relations += relation
        else:
            self.relations.append(relation)
    
    def solve(self):
        super_sets = {s.name: SuperSet(s, self.sets) for s in self.sets}
        for s in super_sets.values():
            print(s)
        print()

        for r in self.relations:
            if isinstance(r.a, Item):
                r.evalulate_immediate(super_sets)
        relations = [r for r in self.relations if not isinstance(r.a, Item)]

        for _ in range(1):
            # remove recurring constraints
            for r in relations:
                r.evalulate_recurring(super_sets)

            # search for lonely foreign entry (siblingless)
            for ss in super_sets.values():
                # looping over foreign sets column wise
                for k in self.sets:
                    key = k.name
                    if key == ss.name:
                        continue
                    lonely = None
                    # find lonely
                    for f in ss.foreign_sets.values():
                        if len(f.foreigns[key]) == 1:
                            lonely = f.foreigns[key][0]
                            continue
                    if lonely:
                        # remove lonely everywhere else
                        for kv, f in ss.foreign_sets.items():
                            if len(f.foreigns[key]) != 1 and lonely in f.foreigns[key]:
                                f.foreigns[key].remove(lonely)
                                if kv in super_sets[key].foreign_sets[lonely].foreigns[ss.name]:
                                    super_sets[key].foreign_sets[lonely].foreigns[ss.name].remove(kv)
            # search for unique mentioning of foreign entry
            for ss in super_sets.values():
                # looping over foreign sets column wise
                for k in self.sets:
                    key = k.name
                    if key == ss.name:
                        continue
                    counts = {}
                    # find uniques
                    for f in ss.foreign_sets.values():
                        for item in f.foreigns[key]:
                            if item in counts:
                                counts[item] += 1
                            else:
                                counts[item] = 1
                    print(ss.name, counts)
                    # remove siblings of uniques
                    for c in [c for c, v in counts.items() if v == 1]:
                        for kv, f in ss.foreign_sets.items():
                            if c in f.foreigns[key]:
                                for redundant in [r for r in f.foreigns[key] if r != c]:
                                    f.foreigns[key].remove(redundant)
                                    if kv in super_sets[key].foreign_sets[redundant].foreigns[ss.name]:
                                        super_sets[key].foreign_sets[redundant].foreigns[ss.name].remove(kv)
        print()
        for s in super_sets.values():
            print(s)
        pass

class SuperSet:
    def __init__(self, set_: Set, sets: list[Set]) -> None:
        self.type = Set.__class__
        self.name = set_.name
        self.foreign_sets = {i: ForeignSet(i, [s.copy() for s in sets if s is not set_]) for i in set_.items}
    
    def __repr__(self) -> str:
        return self.name + ':\n  ' + '\n  '.join(str(s) for s in self.foreign_sets.values())

class ForeignSet:
    def __init__(self, item, foreigns: list[Set]):
        self.item = item
        self.foreigns = {f.name: f.items for f in foreigns}
    
    def __repr__(self) -> str:
        return f'{self.item}: {self.foreigns}'