import socket
import MCLikeCommandParser
import sys
from h import *

using_port = []
MAX_GAME_TIME = 3600 * 3 // 2

def is_port_available(port:int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _sock:
        try:
            _sock.bind(('localhost', port))
        except Exception:
            return False
    return True

async def a_start_one_match() -> int:
    """
    必须在子进程调用
    """
    port = 0
    for i in range(5110, 5510 + 1):
        if i not in using_port and is_port_available(i):
            port = i
            break
    if not port:
        return -1
    server = MatchServerInstance(port)
    asyncio.create_task(server.a_quick_start())
    return port

class GameServerConnection:
    def __init__(self) -> None:
        ...

class MatchServerInstance:
    def __init__(self, port:int) -> None:
        self.port = port
        self.ws = websockets.Server(self.a_request_handler)
        self.match = Match()
        self.uuid = str(uuid.uuid4())
    @staticmethod
    async def a_request_handler(conn:websockets.ServerConnection) -> None:
        while True:
            msg = await conn.recv(decode=True)
            print(msg)
    def message_action_business_bindings(self) -> dict:
        ans = {
            self.match
        }
        ...
        return ans
    async def a_message_action_analyse(self, msg:str) -> None:
        parser = MCLikeCommandParser(msg)
        ...
    async def a_quick_start(self) -> None:
        ...
    async def a_add_player(self) -> None:
        ...
    def start_game(self) -> None:
        asyncio.create_task(self.a_time_limit())
        self.match
        ...
    async def a_time_limit(self) -> None:
        await asyncio.sleep(MAX_GAME_TIME)
        sys.exit()

class Match:
    def __init__(self) -> None:
        self.global_card_pool = GlobalCardPool()
        self.global_last = self.global_initial_action()
        self.global_action_history:list[Action] = []
        self.is_stacking = False
        self.player_ids:list[int] = []
        self.players:list[Player] = []
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
    def add_player(self, qqid:int) -> bool:
        if qqid not in self.player_ids:
            self.players += [Player(qqid)]
            self.player_ids += [qqid]
            return True
        return False
    async def player_action_post_call_uno(self, qqid:int, action_call_uno:ConstStr) -> None:
        ...
    async def player_action_post_pass(self, qqid:int, action_pass:ConstStr) -> None:
        ...
    async def player_action_post_discard_color(self, qqid:int, action_discard:ConstStr, category_color:ConstStr, cardid:str) -> None:
        ...
    async def player_action_post_discard_wild(self, qqid:int, action_discard:ConstStr, category_wild:ConstStr, cardid:str, turnto:int) -> None:
        ...
    async def player_action_post_discard_wild_drawtill(self, qqid:int, action_discard:ConstStr, category_wild_drawtill:ConstStr, cardid:str, drawto:int, turnto:int) -> None:
        ...
    async def player_action_post_self_out(self, qqid:int, action_self_out:ConstStr) -> None:
        ...

class Player:
    def __init__(self, qqid:int) -> None:
        self.qq = qqid
        self.hand = InHandCards()
    def is_system(self) -> bool:
        return self.qq == 37
    
# 笔记
# UNO 的游戏状态是要同步到所有玩家的, 因此我不认为有必要区分哪个玩家是从哪个 websocket 实例来的消息
# 只需要暴力广播就可以, 我们没有带宽问题(UNO 的同步非常惰性)
# 鉴于每个消息内部都要声明自己的身份, 客户端可以自己分辨出来哪些消息是自己发出去的原文

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
        self.uuid_dict = defaultdict(None)
        for c in self.cards:
            self.uuid_dict[c.uuid] = c
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
    def get_card_by_uuid(self, _uuid:str) -> BaseCard|None:
        return self.uuid_dict[_uuid]

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