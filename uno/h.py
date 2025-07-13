import websockets

from collections import deque

class ActionQueue(deque):
    def __init__(self, gui) -> None:
        self.gui = gui
        self.base_actionque:list[int] = []
        self.actionlst:list[int]  = []
        self.players:list[int] = []
        self.cnt_players = 0
        self.player_lock = False
    def add_player(self, player:int) -> None:
        if not self.player_lock and player not in self.players:
            self.players += [player]
            self.cnt_players += 1
    def remove_player(self, player:int) -> None:
        if not self.player_lock and player in self.players:
            self.players.remove(player)
            self.cnt_players -= 1
    def lock_and_initialize(self) -> None:
        self.clear()
        self.player_lock = True
        self.base_actionque = self.players[:]
        self.actionlst = self.base_actionque[:]
        random.shuffle(self.base_actionque)
        for p in self.base_actionque:
            self.append(p)
    def end_round(self) -> None:
        p = self.popleft()
        self.append(p)
        del self.actionlst[0]
        self.actionlst += [p]
        
    def reverse(self) -> None:
        self.actionlst.reverse()
        self.base_actionque.reverse()
        self.reverse()

# 记录:
# 我希望简化 GUI 部分的 API, 它们只需要知道怎么把头像反过来, 怎么在左边插一个头像, 怎么在右边插一个头像, 怎么从左边弹一个头像出来, 怎么从左边弹多个头像出来
# 而不要它自己维护一个行动序列, ActionQueue 给它一个 QQ 号, 让它自己找头像然后正确显示出来就行了
# 这样做动画也更好做, 只需要最简单的 QPropertryAnimation 来改位置和大小就行了

# 怎么说这也是个联网的游戏, 如果你不吝啬流量的话, 不考虑考虑直接不在本地维护行动序列? 让服务端算好发行动序列过来
# 也没那么多同步问题

class BaseCard:
    class const:
        TEMP = temp = -1
        RED = red = 0
        YELLOW = yellow = 1
        BLUE = blue = 2
        GREEN = green = 3
        WILD = wild = 4

        NUM = num = 0
        FEATURE = feature = 1
        ENDSTACK = 2
        VOID = 3

        EMPTY = -2
        ANY = -1
        SKIP = skip = 10
        REVERSE = reverse = 11
        PLUS2 = P2 = 12
        PLUS4 = P4 = 13
        REVERSEPLUS4 = RP4 = 13
        PLUS6 = P6 = 14
        PLUS10 = P10 = 15
        PLUSTILL = plustill = DRAWTILL = drawtill = 16
        ONEMOREROUND = onemoreround = 17
        CLEARCOLOR = clearcolor = 18
    class con(const):...

    category:int
    color:int
    nextcolor:int
    value:int
    isstackable:bool
    iswild:bool
    featfunc=lambda:None
    def __init__(self, _): ...
    def __str__(self): ...
    def __lt__(self, a0:'Num') -> bool: ...
    def __le__(self, a0:'Num') -> bool: ...
    def __gt__(self, a0:'Num') -> bool: ...
    def __ge__(self, a0:'Num') -> bool: ...
    def feat(self) -> None: ...
    def set_feat(self, func) -> None: ...

class Num(BaseCard):
    @staticmethod
    def gen_all() -> 'list[Num]':
        result = []
        for col in range(4):
            for num in range(10):
                result += [Num(col, num)] * 2
        return result
    
    def __init__(self, color:int, num:int):
        self.category = BaseCard.con.NUM
        self.isstackable = False
        self.iswild = False
        self.color = color
        self.nextcolor = color
        self.value = num
        self.featfunc = lambda:None
    def __str__(self):
        _col = '红黄蓝绿'        
        return f"{_col[self.color]} {self.value}"
    
    # UNO 比大小我们只关心数值, 不关心颜色
    def __lt__(self, a0:'Num') -> bool:
        return self.value < a0.value
    def __le__(self, a0:'Num') -> bool:
        return self.value <= a0.value
    def __gt__(self, a0:'Num') -> bool:
        return self.value > a0.value
    def __ge__(self, a0:'Num') -> bool:
        return self.value >= a0.value
    def feat(self) -> None:
        ...
        'NumCard 没有功能'
    def set_feat(self, func) -> None:
        ...

