from typing import Any, Optional, Literal, Callable, Union, Iterable
def verify1(iter: Iterable[Any], *checks: Callable[[Any], bool]):
    """Aplica todas as funções de checkagem em todos os valores 
    de `iter` e retorna o primeiro valor fizer todas as fuunções
    retornarem `True` 
    ```python
    codigos = ["00", "01", "11"]
    comeca_com_zero = lambda string: string[0] == "0"
    termina_com_um = lambda string: string[-1] == "1"
    >>> verify1(codigos, comeca_com_zero, termina_com_um)
    "01"
    ```
    FIM.
    """
    for item in iter:
        if all(map(lambda check: check(item), checks)):
            return item
    return None

def verify2(iter: Iterable[Any], *checks: Callable[[Any], bool]):
    result: list[Any] = []
    for item in iter:
        if all(map(lambda check: check(item), checks)):
            result.append(item)
    return result

def DEFAULT_IDENTATION(node: Any, lvl: int) -> str:
    return ' ' * (lvl * 4)

class BaseNode:
    """
    A class representing a node in a tree structure.

    Attributes:
        data (dict[Any, Any]): The data stored in the node.
        parent (Optional[BaseNode]): The parent node.
        children (list[BaseNode]): The list of child nodes.
        root (BaseNode): The root node of the tree.
        id (int): The unique identifier of the node.
        lvl (int): The level of the node in the tree.
        relative_position (Literal['root', 'first one', 'last one', 'other']): The position of the node relative to its siblings.
        activated (bool): Whether the node is activated.
        all (list[BaseNode]): A list of all nodes in the tree.
        hidden_conditions (list[Callable[[BaseNode], bool]]): Conditions to determine if the node is hidden.
        include_conditions (list[Callable[[BaseNode], bool]]): Conditions to determine if the node can be included.
        equal_conditions (list[Callable[[BaseNode, BaseNode | Any], bool]]): Conditions to determine if two nodes are equal.
        representations (list[Callable[[BaseNode], str]]): Functions to generate string representations of the node.
        identation (Callable[[BaseNode, int], str]): Function to generate the indentation string for the node.
        show_before_identation (list[Callable[[BaseNode], str]]): Functions to generate strings to show before the indentation.

    Methods:
        can_include(): Checks if the node can be included based on the include conditions.
        is_hidden(): Checks if the node is hidden based on the hidden conditions.
        __eq__(other: Union['BaseNode', Any]): Checks if the node is equal to another node or object based on the equal conditions.
        reconfigure(id: int = 0, lvl: int = 0, root: Optional['BaseNode'] = None, parent: Optional['BaseNode'] = None): Reconfigures the node and its children.
        __str__(): Generates a string representation of the node.
        before_ident(): Generates a string to show before the indentation.
        prettystr() -> str: Generates a pretty string representation of the node and its children.
        append(other: 'BaseNode'): Appends a child node.
        remove(checks: list[Callable[['BaseNode'], bool]]): Removes nodes based on the provided checks.
        __getitem__(key: Any): Gets an item from the node's data.
        __setitem__(key: Any, value: Any): Sets an item in the node's data.
    """
    def __init__(self, data: dict[Any, Any]):
        self.data = data
        self.parent: Optional[BaseNode] = None
        self.parents: list[BaseNode] = []
        self.children: list[BaseNode] = []
        self.root: BaseNode = self
        self.id: int = 0
        self.lvl: int = 0
        self.relative_position: Literal[
            'root', 'first one', 'last one', 'other' 
        ] = 'root'
        self.activated: bool = True
        self.all: list[BaseNode] = [self]
        self.hidden_conditions: list[Callable[[BaseNode], bool]] = []
        self.include_conditions: list[Callable[[BaseNode], bool]] = []
        self.equal_conditions: list[Callable[[BaseNode, BaseNode | Any], bool]]  = []
        self.representations: list[Callable[[BaseNode], str]] = []
        self.identation: Callable[[BaseNode, int], str] = DEFAULT_IDENTATION
        self.show_before_identation: list[Callable[[BaseNode], str]] = []
        self.START_FROM: int = 0
    def can_include(self):
        # res = []
        # for function in self.conditions:
        #     res.append(function(self))
        # return all(res)
        return all(map((lambda f: f(self)), self.include_conditions))
    
    def is_hidden(self):
        return all(map((lambda f: f(self)), self.hidden_conditions))
    
    def __eq__(self, other: Union['BaseNode', Any]):
        return all(map(lambda f: f(self, other), self.equal_conditions))

    def reconfigure(self, id: int = 0, lvl: int = 0, root: Optional['BaseNode'] = None, parent: Optional['BaseNode'] = None):
        if id == 0:
            id = self.START_FROM
            self.all.clear()
            root = self
        if self.can_include():
            self.parent = parent
            self.root = root or self
            self.id = id
            self.lvl = lvl
            self.parents = self.parent.parents + [self.parent] if self.parent else []
            self.root.all.append(self)
            lvl += 1
            for n, child in enumerate(self.children):
                if n == 0:
                    child.relative_position = 'first one'
                elif n == (len(self.children) - 1):
                    child.relative_position = 'last one'
                else:
                    child.relative_position = 'other'
                id, lvl = child.reconfigure(id + 1, lvl, root, self)
        return id, lvl - 1
    def __str__(self):
        return ''.join(f(self) for f in self.representations)
    def before_ident(self):
        return ''.join(f(self) for f in self.show_before_identation)
    def prettystr(self, lvl: int=0) -> str:
        r = f'{self.before_ident()}{self.identation(self, lvl)}{self}'
        lvl += 1
        for child in self.children:
            if not child.is_hidden():
                r += f'\n{child.prettystr(lvl=lvl)}'
        return r
    def root_show(self):
        r = ''
        for node in self.children:
            r += f'\n{node.prettystr()}'
        return r
    def append(self, other: 'BaseNode'):
        self.children.append(other)
        self.root.reconfigure()
    def __getitem__(self, key: Any):
        return self.data.get(key)
    def __setitem__(self, key: Any, value: Any):
        self.data[key] = value
    def deactivate(self):
        self.activated = False
        if self.parent is not None:
            index = self.parent.children.index(self)
            del self.parent.children[index]
        self.root.reconfigure()