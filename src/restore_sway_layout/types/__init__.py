import typing
from dataclasses import dataclass

@dataclass
class WorkspaceInfo:
    num: str
    name: str

@dataclass
class Leaf:
    type: str
    snapshot: typing.Any
    workspace: WorkspaceInfo | None

@dataclass
class Split:
    layout: str
    subtrees: list[typing.Union['Leaf', 'Split']]
    workspace: WorkspaceInfo | None

Tree = typing.Union[Leaf, Split]

@dataclass
class Snapshot:
    timestamp: float
    workspaces: list[Tree]

class SupportsSnapshot(typing.Protocol):
    def snapshot(self, node: dict) -> typing.Any:
        pass

class SupportsRestart(typing.Protocol):
    def restart(self, type: str, snapshot: dict) -> typing.Callable:
        pass