class Reverse(BaseCard):
    @staticmethod
    def gen_all() -> 'list[Reverse]':
        result = []
        for col in range(4):
            result += [Reverse(col)] * 3
        return result
    
    def __init__(self, color:int):
        self.category = BaseCard.con.FEATURE
        self.isstackable = False
        self.iswild = False
        self.color = color
        self.nextcolor = color
        self.value = BaseCard.con.REVERSE
        self.featfunc = lambda:None
    def __str__(self):
        _col = '红黄蓝绿'
        return f"{_col[self.color]} 转"
    
    # UNO 比大小我们只关心数值, 不关心颜色
    def __lt__(self, a0:'Num') -> bool:
        return self.value < a0.value
    def __le__(self, a0:'Num') -> bool:
        return self.value <= a0.value
    def __gt__(self, a0:'Num') -> bool:
        return self.value > a0.value
    def __ge__(self, a0:'Num') -> bool:
        return self.value >= a0.value
    def feat(self) -> None:
        self.featfunc()
    def set_feat(self, func) -> None:
        self.featfunc = func

class Skip(BaseCard):
    @staticmethod
    def gen_all() -> 'list[Skip]':
        result = []
        for col in range(4):
            result += [Skip(col)] * 2
        return result
    
    def __init__(self, color:int):
        self.category = BaseCard.con.FEATURE
        self.isstackable = True
        self.iswild = False
        self.color = color
        self.nextcolor = color
        self.value = BaseCard.con.SKIP
        self.featfunc = lambda:None
    def __str__(self):
        _col = '红黄蓝绿'
        return f"{_col[self.color]} 禁"
    
    # UNO 比大小我们只关心数值, 不关心颜色
    def __lt__(self, a0:'Num') -> bool:
        return self.value < a0.value
    def __le__(self, a0:'Num') -> bool:
        return self.value <= a0.value
    def __gt__(self, a0:'Num') -> bool:
        return self.value > a0.value
    def __ge__(self, a0:'Num') -> bool:
        return self.value >= a0.value
    def feat(self) -> None:
        self.featfunc()
    def set_feat(self, func) -> None:
        self.featfunc = func

class OneMoreRound(BaseCard):
    @staticmethod
    def gen_all() -> 'list[OneMoreRound]':
        result = []
        for col in range(4):
            result += [OneMoreRound(col)] * 2
        return result
    
    def __init__(self, color:int):
        self.category = BaseCard.con.FEATURE
        self.isstackable = False
        self.iswild = False
        self.color = color
        self.nextcolor = color
        self.value = BaseCard.con.ONEMOREROUND
        self.featfunc = lambda:None
    def __str__(self):
        _col = '红黄蓝绿'
        return f"{_col[self.color]} 追加"
    
    # UNO 比大小我们只关心数值, 不关心颜色
    def __lt__(self, a0:'Num') -> bool:
        return self.value < a0.value
    def __le__(self, a0:'Num') -> bool:
        return self.value <= a0.value
    def __gt__(self, a0:'Num') -> bool:
        return self.value > a0.value
    def __ge__(self, a0:'Num') -> bool:
        return self.value >= a0.value
    def feat(self) -> None:
        self.featfunc()
    def set_feat(self, func) -> None:
        self.featfunc = func

class ClearColor(BaseCard):
    @staticmethod
    def gen_all() -> 'list[ClearColor]':
        result = []
        for col in range(4):
            result += [ClearColor(col)] * 3
        return result
    
    def __init__(self, color:int):
        self.category = BaseCard.con.FEATURE
        self.isstackable = False
        self.iswild = False
        self.color = color
        self.nextcolor = color
        self.value = BaseCard.con.CLEARCOLOR
        self.featfunc = lambda:None
    def __str__(self):
        _col = '红黄蓝绿'
        return f"{_col[self.color]} 同色全出"
    
    # UNO 比大小我们只关心数值, 不关心颜色
    def __lt__(self, a0:'Num') -> bool:
        return self.value < a0.value
    def __le__(self, a0:'Num') -> bool:
        return self.value <= a0.value
    def __gt__(self, a0:'Num') -> bool:
        return self.value > a0.value
    def __ge__(self, a0:'Num') -> bool:
        return self.value >= a0.value
    def feat(self) -> None:
        self.featfunc()
    def set_feat(self, func) -> None:
        self.featfunc = func

