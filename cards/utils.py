import random

def generate_90ball_ticket():
    columns = [range(1,10), range(10,20), range(20,30), range(30,40), range(40,50),
               range(50,60), range(60,70), range(70,80), range(80,91)]
    ticket = [[None]*9 for _ in range(3)]
    for row in range(3):
        cols = random.sample(range(9), 5)
        used_in_col = {col: set() for col in range(9)}
        for r in range(row):
            for c in range(9):
                if ticket[r][c] is not None:
                    used_in_col[c].add(ticket[r][c])
        for col in cols:
            possible = [n for n in columns[col] if n not in used_in_col[col]]
            if possible:
                ticket[row][col] = random.choice(possible)
        # Sort row
        nums = sorted([x for x in ticket[row] if x])
        i = 0
        for c in range(9):
            if ticket[row][c] is not None:
                ticket[row][c] = nums[i]
                i += 1
    return ticket

def check_90ball_status(marked):
    lines = sum(1 for row in marked if all(m or marked[marked.index(row)][c] is None for c,m in enumerate(row)))
    if lines == 3: return "full_house"
    if lines == 2: return "two_lines"
    if lines == 1: return "one_line"
    return "none"
