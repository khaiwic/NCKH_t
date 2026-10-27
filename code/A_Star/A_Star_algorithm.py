"""A* trên lưới: xuất các bước mở rộng, nhãn g/h/f và đường đi.

Chạy từ thư mục dự án: python code/A_Star/A_Star_algorithm.py
Thư viện vẽ: Matplotlib, Pillow. Không mở cửa sổ đồ họa.
Tọa độ (hàng, cột) từ 0; ô 0 tự do, ô 1 vật cản; bốn hướng, giá mỗi bước 1.
"""

from __future__ import annotations

import argparse
import csv
import heapq
import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

Cell = tuple[int, int]
Grid = Sequence[Sequence[int]]
DIRECTIONS = ((-1, 0), (0, 1), (1, 0), (0, -1))  # trên, phải, dưới, trái


@dataclass
class Snapshot:
    step: int
    current: Cell | None
    g: dict[Cell, int]
    closed: frozenset[Cell]

    @property
    def open_set(self) -> set[Cell]:
        return set(self.g).difference(self.closed)


@dataclass
class SearchResult:
    algorithm: str
    path: list[Cell]
    cost: int | None
    snapshots: list[Snapshot]

    @property
    def expanded_count(self) -> int:
        return len(self.snapshots) - 1


def manhattan(cell: Cell, goal: Cell) -> int:
    """Ước lượng số bước còn lại khi bỏ qua vật cản."""
    return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])


def validate_grid(grid: Grid, start: Cell, goal: Cell) -> None:
    if not grid or not grid[0]:
        raise ValueError("Bản đồ không được rỗng.")
    width = len(grid[0])
    if any(len(row) != width for row in grid):
        raise ValueError("Các hàng phải có cùng số cột.")
    if any(value not in (0, 1) for row in grid for value in row):
        raise ValueError("Ô tự do là 0; ô vật cản là 1.")
    for label, cell in (("Điểm đầu", start), ("Điểm đích", goal)):
        row, col = cell
        if not (0 <= row < len(grid) and 0 <= col < width):
            raise ValueError(f"{label} nằm ngoài bản đồ: {cell}.")
        if grid[row][col]:
            raise ValueError(f"{label} nằm trên vật cản: {cell}.")


def _search(grid: Grid, start: Cell, goal: Cell, use_heuristic: bool) -> SearchResult:
    validate_grid(grid, start, goal)
    name = "A*" if use_heuristic else "Dijkstra"
    heuristic = lambda cell: manhattan(cell, goal) if use_heuristic else 0
    g = {start: 0}
    parents: dict[Cell, Cell] = {}
    closed: set[Cell] = set()
    serial = itertools.count()
    # Ưu tiên f nhỏ; hòa f thì h nhỏ; hòa tiếp thì thứ tự đưa vào heap.
    # Với Dijkstra, h=0 nên đây chính là ưu tiên g và thứ tự vào heap.
    h0 = heuristic(start)
    queue = [(h0, h0, next(serial), 0, start)]
    snapshots = [Snapshot(0, None, g.copy(), frozenset())]

    while queue:
        _, _, _, popped_g, current = heapq.heappop(queue)
        # Bỏ bản ghi cũ hoặc đỉnh đã xử lý; không tính thành bước mở rộng.
        if current in closed or popped_g != g[current]:
            continue
        closed.add(current)
        if current != goal:
            for dr, dc in DIRECTIONS:
                neighbor = (current[0] + dr, current[1] + dc)
                row, col = neighbor
                if not (0 <= row < len(grid) and 0 <= col < len(grid[0])):
                    continue
                if grid[row][col] or neighbor in closed:
                    continue
                candidate = popped_g + 1
                if candidate < g.get(neighbor, math.inf):
                    g[neighbor] = candidate
                    parents[neighbor] = current
                    h = heuristic(neighbor)
                    heapq.heappush(queue, (candidate + h, h, next(serial), candidate, neighbor))
        snapshots.append(Snapshot(len(closed), current, g.copy(), frozenset(closed)))

        # Chỉ kết thúc khi lấy đích ra khỏi heap để chốt, không dừng khi
        # vừa phát hiện đích. Manhattan nhất quán trong mô hình đang xét,
        # nên không cần mở lại các đỉnh đã đóng.
        if current == goal:
            path = [goal]
            while path[-1] != start:
                path.append(parents[path[-1]])
            return SearchResult(name, list(reversed(path)), popped_g, snapshots)
    return SearchResult(name, [], None, snapshots)


