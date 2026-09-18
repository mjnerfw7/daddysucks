"""Neon Maze: a tiny dependency-free first-person 3D game."""

import math
import random
import time
import tkinter as tk


class NeonMaze:
    MAP = (
        "###############",
        "#P....#.......#",
        "#.###.#.#####.#",
        "#...#.#.....#.#",
        "###.#.#####.#.#",
        "#...#.....#...#",
        "#.#######.#.###",
        "#.....#...#...#",
        "#.###.#.#####.#",
        "#...#.#.......#",
        "###.#.#######.#",
        "#...#.........#",
        "#.###########.#",
        "#.............E#",
        "###############",
    )
    WIDTH = 960
    HEIGHT = 600
    FOV = math.pi / 3
    RAYS = 320

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("NEON MAZE // SIGNAL LOST")
        self.root.configure(bg="#080b12")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=self.WIDTH, height=self.HEIGHT,
                                bg="#080b12", highlightthickness=0)
        self.canvas.pack()
        self.keys: set[str] = set()
        self.player_x, self.player_y = 1.5, 1.5
        self.angle = 0.0
        self.start_time = time.time()
        self.last_frame = time.time()
        self.finished = False
        self.crystals = {(4.5, 3.5), (11.5, 3.5), (3.5, 9.5), (9.5, 11.5)}
        self.total_crystals = len(self.crystals)
        self.message = "FIND THE FOUR SIGNAL CRYSTALS"
        self.message_until = 0.0
        self.bind_events()
        self.loop()

    def bind_events(self) -> None:
        self.root.bind("<KeyPress>", lambda event: self.keys.add(event.keysym.lower()))
        self.root.bind("<KeyRelease>", lambda event: self.keys.discard(event.keysym.lower()))
        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.root.bind("<space>", self.restart)
        self.canvas.focus_set()

    def restart(self, _event=None) -> None:
        if self.finished:
            self.player_x, self.player_y = 1.5, 1.5
            self.angle = 0.0
            self.crystals = {(4.5, 3.5), (11.5, 3.5), (3.5, 9.5), (9.5, 11.5)}
            self.finished = False
            self.start_time = time.time()
            self.message = "FIND THE FOUR SIGNAL CRYSTALS"

    def is_wall(self, x: float, y: float) -> bool:
        map_y, map_x = int(y), int(x)
        return (map_y < 0 or map_y >= len(self.MAP) or map_x < 0 or
                map_x >= len(self.MAP[0]) or self.MAP[map_y][map_x] == "#")

    def move(self, distance: float, strafe: float) -> None:
        speed_x = math.cos(self.angle) * distance + math.cos(self.angle + math.pi / 2) * strafe
        speed_y = math.sin(self.angle) * distance + math.sin(self.angle + math.pi / 2) * strafe
        if not self.is_wall(self.player_x + speed_x * 1.8, self.player_y):
            self.player_x += speed_x
        if not self.is_wall(self.player_x, self.player_y + speed_y * 1.8):
            self.player_y += speed_y

    def update(self, dt: float) -> None:
        if self.finished:
            return
        turn = ("right" in self.keys or "d" in self.keys) - ("left" in self.keys or "q" in self.keys)
        forward = ("w" in self.keys or "up" in self.keys) - ("s" in self.keys or "down" in self.keys)
        strafe = ("e" in self.keys) - ("a" in self.keys)
        self.angle += turn * dt * 2.4
        self.move(forward * dt * 2.4, strafe * dt * 2.0)

        collected = next((crystal for crystal in self.crystals
                          if math.hypot(self.player_x - crystal[0], self.player_y - crystal[1]) < 0.45), None)
        if collected:
            self.crystals.remove(collected)
            remaining = len(self.crystals)
            self.message = "SIGNAL ACQUIRED // {} REMAINING".format(remaining) if remaining else "EXIT UNLOCKED // FIND THE GREEN DOOR"
            self.message_until = time.time() + 2.5

        exit_distance = math.hypot(self.player_x - 13.5, self.player_y - 13.5)
        if exit_distance < 0.7:
            if self.crystals:
                self.message = "THE EXIT IS LOCKED // COLLECT ALL CRYSTALS"
                self.message_until = time.time() + 2.0
            else:
                self.finished = True

    def cast_ray(self, ray_angle: float) -> float:
        sin_a, cos_a = math.sin(ray_angle), math.cos(ray_angle)
        distance = 0.02
        while distance < 30:
            x = self.player_x + cos_a * distance
            y = self.player_y + sin_a * distance
            if self.is_wall(x, y):
                return distance
            distance += 0.025
        return 30

    def draw_world(self) -> None:
        horizon = self.HEIGHT * 0.48
        self.canvas.create_rectangle(0, 0, self.WIDTH, horizon, fill="#101d3b", outline="")
        self.canvas.create_rectangle(0, horizon, self.WIDTH, self.HEIGHT, fill="#15121e", outline="")
        self.canvas.create_oval(-160, -190, self.WIDTH + 160, 360, fill="#162a50", outline="")
        for ray in range(self.RAYS):
            ratio = ray / self.RAYS
            ray_angle = self.angle - self.FOV / 2 + ratio * self.FOV
            distance = self.cast_ray(ray_angle)
            corrected = distance * math.cos(ray_angle - self.angle)
            wall_height = min(self.HEIGHT * 1.4, self.HEIGHT / max(corrected, 0.01) * 0.78)
            top = horizon - wall_height / 2
            shade = max(18, min(125, int(138 / (1 + corrected * 0.12))))
            color = "#{:02x}{:02x}{:02x}".format(shade // 3, shade // 2, shade)
            x = int(ratio * self.WIDTH)
            self.canvas.create_rectangle(x, top, x + self.WIDTH / self.RAYS + 1, top + wall_height,
                                         fill=color, outline="")

    def draw_sprites(self) -> None:
        visible = []
        for x, y in self.crystals:
            dx, dy = x - self.player_x, y - self.player_y
            distance = math.hypot(dx, dy)
            angle = math.atan2(dy, dx) - self.angle
            angle = (angle + math.pi) % (2 * math.pi) - math.pi
            if abs(angle) < self.FOV * 0.65 and distance > 0.15:
                visible.append((distance, angle, "#ffdd55"))
        if not self.crystals:
            dx, dy = 13.5 - self.player_x, 13.5 - self.player_y
            distance = math.hypot(dx, dy)
            angle = (math.atan2(dy, dx) - self.angle + math.pi) % (2 * math.pi) - math.pi
            if abs(angle) < self.FOV * 0.65:
                visible.append((distance, angle, "#5dffb0"))
        for distance, angle, color in sorted(visible, reverse=True):
            size = min(150, 90 / max(distance, 0.2))
            center_x = self.WIDTH / 2 + angle / self.FOV * self.WIDTH
            center_y = self.HEIGHT * 0.49
            self.canvas.create_oval(center_x - size / 2, center_y - size / 2,
                                    center_x + size / 2, center_y + size / 2,
                                    fill=color, outline="#ffffff", width=2)
            self.canvas.create_oval(center_x - size / 5, center_y - size / 5,
                                    center_x + size / 5, center_y + size / 5,
                                    fill="#ffffff", outline="")

    def draw_hud(self) -> None:
        elapsed = int(time.time() - self.start_time)
        self.canvas.create_rectangle(20, 18, 300, 72, fill="#080b12", outline="#314565", width=2)
        self.canvas.create_text(36, 35, anchor="w", text="NEON MAZE", fill="#70d7ff", font=("Consolas", 16, "bold"))
        self.canvas.create_text(36, 57, anchor="w", text="CRYSTALS  {}/{}    TIME  {:02d}:{:02d}".format(
            self.total_crystals - len(self.crystals), self.total_crystals, elapsed // 60, elapsed % 60),
            fill="#d8e3ff", font=("Consolas", 10))
        self.canvas.create_rectangle(20, self.HEIGHT - 62, 360, self.HEIGHT - 20, fill="#080b12", outline="#314565")
        self.canvas.create_text(34, self.HEIGHT - 41, anchor="w", text="WASD / ARROWS  MOVE     Q/E  TURN     ESC  QUIT",
                                fill="#9aa9c9", font=("Consolas", 9))
        size = 110
        left, top = self.WIDTH - size - 24, 20
        for row, line in enumerate(self.MAP):
            for col, tile in enumerate(line):
                color = "#18233b" if tile == "#" else "#070c16"
                self.canvas.create_rectangle(left + col * 7, top + row * 7, left + col * 7 + 7,
                                             top + row * 7 + 7, fill=color, outline="")
        self.canvas.create_oval(left + self.player_x * 7 - 2, top + self.player_y * 7 - 2,
                                left + self.player_x * 7 + 2, top + self.player_y * 7 + 2, fill="#ff6b8a", outline="")

        if time.time() < self.message_until or self.finished:
            text = "MISSION COMPLETE  //  PRESS SPACE TO RESTART" if self.finished else self.message
            self.canvas.create_rectangle(self.WIDTH / 2 - 250, 86, self.WIDTH / 2 + 250, 122,
                                         fill="#080b12", outline="#70d7ff")
            self.canvas.create_text(self.WIDTH / 2, 104, text=text, fill="#f1f5ff", font=("Consolas", 11, "bold"))

    def loop(self) -> None:
        now = time.time()
        self.update(min(now - self.last_frame, 0.05))
        self.last_frame = now
        self.canvas.delete("all")
        self.draw_world()
        self.draw_sprites()
        self.draw_hud()
        self.root.after(30, self.loop)


if __name__ == "__main__":
    NeonMaze(tk.Tk()).root.mainloop()
