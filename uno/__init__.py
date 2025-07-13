import socket
import MCLikeCommandParser
from h import *

using_port = []

def is_port_available(port:int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _sock:
        try:
            _sock.bind(('localhost', port))
        except Exception:
            return False
    return True

async def start_one_match() -> int:
    port = 0
    for i in range(5110, 5510 + 1):
        if is_port_available(i):
            port = i
            break
    if not port:
        return -1
    server = MatchServerInstance(port)
    asyncio.create_task(server.quick_start())
    return port

class GameMessage:
    def __init__(self):
        pass

class MatchServerInstance:
    def __init__(self, port:int) -> None:
        self.port = port
        self.ws = websockets.Server(self.request_handler)
        self.match = Match()
    @staticmethod
    async def request_handler(conn:websockets.legacy.server.WebSocketServerProtocol) -> None:
        while True:
            msg = await conn.recv(decode=True)
            print(msg)
    def message_action_business_bindings(self) -> dict:
        ans = {
            self.match
        }
        ...
        return ans
    async def message_action_analyse(self, msg:str) -> None:
        parser = MCLikeCommandParser(msg)
        ...
    async def quick_start(self) -> None:
        ...
    def add_player(self, qqid:int, ws:websockets.legacy.server.WebSocketServerProtocol) -> bool:
        self.match.player_connection_pool.quick_join(qqid, ws)
    def start_game(self) -> None:
        self.match
        ...

class Match:
    def __init__(self) -> None:
        self.global_card_pool = GlobalCardPool()
        self.player_connection_pool = PlayerConnectionPool()
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
    def __init__(self, qqid:int) -> None:
        self.qq = qqid
        self.hand = InHandCards()
    def is_system(self) -> bool:
        return self.qq == 37

class PlayerConnectionPool:
    def __init__(self) -> None:
        self.players:defaultdict[Player, websockets.legacy.server.WebSocketServerProtocol] = defaultdict(None)
        self.cnt = 0
    def get_ws_by_player(self, player:Player) -> websockets.legacy.server.WebSocketServerProtocol|None:
        return self.players[player]
    def join(self, player:Player, ws:websockets.legacy.server.WebSocketServerProtocol) -> bool:
        for p in self.players:
            if p.qq == player.qq:
                return False
        self[player] = ws
        return True
    def quick_join(self, user:int, ws:websockets.legacy.server.WebSocketServerProtocol) -> bool:
        for p in self.players:
            if p.qq == user:
                return False
        self.join(Player(user), ws)
        return True
    def leave(self, player:Player) -> None:
        del self.players[player]
    def find_player_by_ws_strict(self, ws:websockets.legacy.server.WebSocketServerProtocol) -> Player|None:  # 比地址
        """
        按传入 WebSocket 对象的地址查找玩家对象
        """
        for kpl, vws in self.players.items():
            if vws is ws:
                return kpl
        return None
    def get_player_by_ws_strict(self, ws:websockets.legacy.server.WebSocketServerProtocol) -> Player|None:  # 别名
        """
        按传入 WebSocket 对象的地址查找玩家对象
        """
        return self.get_player_by_ws_strict(ws)
    def out(self, player:Player) -> None:
        self.leave(player)
    def get_player_list(self) -> list[Player]:
        ans = []
        for p in self.players:
            if p:
                ans += [p]
        return ans

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
        self.cards = gen_shuffled()
        self.force_refresh_cnt()
    def get_top_7(self) -> list[BaseCard]|None:
        return self.get_top_n(7)
    def get_top_n(self, n:int) -> list[BaseCard]|None:
        if self.cnt >= n >= 1:
            self.cnt -= n
            ans = self.cards[:n]
            self.cards = self.cards[n:]
            return ans
        return None
    def get_random(self) -> BaseCard|None:
        if self.cnt >= 1:
            self.cnt -= 1
            return random.choice(self.cards)
        return None
    def insert_random(self, card:BaseCard) -> bool:
        if card not in self.cards and self.cnt <= 162 - 1:
            position = random.randint(0, self.cnt)
            self.cards.insert(position, card)
            self.cnt += 1
            return True
        return False
    def merge_bottom(self, cards:list[BaseCard]) -> bool:
        if not len(set(self.cards[:] + cards)) and self.cnt + len(cards) <= 162:
            self.cards += cards
            self.cnt += len(cards)
            return True
        return False
    def reset(self) -> None:
        self.cards = gen_shuffled()
        self.force_refresh_cnt()
    def shuffle(self) -> None:
        random.shuffle(self.cards)
    def shuffled(self) -> list[BaseCard]|None:
        self.shuffle()
        return self.cards

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