# 喊 UNO
'/post 986561577 call_uno'  # 24B, 0.024kB
# 不出
'/post 986561577 pass'  # 20B, 0.020kB
# 打出 uuid 为 f49fbcb9-e687-d3eb-b50e-38bacc40c709 的数字牌
'/post 986561577 discard color f49fbcb9-e687-d3eb-b50e-38bacc40c709'  # 66B, 0.066kB
# 打出 uuid 为 ef63abd0-6e70-4c9f-af06-d0d8df0c0bfa 的万能牌, 并换成红色
'/post 986561577 discard wild ef63abd0-6e70-4c9f-af06-d0d8df0c0bfa 0'  # 67B, 0.067kB
# 打出 uuid 为 e98f5768-eaa4-44f3-bffa-28a8693a95ac 的 DrawTill, 令下家一直摸到红色, 转黄
'/post 986561577 discard wild_drawtill e98f5768-eaa4-44f3-bffa-28a8693a95ac 0 1'  # 78B, 0.078kB
# 客户端自检, 发现自己应该出局
'/post 986561577 self_out'
# 凭凭证 6f00952d-be9a-41b6-a7ae-6489096b24a4 加入这个端口上的对局
'/join 986561577 6f00952d-be9a-41b6-a7ae-6489096b24a4'

# 通知 986561577 按照 category=0 color=0 nextcolor=0 value=0 isstackable=0 iswild=0 行动
'/require 986561577 0 0 0 0 0 0'

# heartbeat
'/hb 986561577'