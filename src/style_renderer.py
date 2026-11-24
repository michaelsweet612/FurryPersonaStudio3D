"""Realistic 3D projected furry persona renderer with procedural fur tufts, hinged jaw, tongue, and Twin Mode."""

import math
from typing import Callable, List, Tuple

from persona_engine import PersonaProfile


def _hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) != 6:
        return (120, 120, 180)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _shade(hex_color: str, factor: float, add: int = 0) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    r = max(0, min(255, int(r * factor + add)))
    g = max(0, min(255, int(g * factor + add)))
    b = max(0, min(255, int(b * factor + add)))
    return f"#{r:02x}{g:02x}{b:02x}"


def _project(x: float, y: float, z: float, yaw: float, pitch: float, cx: float, cy: float, scale: float):
    cyaw, syaw = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    x1 = x * cyaw - z * syaw
    z1 = x * syaw + z * cyaw
    y2 = y * cp - z1 * sp
    z2 = y * sp + z1 * cp
    fov = 520.0
    persp = fov / (fov + z2 + 250.0)
    return (cx + x1 * persp * scale, cy + y2 * persp * scale, z2, persp * scale)


class PersonaCanvasRenderer:
    """Real-time 3D perspective painter with procedural fur strands and articulated facial rig."""

    def render(
        self,
        canvas,
        p: PersonaProfile,
        yaw: float = 0.2,
        pitch: float = -0.05,
        mouth_open: float = 0.25,
        tongue_out: float = 0.4,
        eye_open: float = 1.0,
        ear_perk: float = 0.65,
        twins: bool = False,
        shake_dx: int = 0,
        shake_dy: int = 0,
    ) -> None:
        canvas.delete("all")
        w = int(canvas["width"])
        h = int(canvas["height"])

        # Studio dark backdrop + 3D floor grid
        canvas.create_rectangle(0, 0, w, h, fill="#0B0818", outline="")
        for i in range(-5, 6):
            p1 = _project(i * 55, 185, -220, yaw, pitch, w / 2, h / 2, 0.9)
            p2 = _project(i * 55, 185, 220, yaw, pitch, w / 2, h / 2, 0.9)
            canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="#1D3842", width=1)

        if twins:
            self._draw_char(canvas, p, yaw, pitch, w / 2 - 115 + shake_dx, h / 2 + 18 + shake_dy, 0.72, mouth_open, tongue_out, eye_open, ear_perk, False)
            self._draw_char(canvas, p, yaw - 0.35, pitch, w / 2 + 115 + shake_dx, h / 2 + 18 + shake_dy, 0.72, mouth_open, tongue_out, eye_open, ear_perk, True)
        else:
            self._draw_char(canvas, p, yaw, pitch, w / 2 + shake_dx, h / 2 + 16 + shake_dy, 0.96, mouth_open, tongue_out, eye_open, ear_perk, False)

        canvas.create_text(
            14, 16, anchor="nw", fill="#00F5D4", font=("Consolas", 9, "bold"),
            text=f"3D RIG // {p.style.upper()} // {p.species.upper()}{' [TWINS]' if twins else ''}"
        )

    def _draw_fur_ball(self, canvas, x, y, z, rx, ry, color, yaw, pitch, cx, cy, scale, strands: int):
        px, py, _, s = _project(x, y, z, yaw, pitch, cx, cy, scale)
        rpx, rpy = max(2, rx * s), max(2, ry * s)
        # Base shadow sphere + midtone + specular highlight for 3D depth
        canvas.create_oval(px - rpx, py - rpy, px + rpx, py + rpy, fill=_shade(color, 0.65), outline="")
        canvas.create_oval(px - rpx * 0.92, py - rpy * 0.92, px + rpx * 0.82, py + rpy * 0.82, fill=color, outline="")
        canvas.create_oval(px - rpx * 0.65, py - rpy * 0.68, px + rpx * 0.25, py + rpy * 0.12, fill=_shade(color, 1.24, 14), outline="")

        # Procedural directional fur tufts
        for i in range(strands):
            ang = (i / max(1, strands)) * math.tau
            ring = 0.78 + ((i * 29) % 20) / 100.0
            sx = px + math.cos(ang) * rpx * ring
            sy = py + math.sin(ang) * rpy * ring
            flen = (7 + (i * 13) % 8) * s
            col = _shade(color, 1.2, 10) if i % 2 == 0 else _shade(color, 0.75)
            canvas.create_line(sx, sy, sx + math.cos(ang) * flen, sy + math.sin(ang) * flen, fill=col, width=max(1, int(2 * s)), capstyle="round")
        return px, py, s

    def _draw_char(self, canvas, p: PersonaProfile, yaw, pitch, cx, cy, scale, mouth_open, tongue_out, eye_open, ear_perk, flip_colors: bool):
        prim = p.accent_color if flip_colors else p.primary_color
        acc = p.primary_color if flip_colors else p.accent_color
        sec = p.secondary_color
        items: List[Tuple[float, Callable]] = []

        # Chest & shoulders
        z_chest = _project(0, 120, -18, yaw, pitch, cx, cy, scale)[2]
        items.append((z_chest, lambda: (
            self._draw_fur_ball(canvas, 0, 126, -18, 84, 72, prim, yaw, pitch, cx, cy, scale, 26),
            self._draw_fur_ball(canvas, 0, 118, 22, 48, 44, sec, yaw, pitch, cx, cy, scale, 14),
        )))

        # Ears
        for side in (-1, 1):
            ex = side * (46 if p.species == "Bunny" else 74)
            ey = -(126 if p.species == "Bunny" else 96) - ear_perk * 18
            ez = -14
            ez_proj = _project(ex, ey, ez, yaw, pitch, cx, cy, scale)[2]

            def _ear(sd=side, x0=ex, y0=ey):
                if p.species in ("Bunny", "Red Panda", "Hyena"):
                    erx = 24 if p.species == "Bunny" else 34
                    ery = 74 if p.species == "Bunny" else 34
                    self._draw_fur_ball(canvas, x0, y0, -14, erx, ery, prim, yaw, pitch, cx, cy, scale, 14)
                    self._draw_fur_ball(canvas, x0, y0 + 5, -4, erx * 0.55, ery * 0.65, sec, yaw, pitch, cx, cy, scale, 0)
                else:
                    b1 = _project(sd * 32, -74, -6, yaw, pitch, cx, cy, scale)
                    b2 = _project(sd * 86, -30, -12, yaw, pitch, cx, cy, scale)
                    tip = _project(sd * (110 if p.species == "Fox" else 92), -(180 if p.species == "Fox" else 155) - ear_perk * 20, -18, yaw, pitch, cx, cy, scale)
                    fill_c = acc if p.species == "Dragon" else prim
                    canvas.create_polygon(b1[0], b1[1], tip[0], tip[1], b2[0], b2[1], fill=fill_c, outline=_shade(prim, 0.55), width=2)
                    in_tip = _project(sd * 78, -135 - ear_perk * 14, -8, yaw, pitch, cx, cy, scale)
                    canvas.create_polygon(b1[0], b1[1], in_tip[0], in_tip[1], b2[0], b2[1], fill=acc if p.species == "Protogen" else sec, outline="")

            items.append((ez_proj, _ear))

        # Head + Cheeks
        z_head = _project(0, -6, 0, yaw, pitch, cx, cy, scale)[2]
        items.append((z_head, lambda: (
            self._draw_fur_ball(canvas, -68, 22, 6, 44, 34, prim, yaw, pitch, cx, cy, scale, 14),
            self._draw_fur_ball(canvas, 68, 22, 6, 44, 34, prim, yaw, pitch, cx, cy, scale, 14),
            self._draw_fur_ball(canvas, 0, -8, 0, 90, 86, prim, yaw, pitch, cx, cy, scale, 36),
            self._draw_fur_ball(canvas, 0, -84, 36, 32, 22, acc, yaw, pitch, cx, cy, scale, 10),
        )))

        # Hinged Jaw + Mouth Cavity + 3D Tongue + Upper Muzzle + Wet Nose
        jaw_drop = mouth_open * 36.0
        z_mouth = _project(0, 34, 78, yaw, pitch, cx, cy, scale)[2]

        def _draw_mouth():
            if p.species == "Protogen":
                vp = _project(0, 12, 68, yaw, pitch, cx, cy, scale)
                self._draw_fur_ball(canvas, 0, 12, 62, 74, 52, "#0B1020", yaw, pitch, cx, cy, scale, 0)
                ry = (4 + mouth_open * 16) * vp[3]
                canvas.create_oval(vp[0] - 26 * vp[3], vp[1] + 20 * vp[3] - ry, vp[0] + 26 * vp[3], vp[1] + 20 * vp[3] + ry, outline=sec, width=3)
                return

            # Lower jaw
            self._draw_fur_ball(canvas, 0, 54 + jaw_drop, 62 - jaw_drop * 0.25, 40, 22, sec, yaw, pitch, cx, cy, scale, 10)
            if mouth_open > 0.05:
                mp = _project(0, 44 + jaw_drop * 0.55, 76, yaw, pitch, cx, cy, scale)
                mr = (6 + mouth_open * 22) * mp[3]
                canvas.create_oval(mp[0] - 30 * mp[3], mp[1] - mr, mp[0] + 30 * mp[3], mp[1] + mr, fill="#3A0E22", outline="")
            if tongue_out > 0.05:
                tlen = 12 + tongue_out * 46
                tb = _project(0, 48 + jaw_drop * 0.5, 78, yaw, pitch, cx, cy, scale)
                tt = _project(0, 56 + jaw_drop * 0.65 + tlen * 0.68, 86 + tlen * 0.65, yaw, pitch, cx, cy, scale)
                canvas.create_line(tb[0], tb[1], tt[0], tt[1], fill="#FF6B9D", width=max(6, int((20 + tongue_out * 6) * tb[3])), capstyle="round")
            # Upper muzzle & wet nose
            self._draw_fur_ball(canvas, 0, 26, 70, 46, 28, sec, yaw, pitch, cx, cy, scale, 14)
            nx, ny, ns = self._draw_fur_ball(canvas, 0, 14, 110, 16, 11, "#1A1324", yaw, pitch, cx, cy, scale, 0)
            canvas.create_oval(nx - 6 * ns, ny - 5 * ns, nx - 1 * ns, ny - 1 * ns, fill="#FFFFFF", outline="")

        items.append((z_mouth, _draw_mouth))

        # 3D Glossy Eyes
        for side in (-1, 1):
            ep = _project(side * 38, -18, 76, yaw, pitch, cx, cy, scale)

            def _eye(pt=ep):
                ex, ey, _, s = pt
                rx, ry = 17 * s, max(2, 19 * s * eye_open)
                if p.species == "Protogen":
                    canvas.create_oval(ex - rx, ey - ry, ex + rx, ey + ry, fill=p.eye_color, outline="")
                    return
                canvas.create_oval(ex - rx, ey - ry, ex + rx, ey + ry, fill="#F8F9FA", outline="#141022", width=2)
                if eye_open > 0.2:
                    irx, iry = 11 * s, 12 * s * eye_open
                    canvas.create_oval(ex - irx, ey - iry, ex + irx, ey + iry, fill=p.eye_color, outline="")
                    prx, pry = 5.5 * s, 6.5 * s * eye_open
                    canvas.create_oval(ex - prx, ey - pry, ex + prx, ey + pry, fill="#0B0812", outline="")
                    canvas.create_oval(ex - 7 * s, ey - 8 * s * eye_open, ex - 2 * s, ey - 3 * s * eye_open, fill="#FFFFFF", outline="")

            items.append((ep[2] + 5, _eye))

        items.sort(key=lambda it: it[0], reverse=True)
        for _, fn in items:
            fn()