def a_star(grid: Grid, start: Cell, goal: Cell) -> SearchResult:
    """Tìm đường A* với Manhattan trên lưới bốn hướng, chi phí đơn vị.

    g: chi phí tốt nhất đã tìm từ S; h: ước lượng tới G; f = g + h.
    Hàm chỉ dùng thư viện chuẩn; dữ liệu từng bước được lưu để vẽ.
    Không thay Manhattan tùy ý nếu chưa xét tính nhất quán và mở lại đỉnh.
    """
    return _search(grid, start, goal, use_heuristic=True)


def dijkstra_baseline(grid: Grid, start: Cell, goal: Cell) -> SearchResult:
    """Đối chiếu trên cùng bản đồ bằng tìm kiếm với h=0."""
    return _search(grid, start, goal, use_heuristic=False)


def example_map() -> tuple[list[list[int]], Cell, Cell]:
    """Cùng bản đồ 9 × 13 với ví dụ tại code/Dijkstra."""
    rows, cols = 9, 13
    grid = [[0] * cols for _ in range(rows)]
    for row in range(rows):
        grid[row][0] = grid[row][-1] = 1
    for col in range(cols):
        grid[0][col] = grid[-1][col] = 1
    for row in range(1, 6):
        grid[row][4] = 1
    for row in range(3, 8):
        grid[row][8] = 1
    grid[3][2] = grid[5][10] = grid[5][11] = 1
    return grid, (7, 1), (1, 11)


def draw_grid(ax, grid: Grid, start: Cell, goal: Cell, state: Snapshot,
              result: SearchResult, path: Sequence[Cell] = (), title: str = "") -> None:
    from matplotlib.patches import Rectangle

    rows, cols = len(grid), len(grid[0])
    path_set = set(path)
    for row in range(rows):
        for col in range(cols):
            cell = row, col
            color = ("#374151" if grid[row][col] else "#b9d9ef" if cell in state.closed
                     else "#fce5a4" if cell in state.g else "#f3f4f6")
            ax.add_patch(Rectangle((col - .5, row - .5), 1, 1, facecolor=color,
                                   edgecolor="white", linewidth=.8))
    if path:
        ax.plot([p[1] for p in path], [p[0] for p in path], color="#16845f",
                linewidth=3, alpha=.7, zorder=2)

    for row in range(rows):
        for col in range(cols):
            cell = row, col
            if grid[row][col]:
                continue
            marker = "S" if cell == start else "G" if cell == goal else ""
            if cell in state.g:
                g = state.g[cell]
                h = manhattan(cell, goal) if result.algorithm == "A*" else 0
                text = f"f={g+h}\ng={g}\nh={h}"
            else:
                text = "∞"
            ax.text(col, row, text, ha="center", va="center", fontsize=6.6,
                    color="#18354a" if cell in state.g else "#909aa3", linespacing=1.05,
                    weight="bold" if marker else "normal", zorder=3,
                    bbox=dict(boxstyle="round,pad=.08", fc="white", ec="none", alpha=.9)
                    if cell in path_set else None)
            if marker:
                ax.text(col-.39, row-.39, marker, ha="left", va="top",
                        fontsize=7, weight="bold", color="#18354a", zorder=4)
    for cell, color in ((start, "#16845f"), (goal, "#b33245")):
        ax.add_patch(Rectangle((cell[1] - .46, cell[0] - .46), .92, .92,
                               fill=False, edgecolor=color, linewidth=2.2, zorder=4))
    if state.current is not None:
        row, col = state.current
        ax.add_patch(Rectangle((col - .48, row - .48), .96, .96,
                               fill=False, edgecolor="#e36b18", linewidth=2.2, zorder=5))
    ax.set(xlim=(-.5, cols-.5), ylim=(rows-.5, -.5), xticks=range(cols),
           yticks=range(rows), xlabel="Cột", ylabel="Hàng")
    ax.set_aspect("equal")
    ax.tick_params(length=0, labelsize=8)
    ax.set_title(title, fontsize=10.5, weight="bold", pad=10)
    for spine in ax.spines.values():
        spine.set_visible(False)


