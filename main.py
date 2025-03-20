import Nodes
from typing import Any, Optional
from colorama import Fore, Style
import os
import curses
from utils import (
    Actions, 
    Action,
    Input, 
    Print,
    AddLinesWhileBeep
)
import pickle as pkl
from utils.terminal_actions import ignore
RESET = Style.RESET_ALL

def do_nothing():
    return None

def PARENT_IS_CLOSED(node: Nodes.BaseNode) -> bool:
    if node.parent is not None:
        return node.parent['closed'] == True
    return False
def IS_SELECTED(node: Nodes.BaseNode) -> str:
    if node['selected']:
        return f'{Fore.LIGHTGREEN_EX}◉{RESET} '
    return f'{Fore.LIGHTGREEN_EX}○{RESET} '
def EQ_ID(node: Nodes.BaseNode, other: Nodes.BaseNode | Any):
    if isinstance(other, (type(node))):
        return node.id == other.id
    return False
def NAME(node: Nodes.BaseNode) -> str:
    if not node['selected']:
        return f'{Fore.LIGHTBLACK_EX}{node["name"]}{RESET}'
    return f'{node["name"]}'
def STATE(node: Nodes.BaseNode) -> str:
    match node['closed']:
        case True:
            return f'{Fore.RED}⯈ {RESET}'
        case False: 
            return f'{Fore.LIGHTGREEN_EX}⯆ {RESET}'
        case _:
            return '  '
def IS_ACTIVATED(node: Nodes.BaseNode) -> bool:
    return node.activated
def STR_ID(node: Nodes.BaseNode) -> str:
    return f'{node.id:0>2} '
def IDENTATION(node: Nodes.BaseNode, lvl: int) -> str:
    return '  │ ' * lvl
class MyNode(Nodes.BaseNode):
    def __init__(self, name: str, closed: Optional[bool], data: dict[Any, Any]):
        super().__init__(data)
        self['name'] = name
        self['closed'] = closed
        self['selected'] = False
        self.hidden_conditions      = [PARENT_IS_CLOSED   ]
        self.equal_conditions       = [EQ_ID              ]
        self.representations        = [STATE, NAME        ]
        self.include_conditions     = [IS_ACTIVATED       ]
        self.show_before_identation = [IS_SELECTED, STR_ID]
        self.identation = IDENTATION

class Main:
    def __init__(self, window: curses.window):
        self.super = Nodes.BaseNode({})
        self.index = 0
        self.running: bool = True
        curses.curs_set(2)
        self.window = window
        self.print = Print(window=window)
        self.input = Input(window=window)
        actions = Actions(window=window)
        self.actions = actions.display_loop(
            Action('c', 'Criar', 
            lambda: self.print(
            'Escolha uma opção para criar:', end=''
            ),
            actions.display(
            Action('r', 'Criar raiz', self.criar_root),
            Action('n', 'Criar nó', self.criar_node),
            Action('', 'Cancelar', do_nothing)
            )
            ),
            Action('d', 'Deletar', 
            lambda: self.print('Escolha uma opção para deletar:'),
            actions.display(
            Action('r', 'Deletar raiz', 
            lambda: self.print('Tem certeza que deseja deletar a raiz?'),
            actions.display(
            Action('s', 'Sim', self.remover_root),
            Action(('n', ignore), 'Não', do_nothing)
            )
            ),
            Action('n', 'Deletar nó', 
            lambda: self.print('Tem certeza que deseja deletar o nó?'),
            actions.display(
            Action('s', 'Sim', self.remover_node),
            Action(('n', ignore), 'Não', do_nothing)
            )
            ),
            Action('', 'Cancelar', do_nothing)
            )),
            Action('e', 'Expandir/Colapsar nó', self.enc_desenc_node),
            Action('w', 'Mover para cima', self.mover(-1)),
            Action('s', 'Mover para baixo', self.mover(1)),
            Action('f', 'Arquivo', actions.display(
            Action('s', 'Salvar arquivo', self.salvar),
            Action('l', 'Carregar arquivo', self.carregar),
            Action('', 'Cancelar', do_nothing)
            )),
            Action('q', 'Parar execução', self.stop),
            Action('r', 'Reiniciar aplicação', self.restart)
        )
    # Acoes
    def criar_node(self):
        nome = self.input('Nome do novo node: ')
        self.selecionado().append(MyNode(nome, None, {}))
        if self.selecionado()['closed'] is None:
            self.selecionado()['closed'] = False
    def criar_root(self):
        nome = self.input('Nome do novo root: ')
        self.super.append(MyNode(nome, None, {}))
        if self.super['closed'] is None:
            self.super['closed'] = False
    def remover_node(self):
        node = self.selecionado()
        if node.parent not in (self.super, None):
            if len(node.parent.children) <= 1:
                node.parent['closed'] = None
        node.deactivate()
    def remover_root(self):
        x = self.selecionado()
        while x.parent not in (self.super, None):
            x = x.parent
        x.deactivate()
    def editar_campo(self):
        chave = self.input('Chave: ')
        valor = self.input('Valor: ')
        self.selecionado()[chave] = valor
    def enc_desenc_node(self):
        node = self.selecionado()
        match node['closed']:
            case False:
                node['closed'] = True
            case True:
                node['closed'] = False
            case _:
                pass
    def mover(self, n: int):
        def wrapper():
            self.desselecionar()
            self.index += n
            self.normalizar()
            self.selecionar()
            mov = self.mover(1 if n >= 0 else -1)
            while Nodes.verify1(self.selecionado().parents + [self.selecionado()], PARENT_IS_CLOSED):
                mov()
        return wrapper
    # Cursor
    def limite(self):
        return len(self.super.all) - 1
    def normalizar(self):
        self.index = min(max(self.index, 1), self.limite())
    def desselecionar(self):
        for node in self.super.all[1:]:
            node['selected'] = False
    def selecionar(self):
        self.selecionado()['selected'] = True
    def selecionado(self):
        for node in self.super.all[1:]:
            if node.id == self.index:
                return node
        if len(self.super.all) <= 1:
            raise IndexError('Por favor, crie uma raiz.')
        raise IndexError(f'Não existe node com o id {self.index}')
    
    # Arquivo
    def salvar(self):
        filename = self.input('Nome do arquivo: ')
        with open(filename + '.pkl', 'wb') as file:
            pkl.dump(self.super, file)
    def carregar(self):
        filename = self.input('Nome do arquivo: ')
        with open(filename + '.pkl', 'rb') as file:
            self.super = pkl.load(file)
            self.restart()
    # Rodando
    def stop(self):
        self.running = False
        os.system('reset && clear')
    def restart(self):
        self.print('carregando...')
        self.stop()
        self.start()
    def start(self):
        self.running = True
        self.window.scrollok(True)
        self.window.clear()
        AddLinesWhileBeep(self.window, self.super.root_show())
        ajustar_posicao = self.mover(0)
        if len(self.super.all) > 1:
            ajustar_posicao()
        while self.running:
            try:
                self.actions()
                ajustar_posicao()
            except Exception as e:
                self.print(f'{Fore.RED}{type(e).__name__}: {e}{RESET}')
                self.window.getch()
            
            self.window.clear()
            self.print(self.super.root_show(), end='')
            self.window.refresh()
        
if __name__ == '__main__':
    curses.wrapper(Main).start()