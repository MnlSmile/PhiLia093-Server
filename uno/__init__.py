import socket
import MCLikeCommandParser
import sys
from h import *

using_port = []
MAX_GAME_TIME = 3600 * 3 // 2
INIT_INHAND_CARD_CNT = 7

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

def draw(p:'Player', c:'BaseCard') -> str:
    # 加一张 category=0 color=0 nextcolor=0 value=0 isstackable=0 iswild=0 的 350552eb-f924-494a-a11e-110e30a08feb
    return f"/draw {p.qq} {c.uuid} {c.category} {c.color} {c.nextcolor} {c.value} {c.isstackable + 0} {c.iswild + 0}"

def repost(p:'Player', c:'BaseCard') -> str:
    return f"/repost {p.qq} {c.category} {c.color} {c.nextcolor} {c.value} {c.isstackable + 0} {c.iswild + 0}"

class MatchServerInstance:
    def __init__(self, port:int) -> None:
        self.port = port
        self.ws = websockets.Server(self.a_request_handler)
        self.match = Match(self)
        self.uuid = str(uuid.uuid4())
        self.connections:list[websockets.ServerConnection] = []
    async def a_request_handler(self, conn:websockets.ServerConnection) -> None:
        self.connections += [conn]
        while True:
            msg = await conn.recv(decode=True)
            await self.a_message_action_analyse(msg)
            print(msg)
    def message_action_business_bindings(self) -> dict:
        ans = {
            #self.match
        }
        ...
        return ans
    async def a_message_action_analyse(self, msg:str) -> None:
        parser = MCLikeCommandParser.Parser(msg)
        ...
    async def a_quick_start(self) -> None:
        ...
    async def a_start_game(self) -> None:
        asyncio.create_task(self.a_time_limit())
        self.match
        ...
    async def a_time_limit(self) -> None:
        await asyncio.sleep(MAX_GAME_TIME)
        sys.exit()

class Match:
    def __init__(self, server:MatchServerInstance) -> None:
        self.server = server
        self.global_card_pool = GlobalCardPool()
        self.global_last = self.global_initial_action()
        self.global_action_history:list[Action] = []
        self.global_actionque = ActionQueue()
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
        return is_valid_action(self.global_last.card, card)  # type: ignore
    def force_refresh_global_last(self) -> 'Action|None':
        _tmp = self.global_action_history[-1]
        if _tmp.acted():
            self.global_last = _tmp.card
            return _tmp
        else:
            return None
    def add_action(self, act:'Action') -> bool:
        if not act.acted() and self.is_valid_next(act.card) and act not in self.global_action_history:  # type: ignore
            return False
        self.global_last = act
        self.global_action_history += [act]
        return True
    def add_player(self, qqid:int) -> bool:
        if qqid not in self.player_ids:
            self.players += [Player(qqid)]
            self.player_ids += [qqid]
            return True
        return False
    def find_player(self, qqid:int) -> 'Player|None':
        for p in self.players:
            if p.qq == qqid:
                return p
        return None
    async def a_next_round(self) -> None:
        next_player = self.global_actionque.popleft()
        ...
    async def quick_broadcast(self, *args, **kwargs) -> None:
        for conn in self.server.connections:
            asyncio.create_task(conn.send(*args, **kwargs))
    async def player_action_post_call_uno(self, qqid:int, action_call_uno:MCLikeCommandParser.ConstStr) -> None:
        if p := self.find_player(qqid):
            ...
    async def player_action_post_pass(self, qqid:int, action_pass:MCLikeCommandParser.ConstStr) -> None:
        if p := self.find_player(qqid):
            ...
    async def player_action_post_discard_color(self, qqid:int, action_discard:MCLikeCommandParser.ConstStr, category_color:MCLikeCommandParser.ConstStr, cardid:str) -> None:
        if p := self.find_player(qqid):
            c = p.hand.find_card(cardid)
            if is_valid_action(self.global_last.card, c):  # type: ignore
                act = Action(p, c)
                p.hand.remove(c)
                self.add_action(act)
                cmd = repost(p, c)
                await self.quick_broadcast(cmd)
                self.next_round()
            ...
    async def player_action_post_discard_wild(self, qqid:int, action_discard:MCLikeCommandParser.ConstStr, category_wild:MCLikeCommandParser.ConstStr, cardid:str, turnto:int) -> None:
        if p := self.find_player(qqid):
            ...
    async def player_action_post_discard_wild_drawtill(self, qqid:int, action_discard:MCLikeCommandParser.ConstStr, category_wild_drawtill:MCLikeCommandParser.ConstStr, cardid:str, drawto:int, turnto:int) -> None:
        if p := self.find_player(qqid):
            ...
    async def player_action_post_self_out(self, qqid:int, action_self_out:MCLikeCommandParser.ConstStr) -> None:
        if p := self.find_player(qqid):
            ...
    async def initial_game(self) -> None:
        # 发牌
        for p in self.players:
            for c in self.global_card_pool.get_top_n(INIT_INHAND_CARD_CNT):  # type: ignore
                p.hand.add(c)
                await self.quick_broadcast(draw(p, c))
        #for conn in self.server.connections:
        #    await conn.send('/download init_inhand_cards')
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

class PlayerConnectionPool:
    def __init__(self) -> None:
        self.players:defaultdict[Player, websockets.ServerConnection] = defaultdict(None)
        self.cnt = 0
    def get_ws_by_player(self, player:Player) -> websockets.ServerConnection|None:
        return self.players[player]
    def join(self, player:Player, ws:websockets.ServerConnection) -> bool:
        for p in self.players:
            if p.qq == player.qq:
                return False
        self.players[player] = ws
        return True
    def quick_join(self, user:int, ws:websockets.ServerConnection) -> bool:
        for p in self.players:
            if p.qq == user:
                return False
        self.join(Player(user), ws)
        return True
    def leave(self, player:Player) -> None:
        del self.players[player]
    def find_player_by_ws_strict(self, ws:websockets.ServerConnection) -> Player|None:  # 比地址
        """
        按传入 WebSocket 对象的地址查找玩家对象
        """
        for kpl, vws in self.players.items():
            if vws is ws:
                return kpl
        return None
    def get_player_by_ws_strict(self, ws:websockets.ServerConnection) -> Player|None:  # 别名
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
        self.uuid_card_dict:defaultdict[str, BaseCard|None] = defaultdict(None)
    def add(self, card:BaseCard) -> bool:
        if card in self.cards:
            return False
        self.cards += [card]
        self.cnt += 1
        self.uuid_card_dict[card.uuid] = card
        return True
    def remove(self, card:BaseCard) -> bool:
        if card not in self.cards:
            return False
        self.cards.remove(card)
        self.cnt -= 1
        del self.uuid_card_dict[card.uuid]
        return True
    def find_card(self, _uuid:str) -> BaseCard|None:
        return self.uuid_card_dict[_uuid]
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
        return bool(self.card and self._acted)
    def set_card(self, card:BaseCard) -> bool:
        if self.acted():
            return False
        self.card = card
        self._acted = True
        return True
    def __str__(self) -> str:
        ans = f"[{self.player.qq if self.player.qq >= 10000 else '37(SYSTEM)'} -> {self.card.uuid}]"
        return ans

SYSTEM = system = Player(37)

async def main():
    await a_start_one_match()

if __name__ == '__main__':
    asyncio.run(a_start_one_match())