class Plus2(BaseCard):
    @staticmethod
    def gen_all() -> 'list[Plus2]':
        result = []
        for col in range(4):
            result += [Plus2(col)] * 3
        return result
    
    def __init__(self, color:int):
        self.category = BaseCard.con.FEATURE
        self.isstackable = True
        self.iswild = False
        self.color = color
        self.nextcolor = color
        self.value = BaseCard.con.P2
        self.featfunc = lambda:None
    def __str__(self):
        _col = '红黄蓝绿'
        return f"{_col[self.color]} +2"
    
    # UNO 比大小我们只关心数值, 不关心颜色
    def __lt__(self, a0:'Num') -> bool:
        return self.value < a0.value
    def __le__(self, a0:'Num') -> bool:
        return self.value <= a0.value
    def __gt__(self, a0:'Num') -> bool:
        return self.value > a0.value
    def __ge__(self, a0:'Num') -> bool:
        return self.value >= a0.value
    def feat(self) -> None:
        self.featfunc()
    def set_feat(self, func) -> None:
        self.featfunc = func

class ColoredPlus4(BaseCard):
    @staticmethod
    def gen_all() -> 'list[ColoredPlus4]':
        result = []
        for col in range(4):
            result += [ColoredPlus4(col)] * 2
        return result
    
    def __init__(self, color:int):
        self.category = BaseCard.con.FEATURE
        self.isstackable = True
        self.iswild = False
        self.color = color
        self.nextcolor = color
        self.value = BaseCard.con.P4
        self.featfunc = lambda:None
    def __str__(self):
        _col = '红黄蓝绿'
        return f"{_col[self.color]} +4"
    
    # UNO 比大小我们只关心数值, 不关心颜色
    def __lt__(self, a0:'Num') -> bool:
        return self.value < a0.value
    def __le__(self, a0:'Num') -> bool:
        return self.value <= a0.value
    def __gt__(self, a0:'Num') -> bool:
        return self.value > a0.value
    def __ge__(self, a0:'Num') -> bool:
        return self.value >= a0.value
    def feat(self) -> None:
        self.featfunc()
    def set_feat(self, func) -> None:
        self.featfunc = func

class ReversePlus4(BaseCard):
    @staticmethod
    def gen_all() -> 'list[ReversePlus4]':
        result = [ReversePlus4(BaseCard.con.TEMP) for _ in range(8)]
        return result
    
    def __init__(self, nextcolor:int):
        self.category = BaseCard.con.FEATURE
        self.isstackable = True
        self.iswild = True
        self.color = BaseCard.con.WILD
        self.nextcolor = nextcolor
        self.value = BaseCard.con.RP4
        self.featfunc = lambda:None
    def __str__(self):
        return f"反 +4"
    
    # UNO 比大小我们只关心数值, 不关心颜色
    def __lt__(self, a0:'Num') -> bool:
        return self.value < a0.value
    def __le__(self, a0:'Num') -> bool:
        return self.value <= a0.value
    def __gt__(self, a0:'Num') -> bool:
        return self.value > a0.value
    def __ge__(self, a0:'Num') -> bool:
        return self.value >= a0.value
    def feat(self) -> None:
        self.featfunc()
    def set_feat(self, func) -> None:
        self.featfunc = func

class Plus6(BaseCard):
    @staticmethod
    def gen_all() -> 'list[Plus6]':
        result = [Plus6(BaseCard.con.TEMP) for _ in range(4)]
        return result
    
    def __init__(self, nextcolor:int):
        self.category = BaseCard.con.FEATURE
        self.isstackable = True
        self.iswild = True
        self.color = BaseCard.con.WILD
        self.nextcolor = nextcolor
        self.value = BaseCard.con.P6
        self.featfunc = lambda:None
    def __str__(self):
        return f"+6"
    
    # UNO 比大小我们只关心数值, 不关心颜色
    def __lt__(self, a0:'Num') -> bool:
        return self.value < a0.value
    def __le__(self, a0:'Num') -> bool:
        return self.value <= a0.value
    def __gt__(self, a0:'Num') -> bool:
        return self.value > a0.value
    def __ge__(self, a0:'Num') -> bool:
        return self.value >= a0.value
    def feat(self) -> None:
        self.featfunc()
    def set_feat(self, func) -> None:
        self.featfunc = func

