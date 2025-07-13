import socket

from h import *

using_port = []

def is_port_available(port:int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _sock:
        try:
            _sock.bind(('localhost', _sock))
            return False
        except Exception:
            return True

def start_one_match() -> int:
    port = 0
    for i in range(5110, 5510 + 1):
        if is_port_available(i):
            port = i
            break
    if not port:
        return -1

class MatchServerInstance:
    def __init__(self, port:int) -> None:
        self.port = port
        self.ws = websockets.Server(self.request_handler)
    async def request_handler(self, ws) -> None:
        ...

class Match:
    def __init__(self) -> None:
        self.global_card_pool = GlobalCardPool()
        self.global_last = self.global_initial_action()
        self.global_action_history:list[Action] = []
        self.is_stacking = False
    def global_initial_action(self) -> BaseCard:  # 确定底牌
        es = EndStack(random.choice([0, 1, 2, 3]))  # 底牌不要有万能
        self.global_last = es
        _sac = Action(SYSTEM, es)
        self.add_action(_sac)
        return es
    def is_valid_next(self, card:BaseCard) -> bool:
        return is_valid_action(self.global_last, card)
    def force_refresh_global_last(self) -> BaseCard|None:
        _tmp = self.global_action_history[-1]
        if _tmp.acted():
            self.global_last = _tmp.card
            return _tmp
        else:
            return None
    def add_action(self, act:'Action') -> bool:
        if not act.acted() and self.is_valid_next(act.card) and act not in self.global_action_history:
            return False
        self.global_last = act
        self.global_action_history += [act]
    

class Player:
    players = []
    def __init__(self, qqid:int) -> None:
        self.qq = qqid
        self.hand = InHandCards()
        Player.players += [self]
    def is_system(self) -> bool:
        return self.qq == 37

class InHandCards:
    def __init__(self):
        self.cards:list[BaseCard] = []
        self.cnt = 0
    def add(self, card:BaseCard) -> bool:
        if card in self.cards:
            return False
        self.cards += [card]
        self.cnt += 1
        return True
    def remove(self, card:BaseCard) -> bool:
        if card not in self.cards:
            return False
        self.cards.remove(card)
        self.cnt -= 1
        return True
    def force_refresh_cnt(self) -> int:
        self.cnt = len(self.cards)
        return self.cnt

class GlobalCardPool(InHandCards):
    def __init__(self):
        super().__init__()
        self.cards = gen_all()
        self.force_refresh_cnt()

class Action:
    class const:
        PLAYER = player = 0
        SYSTEM = system = 1
    def __init__(self, player:Player, card:BaseCard|None=None):
        self.category = Action.const.PLAYER
        self.player = player
        self._acted = bool(card)
        self.card:BaseCard|None = card
    def is_system_action(self) -> bool:
        return self.player.is_system()
    def acted(self) -> bool:
        return self.card and self._acted
    def set_card(self, card:BaseCard) -> bool:
        if self.acted():
            return False
        self.card = card
        self._acted = True
        return True

SYSTEM = system = Player(37)