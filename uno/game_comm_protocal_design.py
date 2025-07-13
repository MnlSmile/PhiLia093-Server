'/post 986561577 call_uno'  # 24B, 0.024kB
'/post 986561577 pass'  # 20B, 0.020kB
# 打出 uuid 为 f49fbcb9-e687-d3eb-b50e-38bacc40c709 的数字牌
'/post 986561577 discard color f49fbcb9-e687-d3eb-b50e-38bacc40c709'  # 66B, 0.066kB
# 打出 uuid 为 ef63abd0-6e70-4c9f-af06-d0d8df0c0bfa 的万能牌, 并换成红色
'/post 986561577 discard wild ef63abd0-6e70-4c9f-af06-d0d8df0c0bfa 0'  # 67B, 0.067kB
# 打出 uuid 为 e98f5768-eaa4-44f3-bffa-28a8693a95ac 的 DrawTill, 令下家一直摸到红色, 转黄
'/post 986561577 discard wild_drawtill e98f5768-eaa4-44f3-bffa-28a8693a95ac 0 1'  # 78B, 0.078kB
'/post 986561577 repost_ununo 1590947611'
'/post 986561577 self_out'
