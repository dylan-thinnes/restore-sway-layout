import typing
from dataclasses import dataclass

@dataclass
class Leaf:
    type: str
    snapshot: typing.Any

    def clean_tree(self: Leaf) -> None | Tree:
        return self

@dataclass
class Split:
    layout: str
    subtrees: list[typing.Union['Leaf', 'Split']]

    def clean_tree(self: Split) -> None | Tree:
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

Tree = typing.Union[Leaf, Split]

@dataclass
class Workspace:
    num: str
    name: str
    root: Tree

@dataclass
class Snapshot:
    timestamp: float
    workspaces: list[Workspace]

class SupportsSnapshot(typing.Protocol):
    def snapshot(self, node: dict) -> typing.Any:
        pass

class SupportsRestart(typing.Protocol):
    def restart(self, type: str, snapshot: typing.Any) -> typing.Callable:
        pass
