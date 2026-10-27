# Maze Generator & Pathfinding AI Simulator

**Project Overview:** 
The Maze Generator & Pathfinding AI Simulator generates random mazes and demonstrates/compares different graph traversal and pathfinding algorithms in real time using Pygame.

---

### Objectives:
1. To understand graph representation and traversal techniques.
2. To implement maze generation using Randomized DFS.
3. To compare shortest path algorithms (BFS, DFS, Dijkstra, Greedy Best-First Search).
4. To provide real-time visual simulation of path exploration and benchmark performance metrics.

---

### Key Features:
- **Algorithms Supported:**
  - **BFS (Breadth-First Search):** Guarantees shortest path ($O(V + E)$).
  - **DFS (Depth-First Search):** Explores deeply, doesn't guarantee shortest path ($O(V + E)$).
  - **Dijkstra's Algorithm:** Uniform-cost search using priority queue ($O((V + E) \log V)$).
  - **Greedy Best-First Search:** Heuristic Manhattan distance-based traversal ($O(E \log V)$).
- **Interactive Player Mode:** Navigate manually through the maze using arrow keys or WASD.
- **Multiple Grid Sizes:** Support for $15\times15$, $21\times21$, $27\times27$, and $35\times35$ grids.
- **Loop Generation:** Option to toggle loops to create multiple alternate paths.
- **Performance Benchmarking:** Real-time metrics comparing execution time (ms), visited nodes, and path lengths.

---

### Controls:
| Key | Action |
| :--- | :--- |
| **Arrow Keys / W A S D** | Move Player |
| **Space** | Run AI Solver |
| **1 - 4** | Select Algorithm (1: BFS, 2: DFS, 3: Dijkstra, 4: Greedy) |
| **C** | Compare all algorithms side-by-side |
| **G** | Change Grid Size |
| **L** | Toggle Loops (Multiple Paths ON/OFF) |
| **J** | Toggle Stop at Junctions |
| **R** | Generate New Maze |
| **ESC** | Quit Game |

---

### Requirements & Setup:
```bash
pip install pygame
python maze_game.py
