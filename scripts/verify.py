"""Check family metadata, file coverage and shaping for all release weights."""

from io import BytesIO
from pathlib import Path
import re

from fontTools.ttLib import TTFont
import uharfbuzz as hb

from build import FAMILIES, ROOT, VERSION, WEIGHTS


def shaping_font(path, weight=None):
    data = path.read_bytes()
    if path.suffix == ".woff2":
        with TTFont(BytesIO(data), recalcTimestamp=False) as font:
            font.flavor = None
            output = BytesIO()
            font.save(output)
            data = output.getvalue()
    font = hb.Font(hb.Face(data))
    if weight is not None:
        font.set_variations({"wght": weight})
    return font


def shape(font, text, language, direction=None):
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    buffer.language = language
    if direction:
        buffer.direction = direction
    hb.shape(font, buffer, {"tnum": True})
    return [(info.codepoint, position.x_advance, position.x_offset, position.y_offset)
            for info, position in zip(buffer.glyph_infos, buffer.glyph_positions)]


def check_metadata(path, family, weight, persian_digits):
    with TTFont(path, checkChecksums=2) as font:
        assert font["name"].getDebugName(5) == f"Version {VERSION}", path
        assert font["name"].getDebugName(16) == family, path
        assert "The Vazirmatn Project Authors" in font["name"].getDebugName(0), path
        assert len(font.getBestCmap()) >= 300, path
        cmap = font.getBestCmap()
        for digit in range(10):
            for start in (0x30, 0x660):
                assert (cmap[start + digit] == cmap[0x6F0 + digit]) == persian_digits, path
        assert font["prep"].program.getBytecode(), path
        assert font["glyf"][cmap[0x6F0]].program.getBytecode(), path
        if weight is None:
            axes = font["fvar"].axes
            assert [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in axes] == [
                ("wght", 100, 400, 900)], path
            assert all(instance.coordinates["wght"] in WEIGHTS for instance in font["fvar"].instances), path
        else:
            assert all(table not in font for table in ("fvar", "gvar", "HVAR")), path
            assert font["OS/2"].usWeightClass == weight, path
            assert font["name"].getDebugName(17) == WEIGHTS[weight][0], path


def check_family(family, stem, persian_digits):
    fonts = ROOT / "fonts"
    variable = fonts / "variable" / f"{stem}-Variable.ttf"
    web_variable = fonts / "web/variable" / f"{stem}-Variable.woff2"
    for path in (variable, web_variable):
        check_metadata(path, family, None, persian_digits)
    samples = (
        ("همهمه و نامه‌های تازه", "fa"),
        ("پنجره، مبلغ سفارش، گزارش", "fa"),
        ("Settings · Profile", "en"),
        ("0123456789 · 485,000", "en"),
        ("۰۱۲۳۴۵۶۷۸۹ · ۴۸۵٬۰۰۰", "fa"),
    )
    for weight, (style, _) in WEIGHTS.items():
        desktop = fonts / "static" / f"{stem}-{style}.ttf"
        web = fonts / "web/static" / f"{stem}-{style}.woff2"
        for path in (desktop, web):
            check_metadata(path, family, weight, persian_digits)
        vfont = shaping_font(variable, weight)
        others = [shaping_font(path) for path in (desktop, web)]
        others.append(shaping_font(web_variable, weight))
        for text, language in samples:
            expected = shape(vfont, text, language)
            assert all(glyph[0] != 0 for glyph in expected), (family, text, weight)
            assert all(shape(other, text, language) == expected for other in others), (family, text, weight)
        if persian_digits:
            digits = [shape(vfont, seq, "fa", "ltr")
                      for seq in ("0123456789", "۰۱۲۳۴۵۶۷۸۹", "٠١٢٣٤٥٦٧٨٩")]
            assert digits[0] == digits[1] == digits[2], weight


def check_css():
    for basename, count in (("variable.css", 2), ("static.css", 18)):
        css_path = ROOT / "fonts/web" / basename
        urls = re.findall(r'url\("([^"]+)"\)', css_path.read_text(encoding="utf-8"))
        assert len(urls) == count
        assert all((css_path.parent / url).is_file() for url in urls)


if __name__ == "__main__":
    for family, _, stem, persian_digits in FAMILIES:
        check_family(family, stem, persian_digits)
    check_css()
    print("Validated all 40 font binaries, Persian digits, static/variable shaping and CSS links.")