def add_legend(fig, y=.067) -> None:
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    handles = [
        Patch(fc="#374151", label="Vật cản"),
        Patch(fc="#f3f4f6", label="Chưa được tìm tới"),
        Patch(fc="#b9d9ef", label="Đã mở rộng (Closed)"),
        Patch(fc="#fce5a4", label="Đang chờ (Open)"),
        Patch(fc="none", ec="#e36b18", linewidth=2, label="Đỉnh vừa mở rộng"),
        Line2D([0], [0], color="#16845f", linewidth=3, label="Đường đi ngắn nhất"),
    ]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, y),
               ncol=3, frameon=False, fontsize=9)


def state_title(state: Snapshot, result: SearchResult, goal: Cell, final=False) -> str:
    if state.current is None:
        return "Khởi tạo: g(S) = 0; f(S) = h(S)"
    g = state.g[state.current]
    h = manhattan(state.current, goal) if result.algorithm == "A*" else 0
    prefix = "Kết quả" if final else f"Bước {state.step}"
    return f"{prefix}: mở rộng {state.current}, g={g}, h={h}, f={g+h}"


def summary(result: SearchResult) -> str:
    outcome = f"chi phí = {result.cost}" if result.path else "không có đường đi"
    return f"{result.algorithm}: {outcome}; mở rộng {result.expanded_count} đỉnh."


def export_images(grid: Grid, start: Cell, goal: Cell, result: SearchResult,
                  baseline: SearchResult, output: Path, dpi: int,
                  make_gif: bool, all_steps: bool) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.unicode_minus": False})

    total = result.expanded_count
    indices = sorted({min(1, total), *[round(total*p/5) for p in range(1, 6)]})
    fig, axes = plt.subplots(3, 2, figsize=(14, 16))
    for ax, index in zip(axes.flat, indices):
        state = result.snapshots[index]
        final = index == total
        draw_grid(ax, grid, start, goal, state, result, result.path if final else (),
                  state_title(state, result, goal, final))
    for ax in list(axes.flat)[len(indices):]:
        ax.set_visible(False)
    fig.suptitle("A*: CÁC BƯỚC MỞ RỘNG ĐỈNH TRÊN BẢN ĐỒ LƯỚI", fontsize=18, weight="bold", y=.985)
    fig.text(.5, .957, f"Lưới {len(grid)} × {len(grid[0])} • Bốn hướng • Chi phí mỗi bước = 1 • h: khoảng cách Manhattan",
             ha="center", fontsize=10.5)
    fig.subplots_adjust(left=.055, right=.98, top=.92, bottom=.145, hspace=.32, wspace=.17)
    add_legend(fig)
    fig.text(.5, .041, f"S = {start}; G = {goal}. {summary(result)}", ha="center", fontsize=10)
    fig.text(.5, .023, "Nhãn trong ô: f = g + h; g: chi phí từ S; h: ước lượng tới G. Nhãn Open còn tạm thời; ∞: chưa tìm tới.",
             ha="center", fontsize=9)
    fig.savefig(output / "a_star_cac_buoc_mo_rong.png", dpi=dpi, facecolor="white")
    fig.savefig(output / "a_star_cac_buoc_mo_rong.pdf", facecolor="white")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 9.5))
    draw_grid(ax, grid, start, goal, result.snapshots[-1], result, result.path,
              "A*: NHÃN CHI PHÍ g, h, f VÀ ĐƯỜNG ĐI TÌM ĐƯỢC")
    fig.subplots_adjust(left=.07, right=.98, top=.94, bottom=.23)
    add_legend(fig, .07)
    fig.text(.5, .045, summary(result), ha="center", fontsize=11)
    fig.text(.5, .023, "f = g + h; h là khoảng cách Manhattan bỏ qua vật cản.", ha="center", fontsize=10)
    fig.savefig(output / "a_star_duong_di.png", dpi=dpi, facecolor="white")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(15, 8.5))
    for ax, search in zip(axes, (baseline, result)):
        draw_grid(ax, grid, start, goal, search.snapshots[-1], search, search.path,
                  f"{search.algorithm}: {search.expanded_count} đỉnh, chi phí {search.cost}")
    fig.suptitle("DIJKSTRA VÀ A* TRÊN CÙNG BẢN ĐỒ", fontsize=17, weight="bold", y=.98)
    fig.subplots_adjust(left=.045, right=.98, top=.88, bottom=.24, wspace=.15)
    add_legend(fig, .08)
    fig.text(.5, .055, "Dijkstra: h=0. A*: h=Manhattan, hòa f ưu tiên h nhỏ. Hai phương pháp cùng chi phí bước và điều kiện dừng.",
             ha="center", fontsize=10)
    fig.text(.5, .025, "Số đỉnh mở rộng phụ thuộc bản đồ và cách phá hòa; đây là kết quả của ví dụ, không phải bảo đảm giảm trong mọi trường hợp.",
             ha="center", fontsize=9)
    fig.savefig(output / "so_sanh_dijkstra_a_star.png", dpi=dpi, facecolor="white")
    plt.close(fig)

    if make_gif or all_steps:
        from PIL import Image
        if all_steps:
            (output / "tung_buoc").mkdir(exist_ok=True)
        frames = []
        fig, ax = plt.subplots(figsize=(12, 9.5))
        fig.subplots_adjust(left=.07, right=.98, top=.94, bottom=.23)
        add_legend(fig, .065)
        fig.text(.5, .035, "Nhãn ô: f = g + h. g: chi phí từ S; h: Manhattan tới G; ∞: chưa tìm tới.", ha="center", fontsize=10)
        for index, state in enumerate(result.snapshots):
            ax.clear()
            draw_grid(ax, grid, start, goal, state, result,
                      result.path if index == total else (), state_title(state, result, goal, index == total))
            fig.canvas.draw()
            frame = Image.frombuffer("RGBA", fig.canvas.get_width_height(),
                                     fig.canvas.buffer_rgba(), "raw", "RGBA", 0, 1).convert("RGB")
            if make_gif:
                frames.append(frame)
            if all_steps:
                frame.save(output / "tung_buoc" / f"buoc_{index:03d}.png")
        if make_gif:
            durations = [800] + [180] * max(0, len(frames)-2) + ([2200] if len(frames)>1 else [])
            frames[0].save(output / "a_star_qua_trinh.gif", save_all=True,
                           append_images=frames[1:], duration=durations, loop=0)
        plt.close(fig)


