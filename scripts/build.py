"""Build both Vira families and the standalone comparison from versioned inputs."""

from base64 import b64encode
from pathlib import Path
import re

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


ROOT = Path(__file__).resolve().parents[1]
VERSION = "2.200"
WEIGHTS = {
    100: ("Thin", "نازک"),
    200: ("ExtraLight", "بسیار سبک"),
    300: ("Light", "سبک"),
    400: ("Regular", "معمولی"),
    500: ("Medium", "متوسط"),
    600: ("SemiBold", "نیمه‌ضخیم"),
    700: ("Bold", "ضخیم"),
    800: ("ExtraBold", "بسیار ضخیم"),
    900: ("Black", "سیاه"),
}


def set_names(font, values, language):
    for name_id, value in values.items():
        font["name"].setName(value, name_id, 3, 1, language)


def name_font(font, family, family_fa, weight=None):
    style, style_fa = WEIGHTS[weight or 400]
    # Legacy clients group Regular and Bold. Other weights get distinct legacy
    # family names, while modern clients group all weights using name ID 16.
    legacy_family = family if weight in (None, 400, 700) else f"{family} {style}"
    legacy_family_fa = family_fa if weight in (None, 400, 700) else f"{family_fa} {style_fa}"
    legacy_style = "Bold" if weight == 700 else "Regular"
    legacy_style_fa = "ضخیم" if weight == 700 else "معمولی"
    postscript = f"{family.replace(' ', '')}-{style}"
    set_names(font, {
        1: legacy_family, 2: legacy_style, 3: f"{VERSION};{postscript}",
        4: f"{family} {style}", 5: f"Version {VERSION}", 6: postscript,
        16: family, 17: style,
    }, 0x409)
    set_names(font, {
        1: legacy_family_fa, 2: legacy_style_fa, 4: f"{family_fa} {style_fa}",
        16: family_fa, 17: style_fa,
    }, 0x429)

    if weight is None:
        set_names(font, {25: family.replace(" ", "")}, 0x409)
    else:
        font["name"].removeNames(nameID=25)
        font["OS/2"].usWeightClass = weight
        font["OS/2"].fsSelection &= ~((1 << 5) | (1 << 6))
        font["head"].macStyle &= ~1
        if weight == 700:
            font["OS/2"].fsSelection |= 1 << 5
            font["head"].macStyle |= 1
        elif weight == 400:
            font["OS/2"].fsSelection |= 1 << 6


def save_pair(font, category, basename):
    ttf = ROOT / "fonts" / category / f"{basename}.ttf"
    woff = ROOT / "fonts/web" / category / f"{basename}.woff2"
    for path, flavor in ((ttf, None), (woff, "woff2")):
        path.parent.mkdir(parents=True, exist_ok=True)
        font.flavor = flavor
        font.save(path)
    font.flavor = None


def build_family(family, family_fa, stem, persian_digits):
    font = TTFont(recalcTimestamp=False)
    font.importXML(ROOT / "source/Vira.ttx")
    font["head"].fontRevision = float(VERSION)
    description = font["name"].getDebugName(10)
    note = "Vira 2.2 adds static builds and a Persian-digit family."
    if persian_digits:
        for subtable in font["cmap"].tables:
            if subtable.isUnicode():
                for digit in range(10):
                    for start in (0x30, 0x660):
                        subtable.cmap[start + digit] = subtable.cmap[0x6F0 + digit]
        note += " This FaNum build renders ASCII and Arabic-Indic digits as Persian glyphs."
    set_names(font, {10: f"{note} {description}"}, 0x409)
    name_font(font, family, family_fa)
    save_pair(font, "variable", f"{stem}-Variable")

    # Reload compiled tables so XML-only ValueRecord attributes are absent
    # when fontTools freezes and merges the variation data in GPOS.
    with TTFont(ROOT / "fonts/variable" / f"{stem}-Variable.ttf", recalcTimestamp=False) as compiled:
        for weight, (style, _) in WEIGHTS.items():
            static = instantiateVariableFont(compiled, {"wght": weight})
            name_font(static, family, family_fa, weight)
            save_pair(static, "static", f"{stem}-{style}")


def css_rule(family, category, basename, weight):
    return (
        "@font-face {\n"
        f"  font-family: \"{family}\";\n"
        f"  src: url(\"{category}/{basename}.woff2\") format(\"woff2\");\n"
        "  font-style: normal;\n"
        f"  font-weight: {weight};\n"
        "  font-display: swap;\n"
        "}\n"
    )


def build_css():
    web = ROOT / "fonts/web"
    families = {"Vira": "Vira", "Vira FaNum": "ViraFaNum"}
    variable = [css_rule(family, "variable", stem + "-Variable", "100 900")
                for family, stem in families.items()]
    static = [css_rule(family, "static", f"{stem}-{style}", weight)
              for family, stem in families.items() for weight, (style, _) in WEIGHTS.items()]
    (web / "variable.css").write_text("\n".join(variable), encoding="utf-8", newline="\n")
    (web / "static.css").write_text("\n".join(static), encoding="utf-8", newline="\n")


def build_preview():
    specimen = ROOT / "specimen"
    assets = specimen / "assets"
    web = ROOT / "fonts/web/variable"
    template = (specimen / "preview.template.html").read_text(encoding="utf-8")
    files = {
        "CURRENT": web / "Vira-Variable.woff2",
        "FANUM": web / "ViraFaNum-Variable.woff2",
        "ORIGINAL": assets / "Vira-2.0.woff2",
        "VAZIRMATN": assets / "Vazirmatn-33.003.woff2",
    }
    for size in (14, 16):
        for weight in (400, 600):
            files[f"CAP{size}_{weight}"] = assets / f"ClearType-{size}-{weight}.png"
    for key, path in files.items():
        template = template.replace(f"@{key}@", b64encode(path.read_bytes()).decode("ascii"))
    assert not re.search(r"@[A-Z][A-Z0-9_]+@", template)
    (ROOT / "Preview.html").write_text(template, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    build_family("Vira", "ویرا", "Vira", False)
    build_family("Vira FaNum", "ویرا اعداد فارسی", "ViraFaNum", True)
    build_css()
    build_preview()
