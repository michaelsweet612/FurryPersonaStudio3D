"""Furry Persona Studio 3D v3.0 — Desktop 3D Fur & Facial Rig + Random GOOD BOY Button."""

import json
import os
import random
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk

from audio_chaos import GoodBoyAudioEngine
from persona_engine import (
    ACCESSORIES_LIST,
    SPECIES_LIST,
    STYLES_LIST,
    PersonaProfile,
    get_base_path,
    load_palettes,
    load_presets,
    randomize_persona,
)
from style_renderer import PersonaCanvasRenderer


class FurryPersonaStudio3DApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Furry Persona Studio 3D v3.0 — Realistic 3D Fur & Facial Rig (100% Free)")
        self.geometry("1220x780")
        self.minsize(1080, 720)
        self.configure(bg="#0E0B1A")

        icon_path = os.path.join(get_base_path(), "assets", "icons", "app_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self.palettes = load_palettes()
        self.presets = load_presets()
        self.profile = PersonaProfile.from_dict(self.presets[0]) if self.presets else PersonaProfile()
        self.renderer = PersonaCanvasRenderer()
        self.audio = GoodBoyAudioEngine()

        # 3D camera & facial rig state
        self.yaw = 0.22
        self.pitch = -0.05
        self.mouth_var = tk.DoubleVar(value=28.0)
        self.tongue_var = tk.DoubleVar(value=45.0)
        self.blink_var = tk.DoubleVar(value=100.0)
        self.ear_var = tk.DoubleVar(value=65.0)
        self.twins_mode = False
        self._drag_last = None

        self._build_ui()
        self._sync_ui()
        self._render_3d()

    def _build_ui(self) -> None:
        top = tk.Frame(self, bg="#191430", height=56)
        top.pack(fill="x", side="top")
        tk.Label(
            top,
            text="FURRY PERSONA STUDIO 3D v3.0  |  3D FUR RIG + MOUTH/TONGUE + TWINS (FREE)",
            bg="#191430", fg="#00F5D4", font=("Segoe UI", 12, "bold"), padx=16, pady=12
        ).pack(side="left")

        bar = tk.Frame(top, bg="#191430")
        bar.pack(side="right", padx=10)
        for text, cmd, bg in [
            ("Randomize Persona", self._on_randomize_all, "#7B2CBF"),
            ("Randomize Mouth/Face", self._on_randomize_face, "#F77F00"),
            ("Save JSON", self._on_save_json, "#2A9D8F"),
            ("Load JSON", self._on_load_json, "#3A86FF"),
        ]:
            tk.Button(
                bar, text=text, command=cmd, bg=bg, fg="#FFFFFF",
                font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=6, cursor="hand2"
            ).pack(side="left", padx=4)

        body = tk.Frame(self, bg="#0E0B1A")
        body.pack(fill="both", expand=True, padx=14, pady=12)

        # LEFT PANEL: Species, Styles, Colors, Twins
        left = tk.Frame(body, bg="#1B1633", width=300, padx=14, pady=12)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        tk.Label(left, text="FREE 3D STYLES & SPECIES", bg="#1B1633", fg="#00F5D4", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.vars = {}
        for label, key, vals in [
            ("3D Style (Free)", "style", STYLES_LIST),
            ("Species", "species", SPECIES_LIST),
            ("Accessory", "accessory", ACCESSORIES_LIST),
        ]:
            row = tk.Frame(left, bg="#1B1633")
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, bg="#1B1633", fg="#D5CEF2", font=("Segoe UI", 9, "bold"), width=13, anchor="w").pack(side="left")
            v = tk.StringVar()
            cb = ttk.Combobox(row, textvariable=v, values=vals, state="readonly", width=16)
            cb.pack(side="right", fill="x", expand=True)
            cb.bind("<<ComboboxSelected>>", lambda _e, k=key: self._on_field(k))
            self.vars[key] = v

        tk.Label(left, text="FUR & EYE COLORS", bg="#1B1633", fg="#00F5D4", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(12, 4))
        self.color_btns = {}
        cg = tk.Frame(left, bg="#1B1633")
        cg.pack(fill="x")
        for idx, (lbl, key) in enumerate([("Primary Fur", "primary_color"), ("Muzzle/Belly", "secondary_color"), ("Markings", "accent_color"), ("Eyes", "eye_color")]):
            b = tk.Button(cg, text=lbl, command=lambda k=key: self._pick_color(k), fg="#FFFFFF", font=("Segoe UI", 9, "bold"), relief="flat", pady=6, cursor="hand2")
            b.grid(row=idx // 2, column=idx % 2, padx=4, pady=4, sticky="ew")
            self.color_btns[key] = b
        cg.columnconfigure(0, weight=1)
        cg.columnconfigure(1, weight=1)

        tk.Label(left, text="3D VIEW & TWIN MODE", bg="#1B1633", fg="#00F5D4", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(12, 4))
        self.twins_btn = tk.Button(left, text="Twin Mode: OFF", command=self._toggle_twins, bg="#2C254A", fg="#FFFFFF", font=("Segoe UI", 9, "bold"), relief="flat", pady=7, cursor="hand2")
        self.twins_btn.pack(fill="x", pady=3)
        tk.Button(left, text="Reset 3D Camera", command=self._reset_cam, bg="#2C254A", fg="#FFFFFF", font=("Segoe UI", 9, "bold"), relief="flat", pady=7, cursor="hand2").pack(fill="x", pady=3)

        tk.Label(left, text="STARTER PRESETS", bg="#1B1633", fg="#00F5D4", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(12, 4))
        pf = tk.Frame(left, bg="#1B1633")
        pf.pack(fill="x")
        for idx, pr in enumerate(self.presets):
            tk.Button(pf, text=pr["name"], command=lambda d=pr: self._apply_preset(d), bg="#2C254A", fg="#FFFFFF", font=("Segoe UI", 8, "bold"), relief="flat", pady=4, cursor="hand2").grid(row=idx // 2, column=idx % 2, padx=3, pady=3, sticky="ew")
        pf.columnconfigure(0, weight=1)
        pf.columnconfigure(1, weight=1)

        # CENTER PANEL: 3D Interactive Canvas + GOOD BOY Button
        center = tk.Frame(body, bg="#0E0B1A")
        center.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(center, width=540, height=470, bg="#0B0818", highlightthickness=2, highlightbackground="#00F5D4", cursor="fleur")
        self.canvas.pack(pady=(0, 8))
        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_move)

        tk.Label(center, text="Click & drag on the 3D viewport to rotate 360 degrees!", bg="#0E0B1A", fg="#A89FD0", font=("Segoe UI", 9)).pack(pady=(0, 8))

        gb_card = tk.Frame(center, bg="#281640", highlightbackground="#FF2A85", highlightthickness=2, padx=16, pady=12)
        gb_card.pack(fill="x", padx=12)

        tk.Button(
            gb_card, text="🐾  GOOD BOY  🐾", command=self._on_good_boy,
            bg="#FF2A85", fg="#FFFFFF", activebackground="#FFD166", activeforeground="#120E24",
            font=("Segoe UI", 16, "bold"), relief="flat", pady=10, cursor="hand2"
        ).pack(fill="x")
        self.gb_toast = tk.StringVar(value="Press for completely random audio + 3D mouth/tongue reaction!")
        tk.Label(gb_card, textvariable=self.gb_toast, bg="#281640", fg="#FFD166", font=("Segoe UI", 10, "bold")).pack(pady=(8, 2))
        self.gb_meta = tk.StringVar(value=f"Good Boy Presses: 0  |  Loaded Audio Clips: {len(self.audio.clips)} WAVs")
        tk.Label(gb_card, textvariable=self.gb_meta, bg="#281640", fg="#C9BFE6", font=("Consolas", 9)).pack()

        # RIGHT PANEL: 3D Facial Rig (Mouth, Tongue, Blink, Ears) + Audio Log
        right = tk.Frame(body, bg="#1B1633", width=310, padx=14, pady=12)
        right.pack(side="right", fill="y", padx=(12, 0))
        right.pack_propagate(False)

        tk.Label(right, text="3D FACIAL RIG CONTROLS", bg="#1B1633", fg="#00F5D4", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        for lbl, var in [
            ("Mouth Open / Jaw Hinge (%)", self.mouth_var),
            ("Tongue Stick Out / Blep (%)", self.tongue_var),
            ("Eye Openness / Blink (%)", self.blink_var),
            ("Ear Perked / Swivel (%)", self.ear_var),
        ]:
            tk.Label(right, text=lbl, bg="#1B1633", fg="#D5CEF2", font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(8, 0))
            tk.Scale(
                right, from_=0, to=100, orient="horizontal", variable=var,
                command=lambda _v: self._render_3d(), bg="#1B1633", fg="#00F5D4",
                highlightthickness=0, troughcolor="#0E0B1A", activebackground="#00F5D4"
            ).pack(fill="x")

        qgrid = tk.Frame(right, bg="#1B1633")
        qgrid.pack(fill="x", pady=10)
        for idx, (txt, cmd, col) in enumerate([
            ("Open Mouth", lambda: self._set_rig(92, self.tongue_var.get()), "#2A9D8F"),
            ("Close Mouth", lambda: self._set_rig(0, 0), "#3A86FF"),
            ("Stick Tongue Out", lambda: self._set_rig(68, 100), "#FF2A85"),
            ("Chaos Face", self._on_randomize_face, "#7B2CBF"),
        ]):
            tk.Button(qgrid, text=txt, command=cmd, bg=col, fg="#FFFFFF", font=("Segoe UI", 8, "bold"), relief="flat", pady=6, cursor="hand2").grid(row=idx // 2, column=idx % 2, padx=3, pady=3, sticky="ew")
        qgrid.columnconfigure(0, weight=1)
        qgrid.columnconfigure(1, weight=1)

        tk.Label(right, text="GOOD BOY AUDIO LOG", bg="#1B1633", fg="#FF2A85", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 4))
        self.log_box = tk.Listbox(right, height=10, bg="#0E0B1A", fg="#FFD166", relief="flat", font=("Consolas", 8))
        self.log_box.pack(fill="both", expand=True)

    def _sync_ui(self) -> None:
        for k, v in self.vars.items():
            v.set(getattr(self.profile, k))
        for k, b in self.color_btns.items():
            b.configure(bg=getattr(self.profile, k))

    def _render_3d(self, dx: int = 0, dy: int = 0) -> None:
        self.renderer.render(
            self.canvas,
            self.profile,
            yaw=self.yaw,
            pitch=self.pitch,
            mouth_open=self.mouth_var.get() / 100.0,
            tongue_out=self.tongue_var.get() / 100.0,
            eye_open=self.blink_var.get() / 100.0,
            ear_perk=self.ear_var.get() / 100.0,
            twins=self.twins_mode,
            shake_dx=dx,
            shake_dy=dy,
        )

    def _on_drag_start(self, event) -> None:
        self._drag_last = (event.x, event.y)

    def _on_drag_move(self, event) -> None:
        if self._drag_last:
            dx = event.x - self._drag_last[0]
            dy = event.y - self._drag_last[1]
            self.yaw += dx * 0.015
            self.pitch = max(-0.55, min(0.55, self.pitch + dy * 0.012))
            self._drag_last = (event.x, event.y)
            self._render_3d()

    def _set_rig(self, mouth: float, tongue: float) -> None:
        self.mouth_var.set(mouth)
        self.tongue_var.set(tongue)
        self._render_3d()

    def _on_field(self, key: str) -> None:
        setattr(self.profile, key, self.vars[key].get())
        self._render_3d()

    def _pick_color(self, key: str) -> None:
        chosen = colorchooser.askcolor(color=getattr(self.profile, key))
        if chosen and chosen[1]:
            setattr(self.profile, key, chosen[1])
            self.color_btns[key].configure(bg=chosen[1])
            self._render_3d()

    def _toggle_twins(self) -> None:
        self.twins_mode = not self.twins_mode
        self.twins_btn.configure(text=f"Twin Mode: {'ON' if self.twins_mode else 'OFF'}", bg="#00B4D8" if self.twins_mode else "#2C254A")
        self._render_3d()

    def _reset_cam(self) -> None:
        self.yaw, self.pitch = 0.22, -0.05
        self._render_3d()

    def _apply_preset(self, data: dict) -> None:
        self.profile = PersonaProfile.from_dict(data)
        self._sync_ui()
        self._render_3d()

    def _on_randomize_face(self) -> None:
        self.mouth_var.set(random.randint(0, 100))
        self.tongue_var.set(random.randint(0, 100))
        self.blink_var.set(random.randint(25, 100))
        self.ear_var.set(random.randint(0, 100))
        self._render_3d()

    def _on_randomize_all(self) -> None:
        self.profile = randomize_persona(self.palettes)
        self._sync_ui()
        self._on_randomize_face()

    def _on_good_boy(self) -> None:
        clip_label, toast, count = self.audio.trigger_random_good_boy()
        self.gb_toast.set(f"🔊 {toast} ({clip_label})")
        self.gb_meta.set(f"Good Boy Presses: {count}  |  Last Played: {clip_label}")
        self.log_box.insert(0, f"#{count:02d} -> {clip_label}")
        self.mouth_var.set(random.randint(60, 100))
        self.tongue_var.set(random.randint(65, 100))
        for i, (dx, dy) in enumerate([(-9, 4), (9, -4), (-5, -3), (5, 3), (0, 0)]):
            self.after(i * 42, lambda x=dx, y=dy: self._render_3d(x, y))

    def _on_save_json(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", initialfile="fursona_3d.json", filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.profile.to_dict(), f, indent=2)
            messagebox.showinfo("Saved", f"Saved to {path}")

    def _on_load_json(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.profile = PersonaProfile.from_dict(json.load(f))
            self._sync_ui()
            self._render_3d()


if __name__ == "__main__":
    FurryPersonaStudio3DApp().mainloop()
