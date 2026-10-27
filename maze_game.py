import heapq, random, sys, time
import pygame

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
SIZES = [15, 21, 27, 35]
# Algorithm name, time complexity, space complexity, and shortest path guarantee
INFO = {
    'bfs': ('BFS', 'O(V + E)', 'O(V)', 'Yes'),
    'dfs': ('DFS', 'O(V + E)', 'O(V)', 'No'),
    'dijkstra': ('Dijkstra', 'O((V + E) log V)', 'O(V)', 'Yes'),
    'greedy': ('Greedy', 'O(E log V) worst', 'O(V)', 'No')
}
ALGOS = list(INFO)
MAZE_PX, W, H = 540, 960, 680
BG, WALL, FLOOR, TEXT, MUTED, ACCENT = (
    (248, 250, 252), (30, 41, 59), (248, 250, 252),
    (30, 41, 59), (100, 116, 139), (255, 107, 74)
)
START, GOAL, VISIT, SOL, PLAYER = (
    (16, 185, 129), (239, 68, 68), (199, 210, 254),
    (245, 158, 11), (37, 99, 235)
)

# 1. Maze Generation using Randomized DFS
def make_maze(n, loops):
    g = [[1] * n for _ in range(n)]  # 1 represents a wall and 0 represents a path
    stack = [(1, 1)]
    g[1][1] = 0
    while stack:
        r, c = stack[-1]
        nb = [
            (r + 2*dr, c + 2*dc, dr, dc)
            for dr, dc in DIRS
            if 0 < r + 2*dr < n - 1
            and 0 < c + 2*dc < n - 1
            and g[r + 2*dr][c + 2*dc]
        ]
        if nb:
            a, b, dr, dc = random.choice(nb)
            g[r + dr][c + dc] = g[a][b] = 0
            stack.append((a, b))
        else:
            stack.pop()
    # Remove selected walls to create multiple possible paths
    if loops:
        for r in range(1, n - 1):
            for c in range(1, n - 1):
                if g[r][c] and random.random() < .1 and (
                    (not g[r][c-1] and not g[r][c+1])
                    or (not g[r-1][c] and not g[r+1][c])
                ):
                    g[r][c] = 0

    return g
# 2. Pathfinding Algorithms using a Common Search Function
# The priority determines how each algorithm explores the maze:
# BFS uses insertion order, DFS uses reverse insertion order,
# Dijkstra uses distance from the start, and Greedy uses distance to the goal.
def search(algo, grid, start, goal):
    h = lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])
    dist, prev, closed, order = {start: 0}, {start: None}, set(), []
    heap, count = [(0, 0, start)], 0
    while heap:
        _, _, cur = heapq.heappop(heap)

        if cur in closed:
            continue
        closed.add(cur)
        order.append(cur)
        if cur == goal:
            break

        for dr, dc in DIRS:
            nxt = (cur[0] + dr, cur[1] + dc)
            if grid[nxt[0]][nxt[1]] or nxt in closed:
                continue
            nd = dist[cur] + 1
            if nxt in dist and dist[nxt] <= nd:
                continue
            dist[nxt], prev[nxt] = nd, cur
            count += 1
            pri = {
                'bfs': count,
                'dfs': -count,
                'dijkstra': nd,
                'greedy': h(nxt)
            }[algo]
            heapq.heappush(heap, (pri, count, nxt))

    # Reconstruct the path by following previous nodes from the goal
    path, node = [], goal if goal in closed else None
    while node:
        path.append(node)
        node = prev[node]
    return order, path[::-1]

# Measure the average execution time over 20 runs
def bench(algo, grid, start, goal):
    t0 = time.perf_counter()

    for _ in range(20):
        order, path = search(algo, grid, start, goal)

    return order, path, (time.perf_counter() - t0) / 20 * 1000