class Plus10(BaseCard):
    @staticmethod
    def gen_all() -> 'list[Plus10]':
        result = [Plus10(BaseCard.con.TEMP) for _ in range(3)]
        return result
    
    def __init__(self, nextcolor:int):
        self.category = BaseCard.con.FEATURE
        self.isstackable = True
        self.iswild = True
        self.color = BaseCard.con.WILD
        self.nextcolor = nextcolor
        self.value = BaseCard.con.P10
        self.featfunc = lambda:None
    def __str__(self):
        return f"+10"
    
    # UNO 比大小我们只关心数值, 不关心颜色
    def __lt__(self, a0:'Num') -> bool:
        return self.value < a0.value
    def __le__(self, a0:'Num') -> bool:
        return self.value <= a0.value
    def __gt__(self, a0:'Num') -> bool:
        return self.value > a0.value
    def __ge__(self, a0:'Num') -> bool:
        return self.value >= a0.value
    def feat(self) -> None:
        self.featfunc()
    def set_feat(self, func) -> None:
        self.featfunc = func

class DrawTill(BaseCard):
    @staticmethod
    def gen_all() -> 'list[DrawTill]':
        result = [DrawTill(BaseCard.con.TEMP) for _ in range(7)]
        return result
    
    def __init__(self, nextcolor:int):
        self.category = BaseCard.con.FEATURE
        self.isstackable = True
        self.iswild = True
        self.color = BaseCard.con.WILD
        self.nextcolor = nextcolor
        self.value = BaseCard.con.DRAWTILL
        self.featfunc = lambda:None
    def __str__(self):
        return f"+++"
    
    # UNO 比大小我们只关心数值, 不关心颜色
    def __lt__(self, a0:'Num') -> bool:
        return self.value < a0.value
    def __le__(self, a0:'Num') -> bool:
        return self.value <= a0.value
    def __gt__(self, a0:'Num') -> bool:
        return self.value > a0.value
    def __ge__(self, a0:'Num') -> bool:
        return self.value >= a0.value
    def feat(self) -> None:
        self.featfunc()
    def set_feat(self, func) -> None:
        self.featfunc = func

# 处理叠加截止, 回归正常行动的虚拟牌
class EndStack(BaseCard):
    def __init__(self, color:int):
        self.category = BaseCard.con.ENDSTACK
        self.isstackable = False
        self.iswild = False
        self.color = color
        self.nextcolor = color
        self.value = BaseCard.con.ANY
        self.featfunc = lambda:None
    def __str__(self):
        _col = '红黄蓝绿'
        return f"{_col[self.color]} EndStack"
    
    # UNO 比大小我们只关心数值, 不关心颜色
    def __lt__(self, a0:'Num') -> bool:
        return self.value < a0.value
    def __le__(self, a0:'Num') -> bool:
        return self.value <= a0.value
    def __gt__(self, a0:'Num') -> bool:
        return self.value > a0.value
    def __ge__(self, a0:'Num') -> bool:
        return self.value >= a0.value
    def feat(self) -> None:
        self.featfunc()
    def set_feat(self, func) -> None:
        self.featfunc = func

# 处理空行动的虚拟牌
class Void(BaseCard):
    def __init__(self, color:int):
        self.category = BaseCard.con.VOID
        self.isstackable = False
        self.iswild = False
        self.color = color
        self.nextcolor = color
        self.value = BaseCard.con.ANY
        self.featfunc = lambda:None
    def __str__(self):
        _col = '红黄蓝绿'
        return f"{_col[self.color]} EndStack"
    
    # UNO 比大小我们只关心数值, 不关心颜色
    def __lt__(self, a0:'Num') -> bool:
        return self.value < a0.value
    def __le__(self, a0:'Num') -> bool:
        return self.value <= a0.value
    def __gt__(self, a0:'Num') -> bool:
        return self.value > a0.value
    def __ge__(self, a0:'Num') -> bool:
        return self.value >= a0.value
    def feat(self) -> None:
        self.featfunc()
    def set_feat(self, func) -> None:
        self.featfunc = func

