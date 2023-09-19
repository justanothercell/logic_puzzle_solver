from sets import Set, Relation, Item

class Model:
    def __init__(self, *sets: Set):
        self.sets = sets
        self.relations: list[Relation] = []
    
    def relate(self, relation: Relation):
        if isinstance(relation, list):
            self.relations += relation
        else:
            self.relations.append(relation)
    
    def solver(self) -> 'Solver':
        super_sets = {s.name: SuperSet(s, self.sets) for s in self.sets}

        return Solver(super_sets, self.relations)


class Solver:
    def __init__(self, super_sets: dict[str, 'SuperSet'], relations: list[Relation]):
        for r in relations:
            if isinstance(r.a, Item):
                r.evalulate_immediate(super_sets)
        relations = [r for r in relations if not isinstance(r.a, Item)]

        self.super_sets = super_sets
        self.relations = relations

    def solve(self, max_iter=8):
        for _ in range(max_iter):
            # remove recurring constraints
            for r in self.relations:
                r.evalulate_recurring(self.super_sets)

            # search for lonely foreign entry (siblingless)
            for ss in self.super_sets.values():
                # looping over foreign sets column wise
                for k in self.super_sets.values():
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
                                if kv in self.super_sets[key].foreign_sets[lonely].foreigns[ss.name]:
                                    self.super_sets[key].foreign_sets[lonely].foreigns[ss.name].remove(kv)
            # search for unique mentioning of foreign entry
            for ss in self.super_sets.values():
                # looping over foreign sets column wise
                for k in self.super_sets.values():
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
                    # remove siblings of uniques
                    for c in [c for c, v in counts.items() if v == 1]:
                        for kv, f in ss.foreign_sets.items():
                            if c in f.foreigns[key]:
                                for redundant in [r for r in f.foreigns[key] if r != c]:
                                    f.foreigns[key].remove(redundant)
                                    if kv in self.super_sets[key].foreign_sets[redundant].foreigns[ss.name]:
                                        self.super_sets[key].foreign_sets[redundant].foreigns[ss.name].remove(kv)

            # Inter-ForeignSet search
            for ss in self.super_sets.values():
                for ss2 in self.super_sets.values():
                    if ss == ss2:
                        continue
                    for f in ss.foreign_sets.values():
                        for f2 in ss2.foreign_sets.values():
                            common = set(f.foreigns.keys()) & set(f2.foreigns.keys())
                            for k in common:
                                if len(f.foreigns[k]) == 1 and f.foreigns[k] == f2.foreigns[k]:
                                    for k2 in common:
                                        if k2 == k:
                                            continue
                                        for i in set(f2.foreigns[k2]) ^ set(f.foreigns[k2]):
                                            if i in f2.foreigns[k2]:
                                                f2.foreigns[k2].remove(i)
                                            if i in self.super_sets[k].foreign_sets[f.foreigns[k][0]].foreigns[k2]:
                                                self.super_sets[k].foreign_sets[f.foreigns[k][0]].foreigns[k2].remove(i)
            # ForeignSet to SuperSet propagation
            for ss in self.super_sets.values():
                for f in ss.foreign_sets.values():
                    for k in f.foreigns.keys():
                        if len(f.foreigns[k]) == 1:
                            f2 = self.super_sets[k].foreign_sets[f.foreigns[k][0]]
                            common = set(f.foreigns.keys()) & set(f2.foreigns.keys())
                            for k2 in common:
                                for i in set(f.foreigns[k2]) ^ set(f2.foreigns[k2]):
                                    if i in f2.foreigns[k2]:
                                        f2.foreigns[k2].remove(i)
        # check for completeness
        for ss in self.super_sets.values():
            for f in ss.foreign_sets.values():
                for k, i in f.foreigns.items():
                    if len(i) != 1:
                        if len(i) > 1:
                            raise ValueError('Could not solve the model. Either too few interations or the relations were not constraining enough')
                        raise ArithmeticError(f'The model is not solvable since no {k} satisfies a constraint for {ss.name}')
        return Solution(self.super_sets)


class Solution:
    def __init__(self, super_sets: dict[str, 'SuperSet']):
        self.super_sets = super_sets

    def __repr__(self) -> str:
        headigns = [k for k in self.super_sets.keys()]
        rows = []
        ss = list(self.super_sets.values())[0]
        for (k, f) in ss.foreign_sets.items():
            row = [k, *[str(v[0]) for v in f.foreigns.values()]]
            rows.append(row)
        columns = [len(k) for k in headigns]
        for row in rows:
            for i, k in enumerate(row):
                columns[i] = max(columns[i], len(k))
        s_rows = ['| ' + ' | '.join(e.ljust(l) for e, l in zip(headigns, columns)) + ' |', '|-' + '-|-'.join('-' * l for _, l in zip(headigns, columns)) + '-|']
        for row in rows:
            s_rows.append('| ' + ' | '.join(e.ljust(l) for e, l in zip(row, columns)) + ' |')
        return '\n'.join(s_rows)

class SuperSet:
    def __init__(self, set_: Set, sets: list[Set]):
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