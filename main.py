import sys

def solve():
    # Kiritish qismini o'zgartiramiz, readline tezroq va xavfsizroq
    line = sys.stdin.readline()
    if not line:
        return
    try:
        n, m, k = map(int, line.split())
    except ValueError:
        return

    MOD = 10**9 + 7
    num_masks = 1 << (k + 1)
    dp = [[0] * (m + 1) for _ in range(num_masks)]
    dp[0][0] = 1

    for i in range(1, n + 1):
        
        for d in range(1, k + 1):
            if i + d <= n:
            
                m1 = 1          # 0-bit
                m2 = (1 << d)   # d-bit
                combined_mask = m1 | m2
                
                for j in range(m):
                    for mask in range(num_masks):
                        if dp[mask][j] > 0:
                            next_mask = mask ^ combined_mask
                         
                            dp[next_mask][j + 1] = (dp[next_mask][j + 1] + dp[mask][j]) % MOD
      
        if i < n:
            new_dp = [[0] * (m + 1) for _ in range(num_masks)]
            for mask in range(num_masks):
               
                if not (mask & 1):
                    next_mask = mask >> 1
                    for j in range(m + 1):
                        new_dp[next_mask][j] = dp[mask][j]
            dp = new_dp
        else:
            
            print(dp[0][m])

if __name__ == "__main__":
    solve()