def gen_all() -> list[BaseCard]:
    return Num.gen_all() + ColoredPlus4.gen_all() + ReversePlus4.gen_all() + Plus2.gen_all() + Plus6.gen_all() + Plus10.gen_all() + DrawTill.gen_all() + Reverse.gen_all() + Skip.gen_all() + OneMoreRound.gen_all() + ClearColor.gen_all()

def gen_shuffled() -> list[BaseCard]:
    _all = gen_all()
    random.shuffle(_all)
    return _all

_all = gen_all()
_allstr = [str(i) for i in _all]
print(len(_allstr))

def is_valid_action(last:BaseCard, this:BaseCard) -> bool:
    class con(BaseCard.con): ...
    if this.category == con.NUM:  # 这一张是数字
        if last.category in [con.ENDSTACK, con.NUM]:  # 上一张是数字或者堆末
            return this.color == last.nextcolor or this.value == last.value
        elif last.value in [con.CLEARCOLOR, con.ONEMOREROUND]:  # 上一张是同色全出
            return this.color == last.nextcolor or this.value == last.value
        else:  # 其他都不可能出得了
            return False
    elif this.category == con.FEATURE:  # 这一张是功能
        if last.category in [con.ENDSTACK, con.NUM]:  # 上一张是数字或者堆末
            return this.color == last.nextcolor or this.color == con.WILD
        elif last.category == con.FEATURE:  # 上一张是功能
            if this.iswild:  # 这张是万能
                # 万能能接着功能出的，就只有加牌这种情形
                if con.P2 <= this.value <= con.P10 and con.P2 <= last.value <= con.P10:  # 上一张和这个都是加牌
                    return last.value <= this.value
                else:
                    return False
            else:  # 这张有色
                match last.value:
                    case con.SKIP:
                        return this.color == last.nextcolor or this.value == last.value
                    case con.REVERSE:
                        return this.color == last.nextcolor or this.value == last.value
                    case con.ONEMOREROUND:
                        return this.color == last.nextcolor or this.value == last.value
                    case con.CLEARCOLOR:
                        return this.color == last.nextcolor or this.value == last.value
                    case _:
                        return False
        else:
            return False
    elif this.category == con.ENDSTACK:
        return last.isstackable

def is_valid_action_ds(last:BaseCard, this:BaseCard) -> bool:
    """
    此函数逻辑由 Deepseek R1 生成
    """
    # 定义可叠加的功能牌值集合
    stackable_values = {
        BaseCard.const.SKIP,       # 10
        BaseCard.const.PLUS2,      # 12
        BaseCard.const.PLUS4,      # 13
        BaseCard.const.PLUS6,      # 14
        BaseCard.const.PLUS10,     # 15
        BaseCard.const.PLUSTILL,   # 16
        BaseCard.const.ONEMOREROUND,  # 17
        BaseCard.const.CLEARCOLOR  # 18
    }
    
    # 处理EndStack虚拟牌：使用其颜色作为有效颜色
    if last.category == BaseCard.const.ENDSTACK:
        effective_color = last.color
        return (
            this.color == effective_color or
            this.value == last.value or
            this.color == BaseCard.const.WILD
        )
    
    # 检查是否处于加牌叠加序列
    if last.category == BaseCard.const.FEATURE and last.value in stackable_values:
        # 必须出可叠加功能牌，且值不小于上一张牌
        return (
            this.category == BaseCard.const.FEATURE and
            this.value in stackable_values and
            this.value >= last.value
        )
    
    # 基本规则匹配
    # 确定上一张牌的有效颜色：万能牌用nextcolor，其他用自身颜色
    effective_color = last.nextcolor if last.iswild else last.color
    
    # 当前牌匹配条件：颜色相同、值相同、或出万能牌
    return (
        this.color == effective_color or
        (this.value == last.value and this.value != BaseCard.const.TEMP) or
        this.color == BaseCard.const.WILD
    )

def is_plus_type(card:BaseCard) -> bool:
    return BaseCard.con.P2 <= card.value <= BaseCard.con.P10

if __name__ == '__main__':
    a1 = Num(0, 2)
    a2 = Num(1, 2)
    print(a1, '<-', a2, is_valid_action(a1, a2), '\n')
    import random
    a1 = random.choice(_all)
    a2 = random.choice(_all)
    print(a1, '<-', a2, is_valid_action(a1, a2), '\n')