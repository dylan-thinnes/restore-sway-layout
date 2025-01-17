import typing
from dataclasses import dataclass

RawSwayNode = typing.NewType("RawSwayNode", dict)

@dataclass
class Leaf:
    type: str
    snapshot: RawSwayNode

    def clean_tree(self) -> None | typing.Union['Leaf', 'Split']:
        return self

    def leaves(self) -> typing.Generator['Leaf', None, None]:
        yield self

@dataclass
class Split:
    layout: str
    subtrees: list[typing.Union['Leaf', 'Split']]

    def clean_tree(self) -> None | typing.Union[Leaf, 'Split']:
        subtree_count = len(self.subtrees)
        if subtree_count == 0:
            return None
        elif subtree_count == 1:
            return self.subtrees[0].clean_tree()
        else:
            return Split(
                layout = self.layout,
                subtrees = list(filter(None, map(lambda x: x.clean_tree(), self.subtrees))),
            )

    def leaves(self) -> typing.Generator['Leaf', None, None]:
        for subtree in self.subtrees:
            for leaf in subtree.leaves():
                yield leaf

Tree = typing.Union[Leaf, Split]

def dict_to_tree(d: dict) -> Tree:
    if d.get('layout') is not None:
        return Split(
            layout = d['layout'],
            subtrees = list(map(dict_to_tree, d['subtrees']))
        )
    else:
        return Leaf(
            type = d['type'],
            snapshot = RawSwayNode(d['snapshot'])
        )

@dataclass
class Workspace:
    num: str
    name: str
    root: Tree

    def clean_tree(self) -> typing.Union[None, 'Workspace']:
        cleaned_root = self.root.clean_tree()
        if cleaned_root is not None:
            return Workspace(
                num = self.num,
                name = self.name,
                root = cleaned_root
            )
        else:
            return None

    def leaves(self) -> typing.Generator['Leaf', None, None]:
        return self.root.leaves()

def dict_to_workspace(d: dict) -> Workspace:
    return Workspace(
        num = d['num'],
        name = d['name'],
        root = dict_to_tree(d['root'])
    )

@dataclass
class Snapshot:
    timestamp: float
    workspaces: list[Workspace]

    def clean_tree(self) -> 'Snapshot':
        return Snapshot(
            timestamp = self.timestamp,
            workspaces = list(filter(None, map(lambda x: x.clean_tree(), self.workspaces))),
        )

    def leaves(self) -> typing.Generator['Leaf', None, None]:
        for workspace in self.workspaces:
            for leaf in workspace.leaves():
                yield leaf

def dict_to_snapshot(d: dict) -> Snapshot:
    return Snapshot(
        timestamp = d['timestamp'],
        workspaces = list(map(dict_to_workspace, d['workspaces']))
    )

class SupportsSnapshot(typing.Protocol):
    def snapshot(self, node: dict) -> typing.Any:
        pass

class SupportsRestart(typing.Protocol):
    def restart(self, type: str, snapshot: RawSwayNode) -> typing.Callable:
        pass
