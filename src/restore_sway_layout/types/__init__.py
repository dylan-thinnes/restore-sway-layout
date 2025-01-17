import typing

WorkspaceInfo = typing.TypedDict('WorkspaceInfo', {'num': str, 'name': str})
Leaf = typing.TypedDict('Leaf', {'type': str, 'snapshot': typing.Any, 'workspace': WorkspaceInfo | None})
Split = typing.TypedDict('Split', {'layout': str, 'subtrees': list[typing.Union['Leaf', 'Split']], 'workspace': WorkspaceInfo | None})
Tree = typing.Union[Leaf, Split]
Snapshot = typing.TypedDict('Snapshot', {'timestamp': float, 'workspaces': list[Tree]})

class SupportsSnapshot(typing.Protocol):
    def snapshot(self, node: dict) -> typing.Any:
        pass

class SupportsRestart(typing.Protocol):
    def restart(self, type: str, snapshot: dict) -> typing.Callable:
        pass

RootSwayNode = typing.NewType("RootSwayNode", dict)
