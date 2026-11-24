"""Core data models, randomizer, procedural lore generator, and preset management."""

from dataclasses import dataclass, asdict
import hashlib
import json
import os
import random
import sys
from typing import Dict, List


SPECIES_LIST = [
    "Wolf", "Fox", "Cat", "Dragon", "Protogen", "Bunny", "Red Panda", "Hyena"
]

STYLES_LIST = [
    "Cyber-Neon", "Anime Cel", "Retro Pixel", "Pastel Plush", "Comic Ink", "Vaporwave"
]

EXPRESSIONS_LIST = [
    "Happy", "Smug", "Blep", "Fierce", "Sleepy", "Derpy"
]

MARKINGS_LIST = [
    "None", "Stripes", "Spots", "Stars", "Cyber-Circuits", "Galaxy"
]

ACCESSORIES_LIST = [
    "None", "Cyber Visor", "Scarf", "Headphones", "Crown",
    "Bandana", "Round Glasses", "Collar Bell", "Halo"
]

BACKGROUNDS_LIST = [
    "Neon Grid", "Starfield", "Arcade CRT", "Pastel Clouds",
    "Comic Halftone", "Vapor Sunset"
]

NAME_PARTS_A = [
    "Byte", "Mochi", "Cinder", "Nova", "Clover", "Koda", "Vex", "Pixel",
    "Zephyr", "Echo", "Tofu", "Bramble", "Blitz", "Cobalt", "Pebble", "glitch"
]
NAME_PARTS_B = [
    "", "paw", "tail", "spark", "-99", "fang", "whisker", "bean", "wing", "flux"
]

LORE_TEMPLATES = [
    "A {adj} {species} who {hobby} and secretly hoards {hoard}.",
    "Known across the {place} for {hobby}, fueled entirely by {fuel}.",
    "Certified {adj} {species} with a 100% free multi-style license and an obsession with {hoard}.",
    "Spotted at 3 AM in the {place} trying to {hobby} while running on {fuel}."
]
LORE_ADJS = ["chaotic", "cozy", "hyper-caffeinated", "chill", "neon-powered", "sleepy", "dramatic", "wholesome"]
LORE_HOBBIES = [
    "collects vintage synthesizers", "speedruns retro arcade games", "brews questionable iced coffee",
    "writes lo-fi cassette albums", "builds pillow forts", "debugs haunted CRT monitors",
    "trades shiny stickers", "naps in sunbeams"
]
LORE_HOARDS = ["plushies", "mechanical keyboards", "glow-in-the-dark stars", "ramen bowls", "vintage comics", "squeaky toys"]
LORE_PLACES = ["midnight arcade", "cloud cafe", "cyber-alley", "starlight library", "vaporwave mall"]
LORE_FUELS = ["boba tea", "pure chiptune energy", "chamomile tea", "spicy ramen", "thermal paste"]


def get_base_path() -> str:
    """Resolve root directory for both normal execution and PyInstaller bundles."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class PersonaProfile:
    name: str = "Byte"
    species: str = "Wolf"
    style: str = "Cyber-Neon"
    pronouns: str = "they/them"
    primary_color: str = "#2B1E5C"
    secondary_color: str = "#D8F3FF"
    accent_color: str = "#00F5D4"
    eye_color: str = "#FF2A85"
    expression: str = "Smug"
    marking: str = "Cyber-Circuits"
    accessory: str = "Cyber Visor"
    background: str = "Neon Grid"
    bio: str = "Midnight arcade speedrunner who collects broken synths and never sleeps before 4 AM."

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "PersonaProfile":
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)

    def compute_stats(self) -> Dict[str, int]:
        """Deterministically derive fun persona stats from the current build."""
        seed_str = f"{self.name}|{self.species}|{self.style}|{self.expression}|{self.marking}|{self.accessory}"
        digest = hashlib.sha256(seed_str.encode("utf-8")).digest()
        return {
            "Fluffiness": 45 + (digest[0] % 56),
            "Chaos": 30 + (digest[1] % 71),
            "Style": 60 + (digest[2] % 41),
            "Boopability": 50 + (digest[3] % 51),
            "Good Boy Aura": 70 + (digest[4] % 31),
        }


def load_palettes() -> List[Dict]:
    path = os.path.join(get_base_path(), "assets", "palettes", "palettes.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {"name": "Cyber Neon", "primary": "#2B1E5C", "secondary": "#E0F7FA", "accent": "#00F5D4", "eyes": "#FF2A85"}
    ]


def load_presets() -> List[Dict]:
    preset_dir = os.path.join(get_base_path(), "assets", "presets")
    presets = []
    if os.path.isdir(preset_dir):
        for fname in sorted(os.listdir(preset_dir)):
            if fname.endswith(".json"):
                try:
                    with open(os.path.join(preset_dir, fname), "r", encoding="utf-8") as f:
                        presets.append(json.load(f))
                except Exception:
                    pass
    return presets


def generate_random_bio(species: str) -> str:
    tmpl = random.choice(LORE_TEMPLATES)
    return tmpl.format(
        adj=random.choice(LORE_ADJS),
        species=species.lower(),
        hobby=random.choice(LORE_HOBBIES),
        hoard=random.choice(LORE_HOARDS),
        place=random.choice(LORE_PLACES),
        fuel=random.choice(LORE_FUELS),
    )


def randomize_persona(palettes: List[Dict]) -> PersonaProfile:
    species = random.choice(SPECIES_LIST)
    pal = random.choice(palettes) if palettes else {
        "primary": "#2B1E5C", "secondary": "#E0F7FA", "accent": "#00F5D4", "eyes": "#FF2A85"
    }
    name = random.choice(NAME_PARTS_A).capitalize() + random.choice(NAME_PARTS_B)
    return PersonaProfile(
        name=name,
        species=species,
        style=random.choice(STYLES_LIST),
        pronouns=random.choice(["they/them", "he/him", "she/her", "he/they", "she/they", "any/all"]),
        primary_color=pal["primary"],
        secondary_color=pal["secondary"],
        accent_color=pal["accent"],
        eye_color=pal["eyes"],
        expression=random.choice(EXPRESSIONS_LIST),
        marking=random.choice(MARKINGS_LIST),
        accessory=random.choice(ACCESSORIES_LIST),
        background=random.choice(BACKGROUNDS_LIST),
        bio=generate_random_bio(species),
    )
