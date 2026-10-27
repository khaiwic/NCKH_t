"""Dijkstra trên bản đồ lưới và xuất hình minh họa quá trình tìm đường.

Chạy: python code/Dijkstra_algorithm.py
Kết quả mặc định: code/output/dijkstra/ (không cần mở cửa sổ đồ họa).

Quy ước: ô 0 tự do, ô 1 là vật cản; tọa độ (hàng, cột), bắt đầu từ 0.
Chỉ xét bốn hướng, chi phí mỗi bước bằng 1. Không dùng heuristic.
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
# Thứ tự xét láng giềng cố định, giúp kết quả lặp lại giữa các lần chạy.
DIRECTIONS = ((-1, 0), (0, 1), (1, 0), (0, -1))


@dataclass
class Snapshot:
    """Trạng thái sau khi chốt một đỉnh có chi phí nhỏ nhất."""

    step: int
    current: Cell | None
    distances: dict[Cell, int]
    settled: frozenset[Cell]

    @property
    def frontier(self) -> set[Cell]:
        return set(self.distances).difference(self.settled)


@dataclass
class DijkstraResult:
    path: list[Cell]
    cost: int | None
    snapshots: list[Snapshot]


def validate_grid(grid: Grid, start: Cell, goal: Cell) -> None:
    if not grid or not grid[0]:
        raise ValueError("Bản đồ không được rỗng.")
    width = len(grid[0])
    if any(len(row) != width for row in grid):
        raise ValueError("Các hàng của bản đồ phải có cùng số cột.")
    if any(value not in (0, 1) for row in grid for value in row):
        raise ValueError("Mỗi ô phải bằng 0 (tự do) hoặc 1 (vật cản).")
    for name, cell in (("Điểm đầu", start), ("Điểm đích", goal)):
        row, col = cell
        if not (0 <= row < len(grid) and 0 <= col < width):
            raise ValueError(f"{name} nằm ngoài bản đồ: {cell}.")
        if grid[row][col] != 0:
            raise ValueError(f"{name} nằm trên vật cản: {cell}.")


def dijkstra(grid: Grid, start: Cell, goal: Cell) -> DijkstraResult:
    """Tìm đường bằng hàng đợi ưu tiên, lưu trạng thái để minh họa.

    Một đỉnh được chốt khi lấy ra khỏi heap với nhãn nhỏ nhất, không phải
    ngay khi đưa vào heap. Chỉ dừng khi đích được chốt. Bộ đếm phụ phá hòa
    theo thứ tự đưa vào heap; các bản ghi cũ trong heap được bỏ qua.
    """
    validate_grid(grid, start, goal)
    rows, cols = len(grid), len(grid[0])
    distances = {start: 0}
    parents: dict[Cell, Cell] = {}
    settled: set[Cell] = set()
    order = itertools.count()
    queue = [(0, next(order), start)]
    snapshots = [Snapshot(0, None, distances.copy(), frozenset())]

    while queue:
        cost, _, current = heapq.heappop(queue)
        if current in settled or cost != distances[current]:
            continue
        settled.add(current)

        if current != goal:
            for dr, dc in DIRECTIONS:
                neighbor = (current[0] + dr, current[1] + dc)
                row, col = neighbor
                if not (0 <= row < rows and 0 <= col < cols):
                    continue
                if grid[row][col] or neighbor in settled:
                    continue
                new_cost = cost + 1
                if new_cost < distances.get(neighbor, math.inf):
                    distances[neighbor] = new_cost
                    parents[neighbor] = current
                    heapq.heappush(queue, (new_cost, next(order), neighbor))

        snapshots.append(
            Snapshot(len(settled), current, distances.copy(), frozenset(settled))
        )
        if current == goal:
            path = [goal]
            while path[-1] != start:
                path.append(parents[path[-1]])
            path.reverse()
            return DijkstraResult(path, cost, snapshots)

    return DijkstraResult([], None, snapshots)


def example_map() -> tuple[list[list[int]], Cell, Cell]:
    """Ví dụ cố định: hai vách đứng buộc đường đi qua các khe khác nhau."""
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


def draw_grid(ax, grid: Grid, start: Cell, goal: Cell, snapshot: Snapshot,
              path: Sequence[Cell] = (), title: str = "") -> None:
    from matplotlib.patches import Rectangle

    rows, cols = len(grid), len(grid[0])
    for row in range(rows):
        for col in range(cols):
            cell = (row, col)
            if grid[row][col]:
                color = "#374151"
            elif cell in snapshot.settled:
                color = "#b9d9ef"
            elif cell in snapshot.distances:
                color = "#fce5a4"
            else:
                color = "#f3f4f6"
            ax.add_patch(Rectangle((col - .5, row - .5), 1, 1,
                                   facecolor=color, edgecolor="white", linewidth=.8))

    if path:
        ax.plot([p[1] for p in path], [p[0] for p in path],
                color="#16845f", linewidth=3, alpha=.8, zorder=2)

    for row in range(rows):
        for col in range(cols):
            cell = (row, col)
            if grid[row][col]:
                continue
            value = str(snapshot.distances[cell]) if cell in snapshot.distances else "∞"
            if cell == start:
                value = f"S\n{value}"
            elif cell == goal:
                value = f"G\n{value}"
            ax.text(col, row, value, ha="center", va="center", fontsize=9,
                    weight="bold" if cell in (start, goal) else "normal",
                    color="#122d40" if cell in snapshot.distances else "#969da5",
                    linespacing=.85, zorder=3,
                    bbox=dict(boxstyle="round,pad=.08", fc="white", ec="none", alpha=.8)
                    if path and cell in path else None)

    for cell, color in ((start, "#16845f"), (goal, "#b33245")):
        ax.add_patch(Rectangle((cell[1] - .46, cell[0] - .46), .92, .92,
                               fill=False, edgecolor=color, linewidth=2.3, zorder=4))
    if snapshot.current is not None:
        row, col = snapshot.current
        ax.add_patch(Rectangle((col - .48, row - .48), .96, .96,
                               fill=False, edgecolor="#e36b18", linewidth=2.3, zorder=5))

    ax.set(xlim=(-.5, cols - .5), ylim=(rows - .5, -.5),
           xticks=range(cols), yticks=range(rows), xlabel="Cột", ylabel="Hàng")
    ax.set_aspect("equal")
    ax.tick_params(labelsize=8, length=0)
    ax.set_title(title, fontsize=11, weight="bold", pad=9)
    for spine in ax.spines.values():
        spine.set_visible(False)


def add_legend(fig, y: float = .065) -> None:
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    handles = [
        Patch(facecolor="#374151", label="Vật cản"),
        Patch(facecolor="#f3f4f6", label="Chưa được tìm tới"),
        Patch(facecolor="#b9d9ef", label="Đã mở rộng (đã chốt)"),
        Patch(facecolor="#fce5a4", label="Đang chờ mở rộng"),
        Patch(facecolor="none", edgecolor="#e36b18", linewidth=2,
              label="Đỉnh vừa mở rộng"),
        Line2D([0], [0], color="#16845f", linewidth=3, label="Đường đi ngắn nhất"),
    ]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, y),
               ncol=3, frameon=False, fontsize=9)


def snapshot_title(snapshot: Snapshot, final: bool = False) -> str:
    prefix = "Kết quả cuối" if final else f"Bước {snapshot.step}"
    if snapshot.current is None:
        return "Khởi tạo: d(S) = 0; các ô khác chưa biết chi phí"
    row, col = snapshot.current
    cost = snapshot.distances[snapshot.current]
    return f"{prefix}: chốt ({row}, {col}), d = {cost}"


def export_images(grid: Grid, start: Cell, goal: Cell, result: DijkstraResult,
                  output: Path, dpi: int, make_gif: bool, all_steps: bool) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.unicode_minus": False})
    total = len(result.snapshots) - 1
    # Sáu trạng thái đại diện; đồ thị rất nhỏ có thể có ít hơn sáu trạng thái.
    indices = sorted({1 if total else 0, *[round(total * p / 5) for p in range(1, 6)]})
    fig, axes = plt.subplots(3, 2, figsize=(13, 15))
    for ax, index in zip(axes.flat, indices):
        state = result.snapshots[index]
        final = index == total
        draw_grid(ax, grid, start, goal, state, result.path if final else (),
                  snapshot_title(state, final))
    for ax in list(axes.flat)[len(indices):]:
        ax.set_visible(False)
    fig.suptitle("DIJKSTRA TRÊN BẢN ĐỒ LƯỚI", fontsize=19, weight="bold", y=.985)
    fig.text(.5, .955, f"Lưới {len(grid)} × {len(grid[0])} • Bốn hướng • Chi phí mỗi bước = 1 • Không dùng heuristic",
             ha="center", fontsize=11)
    fig.subplots_adjust(left=.055, right=.98, top=.92, bottom=.14, hspace=.31, wspace=.18)
    add_legend(fig, .065)
    status = f"Chi phí đường đi = {result.cost}; mở rộng {total} đỉnh." if result.path else "Không tìm thấy đường tới đích."
    fig.text(.5, .04, f"S = {start}; G = {goal}. {status}", ha="center", fontsize=10)
    fig.text(.5, .021, "Số trong ô: nhãn chi phí d từ S. Nhãn ô xanh đã chốt; nhãn ô vàng còn tạm thời; ∞: chưa tìm tới.",
             ha="center", fontsize=9)
    fig.savefig(output / "dijkstra_cac_buoc_mo_rong.png", dpi=dpi, facecolor="white")
    fig.savefig(output / "dijkstra_cac_buoc_mo_rong.pdf", facecolor="white")
    plt.close(fig)

    final_fig, ax = plt.subplots(figsize=(11, 8.6))
    draw_grid(ax, grid, start, goal, result.snapshots[-1], result.path,
              "DIJKSTRA: NHÃN CHI PHÍ VÀ ĐƯỜNG ĐI TÌM ĐƯỢC")
    final_fig.subplots_adjust(left=.08, right=.97, top=.93, bottom=.22)
    add_legend(final_fig, .06)
    final_fig.text(.5, .035, status, ha="center", fontsize=11)
    final_fig.savefig(output / "dijkstra_duong_di.png", dpi=dpi, facecolor="white")
    plt.close(final_fig)

    if make_gif or all_steps:
        from PIL import Image
        frames = []
        if all_steps:
            (output / "tung_buoc").mkdir(exist_ok=True)
        animation_fig, ax = plt.subplots(figsize=(10, 8))
        animation_fig.subplots_adjust(left=.07, right=.98, top=.92, bottom=.22)
        add_legend(animation_fig, .06)
        animation_fig.text(.5, .035, "Số trong ô = chi phí d; xanh: đã chốt; vàng: đang chờ; ∞: chưa tìm tới.",
                           ha="center", fontsize=9)
        for index, state in enumerate(result.snapshots):
            ax.clear()
            draw_grid(ax, grid, start, goal, state,
                      result.path if index == total else (), snapshot_title(state, index == total))
            animation_fig.canvas.draw()
            frame = Image.frombuffer("RGBA", animation_fig.canvas.get_width_height(),
                                     animation_fig.canvas.buffer_rgba(), "raw", "RGBA", 0, 1).convert("RGB")
            if make_gif:
                frames.append(frame)
            if all_steps:
                frame.save(output / "tung_buoc" / f"buoc_{index:03d}.png")
        if make_gif:
            frames[0].save(output / "dijkstra_qua_trinh.gif", save_all=True,
                           append_images=frames[1:], loop=0,
                           duration=[800] + [180] * max(0, len(frames) - 2) + ([2200] if len(frames) > 1 else []))
        plt.close(animation_fig)


def export_data(grid: Grid, start: Cell, goal: Cell, result: DijkstraResult,
                output: Path) -> None:
    with (output / "nhat_ky_mo_rong.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("buoc", "hang", "cot", "chi_phi_da_chot", "so_dinh_dang_cho"))
        for state in result.snapshots[1:]:
            writer.writerow((state.step, *state.current,
                             state.distances[state.current], len(state.frontier)))
    data = dict(grid=grid, start=start, goal=goal, moves="up,right,down,left",
                step_cost=1, path=result.path, total_cost=result.cost,
                expanded_vertices=len(result.snapshots) - 1)
    (output / "ket_qua.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parent / "output" / "dijkstra")
    parser.add_argument("--dpi", type=int, default=240, help="Độ phân giải PNG (mặc định 240).")
    parser.add_argument("--no-gif", action="store_true", help="Không xuất ảnh động.")
    parser.add_argument("--all-steps", action="store_true", help="Xuất thêm một PNG cho mỗi bước.")
    args = parser.parse_args()
    if args.dpi <= 0:
        parser.error("--dpi phải lớn hơn 0.")
    grid, start, goal = example_map()
    result = dijkstra(grid, start, goal)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    export_data(grid, start, goal, result, args.output_dir)
    export_images(grid, start, goal, result, args.output_dir,
                  args.dpi, not args.no_gif, args.all_steps)
    print(f"Start (row, col): {start}; Goal: {goal}")
    print(f"Shortest-path cost: {result.cost}; expanded vertices: {len(result.snapshots)-1}")
    print("Path:", " -> ".join(str(cell) for cell in result.path))
    print("Output:", args.output_dir.resolve())


if __name__ == "__main__":
    main()