def export_data(grid: Grid, start: Cell, goal: Cell, result: SearchResult,
                baseline: SearchResult, output: Path) -> None:
    with (output / "nhat_ky_mo_rong.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("buoc", "hang", "cot", "g", "h", "f", "so_dinh_open"))
        for state in result.snapshots[1:]:
            g, h = state.g[state.current], manhattan(state.current, goal)
            writer.writerow((state.step, *state.current, g, h, g+h, len(state.open_set)))
    data = dict(grid=grid, start=start, goal=goal, step_cost=1,
                moves="up,right,down,left", heuristic="Manhattan",
                tie_break="smaller f, then smaller h, then insertion order",
                path=result.path, total_cost=result.cost, expanded_vertices=result.expanded_count,
                dijkstra=dict(total_cost=baseline.cost, expanded_vertices=baseline.expanded_count,
                              path=baseline.path))
    (output / "ket_qua.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "output")
    parser.add_argument("--dpi", type=int, default=240)
    parser.add_argument("--no-gif", action="store_true")
    parser.add_argument("--all-steps", action="store_true", help="Xuất thêm PNG cho từng bước.")
    args = parser.parse_args()
    if args.dpi <= 0:
        parser.error("--dpi phải lớn hơn 0.")
    grid, start, goal = example_map()
    result = a_star(grid, start, goal)
    baseline = dijkstra_baseline(grid, start, goal)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    export_data(grid, start, goal, result, baseline, args.output_dir)
    export_images(grid, start, goal, result, baseline, args.output_dir,
                  args.dpi, not args.no_gif, args.all_steps)
    print(f"Start: {start}; goal: {goal}")
    print(f"A*: cost={result.cost}, expanded={result.expanded_count}")
    print(f"Dijkstra: cost={baseline.cost}, expanded={baseline.expanded_count}")
    print("Path:", " -> ".join(str(cell) for cell in result.path))
    print("Output:", args.output_dir.resolve())


if __name__ == "__main__":
    main()