# 3. Game Implementation
class Game:
    def __init__(self):
        self.size_i, self.loops, self.junction, self.algo = 1, False, True, 'bfs'
        self.new_maze()

    def new_maze(self):
        self.n = SIZES[self.size_i]
        self.cell = MAZE_PX // self.n
        self.grid = make_maze(self.n, self.loops)
        self.start, self.goal = (1, 1), (self.n - 2, self.n - 2)
        self.player, self.visited, self.path = self.start, [], []
        self.anim = self.glide = None
        self.moves = self.steps = 0
        self.won = False
        self.stats, self.table = (0, 0, 0), []
        self.optimal = len(
            search('bfs', self.grid, self.start, self.goal)[1]
        ) - 1
        self.msg = 'Reach the red goal, or press SPACE for the AI solver.'

    def solve(self):
        if self.anim or self.glide:
            return
        order, path, ms = bench(
            self.algo, self.grid, self.player, self.goal
        )
        self.stats = (ms, len(order), len(path) - 1)
        self.visited, self.path, self.anim = [], [], [order, path, 0]

    def compare(self):
        self.table = []
        # Compare all algorithms on the same maze
        for a in ALGOS:
            order, path, ms = bench(
                a, self.grid, self.player, self.goal
            )
            self.table.append(
                (INFO[a][0], len(order), len(path) - 1, ms)
            )

    def update_anim(self):
        if not self.anim:
            return
        order, path, i = self.anim
        i += 4
        self.visited = order[:i]
        if i >= len(order):
            self.path, self.anim = path, None
            self.msg = (
                f'{INFO[self.algo][0]}: path of {len(path) - 1} steps '
                f'(shortest possible = {self.optimal})'
            )
        else:
            self.anim[2] = i

    def step_glide(self):
        dr, dc = self.glide
        r, c = self.player
        nr, nc = r + dr, c + dc
        if self.grid[nr][nc]:
            self.glide = None
            return
        self.player = (nr, nc)
        self.steps += 1
        if self.player == self.goal:
            self.won, self.glide = True, None
            self.msg = (
                f'You win! {self.moves} moves, {self.steps} cells. '
                f'Shortest possible: {self.optimal}. Press R.'
            )
            return
        side = ((0, -1), (0, 1)) if dr else ((-1, 0), (1, 0))
        if self.junction and any(
            not self.grid[nr + a][nc + b] for a, b in side
        ):
            self.glide = None

    def key(self, k):
        moves = {
            pygame.K_UP: (-1, 0), pygame.K_w: (-1, 0),
            pygame.K_DOWN: (1, 0), pygame.K_s: (1, 0),
            pygame.K_LEFT: (0, -1), pygame.K_a: (0, -1),
            pygame.K_RIGHT: (0, 1), pygame.K_d: (0, 1)
        }
        if k in moves and not (self.glide or self.anim or self.won):
            dr, dc = moves[k]

            if not self.grid[self.player[0] + dr][self.player[1] + dc]:
                self.moves += 1
                self.glide = (dr, dc)
        elif k in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
            self.algo = ALGOS[k - pygame.K_1]
        elif k == pygame.K_SPACE:
            self.solve()
        elif k == pygame.K_c:
            self.compare()
        elif k == pygame.K_j:
            self.junction = not self.junction
        elif k == pygame.K_l:
            self.loops = not self.loops
            self.new_maze()
        elif k == pygame.K_g:
            self.size_i = (self.size_i + 1) % len(SIZES)
            self.new_maze()
        elif k == pygame.K_r:
            self.new_maze()

    def draw(self, s, fonts):
        big, font, small = fonts
        s.fill(BG)
        cs, ox, oy = self.cell, 20, 20
        def rect(p, color, pad=0):
            pygame.draw.rect(
                s, color,
                (
                    ox + p[1]*cs + pad,
                    oy + p[0]*cs + pad,
                    cs - 2*pad,
                    cs - 2*pad
                )
            )

        def text(t, x, y, color=TEXT, f=font):
            s.blit(f.render(t, True, color), (x, y))

        for r in range(self.n):
            for c in range(self.n):
                rect((r, c), WALL if self.grid[r][c] else FLOOR)

        for p in self.visited:
            rect(p, VISIT)

        for p in self.path:
            rect(p, SOL, 2)

        rect(self.start, START, 2)
        rect(self.goal, GOAL, 2)

        pygame.draw.circle(
            s, PLAYER,
            (
                ox + self.player[1]*cs + cs//2,
                oy + self.player[0]*cs + cs//2
            ),
            cs//2 - 3
        )
        text(self.msg, 20, 572, TEXT, font)
        for i, (name, col) in enumerate([
            ('Start', START), ('Goal', GOAL), ('Visited', VISIT),
            ('Path', SOL), ('Player', PLAYER)
        ]):
            pygame.draw.rect(s, col, (20 + i*100, 604, 12, 12))
            text(name, 38 + i*100, 600, MUTED, small)
        text(
            'Arrows/WASD: move   SPACE: solve   C: compare   R: new maze   ESC: quit',
            20, 630, MUTED, small
        )

        # Display algorithm settings and performance metrics
        x = 590
        text('Maze Game - Pathfinding AI', x, 20, ACCENT, big)
        text('ALGORITHM  (keys 1-4)', x, 62, MUTED, small)
        for i, a in enumerate(ALGOS):
            on = a == self.algo
            text(
                ('> ' if on else '   ') + f'{i+1}. {INFO[a][0]}',
                x, 82 + i*22, ACCENT if on else TEXT
            )
        text('SETTINGS', x, 180, MUTED, small)
        text(f'[G] Grid size: {self.n} x {self.n}', x, 200)
        text(
            f'[L] Loops (multiple paths): {"ON" if self.loops else "OFF"}',
            x, 222
        )
        text(
            f'[J] Stop at junctions: {"ON" if self.junction else "OFF"}',
            x, 244
        )
        text('METRICS  (time = avg of 20 runs)', x, 276, MUTED, small)
        for i, t in enumerate([
            f'Time: {self.stats[0]:.3f} ms',
            f'Nodes explored: {self.stats[1]}',
            f'Path length: {self.stats[2]}',
            f'Player moves: {self.moves}'
        ]):
            text(t, x, 296 + i*22)
        name, tc, sc, opt = INFO[self.algo]
        text('COMPLEXITY', x, 394, MUTED, small)
        for i, t in enumerate([
            f'{name}',
            f'Time: {tc}',
            f'Space: {sc}',
            f'Always shortest: {opt}'
        ]):
            text(t, x, 414 + i*22)
        text('COMPARISON  (press C)', x, 510, MUTED, small)
        rows = [('Algo', 'Nodes', 'Path', 'ms')] + [
            (a, str(n), str(p), f'{ms:.3f}')
            for a, n, p, ms in self.table
        ]
        for i, row in enumerate(rows):
            for j, cell in enumerate(row):
                text(
                    cell, x + j*85, 530 + i*20,
                    MUTED if i == 0 else TEXT, small
                )

# 4. Main Game Loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption('DAA Project: Maze Game & Pathfinding AI')
    fonts = [
        pygame.font.SysFont('segoeui,arial', sz, bold=b)
        for sz, b in ((20, True), (16, False), (13, False))
    ]
    clock, g, last = pygame.time.Clock(), Game(), 0
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (
                e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                g.key(e.key)
        now = pygame.time.get_ticks()
        if g.glide and now - last > 30:
            g.step_glide()
            last = now
        g.update_anim()
        g.draw(screen, fonts)
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()