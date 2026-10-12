import json
import math
import random
from datetime import datetime

import flet as ft
import flet.canvas as cv

APP_PREFIX = "geometry_calculator_pro"
HISTORY_KEY = f"{APP_PREFIX}.history.v1"

# Internal names stay in English so formula calculations are language-independent.
FORMULAS = {
    "2D Shapes": {
        "Square": {
            "Area": [("Side length", "side")],
            "Perimeter": [("Side length", "side")],
        },
        "Rectangle": {
            "Area": [("Width", "width"), ("Height", "height")],
            "Perimeter": [("Width", "width"), ("Height", "height")],
        },
        "Circle": {
            "Area": [("Radius", "radius")],
            "Circumference": [("Radius", "radius")],
        },
        "Triangle": {
            "Area": [("Base", "base"), ("Perpendicular height", "height")],
            "Perimeter": [("Side A", "a"), ("Side B", "b"), ("Side C", "c")],
        },
        "Parallelogram": {
            "Area": [("Base", "base"), ("Perpendicular height", "height")],
            "Perimeter": [("Side A", "a"), ("Side B", "b")],
        },
        "Trapezoid": {
            "Area": [("First parallel base", "base_a"), ("Second parallel base", "base_b"), ("Perpendicular height", "height")],
            "Perimeter": [("Side A", "a"), ("Side B", "b"), ("Side C", "c"), ("Side D", "d")],
        },
        "Rhombus": {
            "Area": [("Diagonal A", "d1"), ("Diagonal B", "d2")],
            "Perimeter": [("Side length", "side")],
        },
        "Kite": {
            "Area": [("Diagonal A", "d1"), ("Diagonal B", "d2")],
            "Perimeter": [("First side length", "a"), ("Second side length", "b")],
        },
        "Ellipse": {
            "Area": [("First semi-axis", "a"), ("Second semi-axis", "b")],
            "Approximate Perimeter": [("First semi-axis", "a"), ("Second semi-axis", "b")],
        },
        "Regular Polygon": {
            "Area": [("Number of sides (3 or more)", "n"), ("Side length", "side")],
            "Perimeter": [("Number of sides (3 or more)", "n"), ("Side length", "side")],
        },
    },
    "3D Solids": {
        "Cube": {
            "Surface Area": [("Side length", "side")],
            "Volume": [("Side length", "side")],
        },
        "Cuboid": {
            "Surface Area": [("Length", "length"), ("Width", "width"), ("Height", "height")],
            "Volume": [("Length", "length"), ("Width", "width"), ("Height", "height")],
        },
        "Sphere": {
            "Surface Area": [("Radius", "radius")],
            "Volume": [("Radius", "radius")],
        },
        "Cylinder": {
            "Total Surface Area": [("Radius", "radius"), ("Height", "height")],
            "Volume": [("Radius", "radius"), ("Height", "height")],
        },
        "Cone": {
            "Total Surface Area": [("Radius", "radius"), ("Vertical height", "height")],
            "Volume": [("Radius", "radius"), ("Vertical height", "height")],
        },
        "Square Pyramid": {
            "Total Surface Area": [("Base side length", "side"), ("Vertical height", "height")],
            "Volume": [("Base side length", "side"), ("Vertical height", "height")],
        },
    },
}

# Each item is (English, Arabic). Missing translations fall back to the English key.
TEXT = {
    "app_title": ("Geometry Calculator Pro", "حاسبة الهندسة برو"),
    "tagline": ("Understand the formula, not just the answer.", "افهم القانون، مش النتيجة بس."),
    "intro": ("Calculate 2D areas, perimeters and 3D volumes.", "احسب المساحات والمحيطات والحجوم بسهولة."),
    "calculator": ("Calculator", "الحاسبة"),
    "history": ("History", "سجل الحسابات"),
    "practice": ("Practice", "تدريب سريع"),
    "switch_language": ("العربية", "English"),
    "category": ("Category", "الفئة"),
    "2D Shapes": ("2D Shapes", "أشكال مستوية 2D"),
    "3D Solids": ("3D Solids", "مجسمات 3D"),
    "choose_shape": ("Choose a shape", "اختر الشكل الهندسي"),
    "choose_calculation": ("Choose a calculation", "اختر العملية الحسابية"),
    "Side length": ("Side length", "طول الضلع"),
    "Width": ("Width", "العرض"),
    "Height": ("Height", "الارتفاع"),
    "Length": ("Length", "الطول"),
    "Radius": ("Radius", "نصف القطر"),
    "Base": ("Base", "القاعدة"),
    "Perpendicular height": ("Perpendicular height", "الارتفاع العمودي"),
    "Vertical height": ("Vertical height", "الارتفاع الرأسي"),
    "Side A": ("Side A", "الضلع أ"),
    "Side B": ("Side B", "الضلع ب"),
    "Side C": ("Side C", "الضلع ج"),
    "Side D": ("Side D", "الضلع د"),
    "First parallel base": ("First parallel base", "القاعدة المتوازية الأولى"),
    "Second parallel base": ("Second parallel base", "القاعدة المتوازية الثانية"),
    "Diagonal A": ("Diagonal A", "القطر الأول"),
    "Diagonal B": ("Diagonal B", "القطر الثاني"),
    "First side length": ("First side length", "طول الضلع الأول"),
    "Second side length": ("Second side length", "طول الضلع الثاني"),
    "First semi-axis": ("First semi-axis", "نصف المحور الأول"),
    "Second semi-axis": ("Second semi-axis", "نصف المحور الثاني"),
    "Number of sides (3 or more)": ("Number of sides (3 or more)", "عدد الأضلاع (3 أو أكثر)"),
    "Base side length": ("Base side length", "طول ضلع القاعدة"),
    "Square": ("Square", "مربع"),
    "Rectangle": ("Rectangle", "مستطيل"),
    "Circle": ("Circle", "دائرة"),
    "Triangle": ("Triangle", "مثلث"),
    "Parallelogram": ("Parallelogram", "متوازي الأضلاع"),
    "Trapezoid": ("Trapezoid", "شبه منحرف"),
    "Rhombus": ("Rhombus", "معيّن"),
    "Kite": ("Kite", "طائرة ورقية"),
    "Ellipse": ("Ellipse", "قطع ناقص"),
    "Regular Polygon": ("Regular Polygon", "مضلع منتظم"),
    "Cube": ("Cube", "مكعب"),
    "Cuboid": ("Cuboid", "متوازي مستطيلات"),
    "Sphere": ("Sphere", "كرة"),
    "Cylinder": ("Cylinder", "أسطوانة"),
    "Cone": ("Cone", "مخروط"),
    "Square Pyramid": ("Square Pyramid", "هرم رباعي"),
    "Area": ("Area", "المساحة"),
    "Perimeter": ("Perimeter", "المحيط"),
    "Circumference": ("Circumference", "محيط الدائرة"),
    "Approximate Perimeter": ("Approximate Perimeter", "المحيط التقريبي"),
    "Surface Area": ("Surface Area", "المساحة السطحية"),
    "Total Surface Area": ("Total Surface Area", "المساحة السطحية الكلية"),
    "Volume": ("Volume", "الحجم"),
    "calculate": ("Calculate", "احسب"),
    "clear": ("Clear", "مسح"),
    "your_result": ("YOUR RESULT", "النتيجة"),
    "your_answer": ("Your answer will appear here.", "ستظهر النتيجة هنا."),
    "measurements_tip": ("Use the same unit for every measurement.", "استخدم نفس وحدة القياس لكل الأبعاد."),
    "formula_title": ("Formula & explanation", "القانون وشرح الحل"),
    "diagram_title": ("Shape preview", "رسم توضيحي للشكل"),
    "diagram_note": ("Illustration only; not to scale.", "رسم توضيحي فقط، وليس بمقياس رسم."),
    "steps_title": ("How the result was calculated", "خطوات الوصول للنتيجة"),
    "enter_positive": ("Enter a positive number", "أدخل رقمًا موجبًا"),
    "empty_field": ("Please enter a value for: {field}.", "من فضلك أدخل قيمة لـ: {field}."),
    "positive_error": ("All measurements must be positive numbers.", "يجب أن تكون كل القياسات أرقامًا موجبة."),
    "triangle_error": ("These side lengths cannot form a triangle.", "الأطوال دي لا تكوّن مثلثًا."),
    "polygon_error": ("The number of sides must be a whole number of 3 or more.", "عدد الأضلاع لازم يكون عددًا صحيحًا لا يقل عن 3."),
    "formula_hint": ("Put all measurements in the same unit, then substitute them into the formula.", "وحّد وحدة القياس، ثم عوّض بالقيم في القانون."),
    "formula_substitute": ("Values entered", "القيم المدخلة"),
    "unit_area": ("square units", "وحدة مربعة"),
    "unit_volume": ("cubic units", "وحدة مكعبة"),
    "unit_linear": ("units", "وحدة طول"),
    "unit_approx": ("units (approx.)", "وحدة طول (تقريبي)"),
    "no_history": ("No calculations saved yet. Calculate a shape first.", "لا توجد حسابات محفوظة بعد. احسب شكلًا أولًا."),
    "clear_history": ("Clear history", "مسح السجل"),
    "history_cleared": ("Calculation history cleared.", "تم مسح سجل الحسابات."),
    "history_saved_note": ("Recent calculations are saved on this device.", "يتم حفظ أحدث الحسابات على هذا الجهاز."),
    "practice_title": ("Formula challenge", "تحدي القوانين الهندسية"),
    "practice_intro": ("Answer a quick geometry question and build your score.", "جاوب على سؤال هندسة سريع واجمع النقاط."),
    "score": ("Score", "النقاط"),
    "correct": ("Correct! Well done.", "إجابة صحيحة! برافو."),
    "incorrect": ("Not quite. The correct answer is:", "مش بالضبط. الإجابة الصحيحة هي:"),
    "next_question": ("Next question", "السؤال التالي"),
    "practice_again": ("Start another question", "ابدأ سؤالًا جديدًا"),
    "history_empty_confirm": ("Clear all saved calculations?", "هل تريد مسح كل الحسابات المحفوظة؟"),
    "about_note": ("Free learning tool. Always verify important calculations.", "أداة تعليمية مجانية. راجع الحسابات المهمة دائمًا."),
}

SHAPE_SYMBOLS = {
    "Square": "□", "Rectangle": "▱", "Circle": "◯", "Triangle": "△",
    "Parallelogram": "▱", "Trapezoid": "⏢", "Rhombus": "◇", "Kite": "◇",
    "Ellipse": "⬭", "Regular Polygon": "⬡", "Cube": "⬛", "Cuboid": "▰",
    "Sphere": "◉", "Cylinder": "▤", "Cone": "△", "Square Pyramid": "△",
}

FORMULA_TEXT = {
    ("Square", "Area"): "A = s²",
    ("Square", "Perimeter"): "P = 4s",
    ("Rectangle", "Area"): "A = w × h",
    ("Rectangle", "Perimeter"): "P = 2(w + h)",
    ("Circle", "Area"): "A = πr²",
    ("Circle", "Circumference"): "C = 2πr",
    ("Triangle", "Area"): "A = (b × h) / 2",
    ("Triangle", "Perimeter"): "P = a + b + c",
    ("Parallelogram", "Area"): "A = b × h",
    ("Parallelogram", "Perimeter"): "P = 2(a + b)",
    ("Trapezoid", "Area"): "A = ((a + b) × h) / 2",
    ("Trapezoid", "Perimeter"): "P = a + b + c + d",
    ("Rhombus", "Area"): "A = (d₁ × d₂) / 2",
    ("Rhombus", "Perimeter"): "P = 4s",
    ("Kite", "Area"): "A = (d₁ × d₂) / 2",
    ("Kite", "Perimeter"): "P = 2(a + b)",
    ("Ellipse", "Area"): "A = πab",
    ("Ellipse", "Approximate Perimeter"): "P ≈ π(a + b)[1 + 3q/(10 + √(4 − 3q))], q = ((a − b)/(a + b))²",
    ("Regular Polygon", "Area"): "A = n × s² / (4 tan(π/n))",
    ("Regular Polygon", "Perimeter"): "P = n × s",
    ("Cube", "Surface Area"): "SA = 6s²",
    ("Cube", "Volume"): "V = s³",
    ("Cuboid", "Surface Area"): "SA = 2(lw + lh + wh)",
    ("Cuboid", "Volume"): "V = l × w × h",
    ("Sphere", "Surface Area"): "SA = 4πr²",
    ("Sphere", "Volume"): "V = (4/3)πr³",
    ("Cylinder", "Total Surface Area"): "SA = 2πr(r + h)",
    ("Cylinder", "Volume"): "V = πr²h",
    ("Cone", "Total Surface Area"): "SA = πr(r + l), l = √(r² + h²)",
    ("Cone", "Volume"): "V = πr²h / 3",
    ("Square Pyramid", "Total Surface Area"): "SA = s² + 2sl, l = √(h² + (s/2)²)",
    ("Square Pyramid", "Volume"): "V = s²h / 3",
}

QUIZ_QUESTIONS = [
    {
        "question": ("What is the area of a square with side 4?", "ما مساحة مربع طول ضلعه ٤؟"),
        "options": [("16", "16 square units", "١٦ وحدة مربعة"), ("8", "8 square units", "٨ وحدات مربعة"), ("12", "12 square units", "١٢ وحدة مربعة"), ("20", "20 square units", "٢٠ وحدة مربعة")],
        "correct": "16",
    },
    {
        "question": ("What is the volume of a cube with side 3?", "ما حجم مكعب طول ضلعه ٣؟"),
        "options": [("27", "27 cubic units", "٢٧ وحدة مكعبة"), ("9", "9 cubic units", "٩ وحدات مكعبة"), ("18", "18 cubic units", "١٨ وحدة مكعبة"), ("12", "12 cubic units", "١٢ وحدة مكعبة")],
        "correct": "27",
    },
    {
        "question": ("Which formula gives the area of a circle?", "أي قانون يحسب مساحة الدائرة؟"),
        "options": [("pi_r2", "π × r²", "π × نق²"), ("2pir", "2 × π × r", "٢ × π × نق"), ("4s", "4 × side", "٤ × الضلع"), ("lwh", "length × width × height", "الطول × العرض × الارتفاع")],
        "correct": "pi_r2",
    },
    {
        "question": ("A rectangle is 5 by 2. What is its perimeter?", "مستطيل طوله ٥ وعرضه ٢، ما محيطه؟"),
        "options": [("14", "14 units", "١٤ وحدة طول"), ("10", "10 units", "١٠ وحدات طول"), ("7", "7 units", "٧ وحدات طول"), ("12", "12 units", "١٢ وحدة طول")],
        "correct": "14",
    },
    {
        "question": ("What is the volume formula for a cylinder?", "ما قانون حجم الأسطوانة؟"),
        "options": [("cyl_v", "π × r² × h", "π × نق² × ع"), ("2pir", "2 × π × r", "٢ × π × نق"), ("4pir2", "4 × π × r²", "٤ × π × نق²"), ("side3", "side³", "الضلع³")],
        "correct": "cyl_v",
    },
]


def calculate(shape, operation, v):
    """Return the requested measurement for a shape."""
    pi = math.pi

    if shape == "Square":
        return v["side"] ** 2 if operation == "Area" else 4 * v["side"]
    if shape == "Rectangle":
        return v["width"] * v["height"] if operation == "Area" else 2 * (v["width"] + v["height"])
    if shape == "Circle":
        return pi * v["radius"] ** 2 if operation == "Area" else 2 * pi * v["radius"]
    if shape == "Triangle":
        if operation == "Area":
            return (v["base"] * v["height"]) / 2
        a, b, c = v["a"], v["b"], v["c"]
        if a + b <= c or a + c <= b or b + c <= a:
            raise ValueError("triangle_error")
        return a + b + c
    if shape == "Parallelogram":
        return v["base"] * v["height"] if operation == "Area" else 2 * (v["a"] + v["b"])
    if shape == "Trapezoid":
        return ((v["base_a"] + v["base_b"]) * v["height"]) / 2 if operation == "Area" else v["a"] + v["b"] + v["c"] + v["d"]
    if shape == "Rhombus":
        return (v["d1"] * v["d2"]) / 2 if operation == "Area" else 4 * v["side"]
    if shape == "Kite":
        return (v["d1"] * v["d2"]) / 2 if operation == "Area" else 2 * (v["a"] + v["b"])
    if shape == "Ellipse":
        a, b = v["a"], v["b"]
        if operation == "Area":
            return pi * a * b
        q = ((a - b) / (a + b)) ** 2
        return pi * (a + b) * (1 + (3 * q) / (10 + math.sqrt(4 - 3 * q)))
    if shape == "Regular Polygon":
        n_value = v["n"]
        n = int(n_value)
        if n_value != n or n < 3:
            raise ValueError("polygon_error")
        return (n * v["side"] ** 2) / (4 * math.tan(pi / n)) if operation == "Area" else n * v["side"]
    if shape == "Cube":
        return 6 * v["side"] ** 2 if operation == "Surface Area" else v["side"] ** 3
    if shape == "Cuboid":
        l, w, h = v["length"], v["width"], v["height"]
        return 2 * (l * w + l * h + w * h) if operation == "Surface Area" else l * w * h
    if shape == "Sphere":
        r = v["radius"]
        return 4 * pi * r ** 2 if operation == "Surface Area" else (4 / 3) * pi * r ** 3
    if shape == "Cylinder":
        r, h = v["radius"], v["height"]
        return 2 * pi * r * (r + h) if operation == "Total Surface Area" else pi * r ** 2 * h
    if shape == "Cone":
        r, h = v["radius"], v["height"]
        if operation == "Total Surface Area":
            return pi * r * (r + math.sqrt(r ** 2 + h ** 2))
        return pi * r ** 2 * h / 3
    if shape == "Square Pyramid":
        side, height = v["side"], v["height"]
        if operation == "Total Surface Area":
            slant_height = math.sqrt(height ** 2 + (side / 2) ** 2)
            return side ** 2 + 2 * side * slant_height
        return side ** 2 * height / 3
    raise ValueError("Please choose a valid shape and operation.")


def build_shape_canvas(shape):
    """Draw a simple, responsive outline preview for the selected shape."""
    stroke = ft.Paint(color=ft.Colors.TEAL_700, stroke_width=3, style=ft.PaintingStyle.STROKE)
    accent = ft.Paint(color=ft.Colors.BLUE_GREY_500, stroke_width=2, style=ft.PaintingStyle.STROKE)
    shapes = []

    def line(x1, y1, x2, y2, paint=stroke):
        shapes.append(cv.Line(x1, y1, x2, y2, paint=paint))

    if shape == "Square":
        shapes.append(cv.Rect(45, 15, 100, 100, paint=stroke))
    elif shape == "Rectangle":
        shapes.append(cv.Rect(22, 32, 146, 70, paint=stroke))
    elif shape == "Circle":
        shapes.append(cv.Circle(90, 65, 45, paint=stroke))
        line(90, 65, 135, 65, accent)
    elif shape == "Triangle":
        line(90, 12, 145, 112); line(145, 112, 35, 112); line(35, 112, 90, 12)
    elif shape == "Parallelogram":
        line(48, 105, 75, 25); line(75, 25, 145, 25); line(145, 25, 118, 105); line(118, 105, 48, 105)
    elif shape == "Trapezoid":
        line(55, 25, 125, 25); line(125, 25, 155, 105); line(155, 105, 25, 105); line(25, 105, 55, 25)
    elif shape in ("Rhombus", "Kite"):
        line(90, 12, 145, 63); line(145, 63, 90, 115); line(90, 115, 35, 63); line(35, 63, 90, 12)
        line(90, 12, 90, 115, accent); line(35, 63, 145, 63, accent)
    elif shape == "Ellipse":
        shapes.append(cv.Oval(20, 35, 140, 60, paint=stroke))
    elif shape == "Regular Polygon":
        points = [(90, 12), (135, 38), (135, 90), (90, 116), (45, 90), (45, 38)]
        for i, (x, y) in enumerate(points):
            nx, ny = points[(i + 1) % len(points)]
            line(x, y, nx, ny)
    elif shape == "Cube":
        shapes.append(cv.Rect(35, 38, 78, 72, paint=stroke))
        shapes.append(cv.Rect(70, 15, 78, 72, paint=stroke))
        line(35, 38, 70, 15); line(113, 38, 148, 15); line(113, 110, 148, 87)
    elif shape == "Cuboid":
        shapes.append(cv.Rect(25, 42, 105, 65, paint=stroke))
        shapes.append(cv.Rect(57, 20, 105, 65, paint=stroke))
        line(25, 42, 57, 20); line(130, 42, 162, 20); line(130, 107, 162, 85)
    elif shape == "Sphere":
        shapes.append(cv.Circle(90, 65, 45, paint=stroke))
        shapes.append(cv.Oval(47, 43, 86, 44, paint=accent))
    elif shape == "Cylinder":
        shapes.append(cv.Oval(43, 18, 94, 28, paint=stroke))
        line(43, 32, 43, 98); line(137, 32, 137, 98)
        shapes.append(cv.Oval(43, 84, 94, 28, paint=stroke))
    elif shape == "Cone":
        line(90, 14, 40, 100); line(90, 14, 140, 100)
        shapes.append(cv.Oval(40, 83, 100, 30, paint=stroke))
    elif shape == "Square Pyramid":
        line(90, 12, 35, 100); line(90, 12, 145, 100)
        line(35, 100, 60, 116); line(60, 116, 120, 116); line(120, 116, 145, 100); line(145, 100, 35, 100)
        line(90, 12, 60, 116, accent); line(90, 12, 120, 116, accent)
    return cv.Canvas(width=180, height=132, shapes=shapes)


def main(page: ft.Page):
    page.title = "Geometry Calculator Pro"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.TEAL)
    page.bgcolor = ft.Colors.GREY_50
    page.padding = 14

    prefs = ft.SharedPreferences()
    state = {
        "lang": "en",
        "screen": "calculator",
        "mode": "2D Shapes",
        "shape": "Square",
        "operation": "Area",
        "history": [],
        "last_steps": "",
        "quiz_score": 0,
        "quiz_current": None,
        "quiz_answered": False,
        "quiz_feedback": "",
        "quiz_order": [],
    }

    def t(key):
        pair = TEXT.get(key)
        if pair is None:
            return key
        return pair[1] if state["lang"] == "ar" else pair[0]

    def shape_label(key):
        return t(key)

    def unit_for(operation):
        if operation in ("Area", "Surface Area", "Total Surface Area"):
            return t("unit_area")
        if operation == "Volume":
            return t("unit_volume")
        if operation == "Approximate Perimeter":
            return t("unit_approx")
        return t("unit_linear")

    def card(content, bgcolor=ft.Colors.WHITE, padding=16):
        return ft.Container(
            content=content,
            bgcolor=bgcolor,
            padding=padding,
            border_radius=18,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_50),
        )

    brand = ft.Text(t("app_title"), size=21, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    tagline = ft.Text(t("tagline"), size=13, color=ft.Colors.TEAL_100)
    intro = ft.Text(t("intro"), size=12, color=ft.Colors.WHITE)
    body = ft.Column(spacing=13, scroll=ft.ScrollMode.AUTO, expand=True)
    lang_button = ft.Button(content=t("switch_language"), on_click=lambda e: switch_language())

    def nav_button(label_key, screen_key):
        return ft.Button(content=t(label_key), on_click=lambda e: navigate(screen_key))

    nav = ft.Row(
        controls=[nav_button("calculator", "calculator"), nav_button("history", "history"), nav_button("practice", "practice")],
        spacing=8,
        wrap=True,
    )

    header = ft.Container(
        bgcolor=ft.Colors.BLUE_GREY_900,
        border_radius=20,
        padding=18,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Row(controls=[ft.Icon(ft.Icons.CALCULATE, color=ft.Colors.TEAL_200, size=28), brand, lang_button], wrap=True, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                tagline,
                intro,
            ],
        ),
    )

    def update_header():
        brand.value = t("app_title")
        tagline.value = t("tagline")
        intro.value = t("intro")
        lang_button.content = t("switch_language")
        nav.controls = [nav_button("calculator", "calculator"), nav_button("history", "history"), nav_button("practice", "practice")]
        page.rtl = state["lang"] == "ar"

    async def save_history(entry):
        # Load saved entries first so a calculation made immediately after app launch
        # does not overwrite history from a previous session.
        try:
            raw = await prefs.get(HISTORY_KEY)
            stored = json.loads(raw) if raw else []
            history = stored if isinstance(stored, list) else list(state["history"])
        except Exception:
            history = list(state["history"])
        history.insert(0, entry)
        history = history[:60]
        state["history"] = history
        try:
            await prefs.set(HISTORY_KEY, json.dumps(history, ensure_ascii=False))
        except Exception:
            # Keep this session's history visible even if client storage is unavailable.
            pass

    async def load_history():
        try:
            raw = await prefs.get(HISTORY_KEY)
            loaded = json.loads(raw) if raw else []
            if isinstance(loaded, list):
                state["history"] = loaded[:60]
        except Exception:
            state["history"] = state["history"] or []

    def update_page():
        update_header()
        page.update()

    def render_calculator():
        state["screen"] = "calculator"
        mode_options = [ft.DropdownOption(key=k, text=t(k)) for k in FORMULAS]
        selected_mode = state["mode"] if state["mode"] in FORMULAS else "2D Shapes"
        shape_keys = list(FORMULAS[selected_mode].keys())
        selected_shape = state["shape"] if state["shape"] in shape_keys else shape_keys[0]
        operation_keys = list(FORMULAS[selected_mode][selected_shape].keys())
        selected_operation = state["operation"] if state["operation"] in operation_keys else operation_keys[0]
        state["mode"], state["shape"], state["operation"] = selected_mode, selected_shape, selected_operation

        def change_mode(e):
            state["mode"] = e.control.value
            state["shape"] = list(FORMULAS[state["mode"]].keys())[0]
            state["operation"] = list(FORMULAS[state["mode"]][state["shape"]].keys())[0]
            state["last_steps"] = ""
            state.pop("last_calculation", None)
            render_calculator()

        def change_shape(e):
            state["shape"] = e.control.value
            state["operation"] = list(FORMULAS[state["mode"]][state["shape"]].keys())[0]
            state["last_steps"] = ""
            state.pop("last_calculation", None)
            render_calculator()

        def change_operation(e):
            state["operation"] = e.control.value
            state["last_steps"] = ""
            state.pop("last_calculation", None)
            render_calculator()

        mode_dropdown = ft.Dropdown(
            label=t("category"), value=selected_mode, options=mode_options,
            on_select=change_mode, expand=True,
        )
        shape_dropdown = ft.Dropdown(
            label=t("choose_shape"), value=selected_shape,
            options=[ft.DropdownOption(key=k, text=shape_label(k)) for k in shape_keys],
            on_select=change_shape, expand=True,
        )
        operation_dropdown = ft.Dropdown(
            label=t("choose_calculation"), value=selected_operation,
            options=[ft.DropdownOption(key=k, text=t(k)) for k in operation_keys],
            on_select=change_operation, expand=True,
        )

        input_fields = []
        input_controls = []
        for label_key, value_key in FORMULAS[selected_mode][selected_shape][selected_operation]:
            field = ft.TextField(
                label=t(label_key), hint_text=t("enter_positive"),
                keyboard_type=ft.KeyboardType.NUMBER, border_radius=12,
                expand=True,
            )
            field.data = value_key
            input_fields.append(field)
            input_controls.append(field)

        formula = FORMULA_TEXT.get((selected_shape, selected_operation), "")
        explain = ft.Text(t("formula_hint"), size=13, color=ft.Colors.BLUE_GREY_700)
        formula_card = card(ft.Column(
            spacing=8,
            controls=[
                ft.Text(t("formula_title"), size=17, weight=ft.FontWeight.BOLD),
                ft.Text(formula, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.TEAL_900, selectable=True),
                explain,
            ],
        ), bgcolor=ft.Colors.TEAL_50)

        diagram_card = card(ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                ft.Text(t("diagram_title"), size=15, weight=ft.FontWeight.BOLD),
                ft.Container(content=build_shape_canvas(selected_shape), padding=4, border_radius=12, bgcolor=ft.Colors.WHITE),
                ft.Text(shape_label(selected_shape), size=14, weight=ft.FontWeight.BOLD),
                ft.Text(t("diagram_note"), size=11, color=ft.Colors.GREY_600),
            ],
        ), bgcolor=ft.Colors.WHITE)

        result_text = ft.Text(t("your_answer"), size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800, text_align=ft.TextAlign.CENTER)

        def format_steps(shape_name, operation_name, values_used, result_value):
            formula_line = FORMULA_TEXT.get((shape_name, operation_name), "")
            label_values = []
            for label_key, value_key in FORMULAS[state["mode"]][shape_name][operation_name]:
                label_values.append(f"{t(label_key)} = {values_used[value_key]:g}")
            values_line = ", ".join(label_values)
            return f"{t('steps_title')}\n{formula_line}\n{t('formula_substitute')}: {values_line}\n= {result_value:,.4f} {unit_for(operation_name)}"

        steps_text = ft.Text("", size=13, color=ft.Colors.BLUE_GREY_800, selectable=True)
        last_calc = state.get("last_calculation")
        if last_calc and last_calc.get("shape") == selected_shape and last_calc.get("operation") == selected_operation:
            result_text.value = f"{last_calc['result']:,.2f} {unit_for(selected_operation)}"
            steps_text.value = format_steps(selected_shape, selected_operation, last_calc["values"], last_calc["result"])
            state["last_steps"] = steps_text.value

        def clear_fields(e=None):
            for field in input_fields:
                field.value = ""
            state["last_steps"] = ""
            state.pop("last_calculation", None)
            result_text.value = t("your_answer")
            steps_text.value = ""
            page.update()

        async def calculate_clicked(e):
            try:
                values = {}
                for field in input_fields:
                    raw = (field.value or "").strip()
                    raw = raw.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩٫", "0123456789."))
                    raw = raw.replace("٬", "").replace(",", ".")
                    if not raw:
                        raise ValueError(t("empty_field").format(field=field.label))
                    try:
                        number = float(raw)
                    except ValueError as exc:
                        raise ValueError(t("positive_error")) from exc
                    if not math.isfinite(number) or number <= 0:
                        raise ValueError(t("positive_error"))
                    values[field.data] = number

                result = calculate(selected_shape, selected_operation, values)
                result = float(result)
                if not math.isfinite(result):
                    raise ValueError(t("positive_error"))
                unit = unit_for(selected_operation)
                result_display = f"{result:,.2f} {unit}"
                result_text.value = result_display
                result_text.color = ft.Colors.TEAL_900
                state["last_calculation"] = {
                    "shape": selected_shape,
                    "operation": selected_operation,
                    "result": result,
                    "values": values,
                }
                state["last_steps"] = format_steps(selected_shape, selected_operation, values, result)
                steps_text.value = state["last_steps"]

                entry = {
                    "shape": selected_shape,
                    "operation": selected_operation,
                    "result": round(result, 6),
                    "unit": unit,
                    "values": values,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                await save_history(entry)

            except (ValueError, OverflowError) as exc:
                result_text.value = ""
                steps_text.value = str(exc)
                steps_text.color = ft.Colors.RED_700
            else:
                steps_text.color = ft.Colors.BLUE_GREY_800
            page.update()

        form_card = card(ft.Column(
            spacing=12,
            controls=[
                ft.Text(t("choose_calculation"), size=17, weight=ft.FontWeight.BOLD),
                mode_dropdown,
                shape_dropdown,
                operation_dropdown,
                *input_controls,
                ft.Row(
                    controls=[
                        ft.Button(content=t("calculate"), icon=ft.Icons.CALCULATE, on_click=calculate_clicked, expand=True),
                        ft.Button(content=t("clear"), icon=ft.Icons.CLEAR, on_click=clear_fields),
                    ], spacing=8, wrap=True,
                ),
                ft.Text(t("measurements_tip"), size=12, color=ft.Colors.GREY_700),
            ],
        ))

        result_card = card(ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Text(t("your_result"), size=12, color=ft.Colors.TEAL_900, weight=ft.FontWeight.BOLD),
                result_text,
                ft.Divider(),
                steps_text,
            ],
        ), bgcolor=ft.Colors.TEAL_50)

        body.controls = [diagram_card, form_card, formula_card, result_card,
                         ft.Text(t("about_note"), size=11, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)]
        update_page()

    def render_history():
        state["screen"] = "history"
        controls = [ft.Text(t("history"), size=22, weight=ft.FontWeight.BOLD),
                    ft.Text(t("history_saved_note"), size=12, color=ft.Colors.GREY_700)]
        if not state["history"]:
            controls.append(card(ft.Text(t("no_history"), size=14)))
        else:
            for entry in state["history"]:
                shape = entry.get("shape", "")
                operation = entry.get("operation", "")
                created_at = entry.get("created_at", "")
                result = entry.get("result", "")
                unit = unit_for(operation)
                controls.append(card(ft.Column(
                    spacing=5,
                    controls=[
                        ft.Text(f"{shape_label(shape)} · {t(operation)}", size=15, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{result:,.2f} {unit}", size=18, color=ft.Colors.TEAL_900, weight=ft.FontWeight.BOLD),
                        ft.Text(created_at, size=11, color=ft.Colors.GREY_600),
                    ],
                )))
        controls.append(ft.Button(content=t("clear_history"), icon=ft.Icons.DELETE_OUTLINE, on_click=clear_history))
        body.controls = controls
        update_page()

    async def open_history(e=None):
        await load_history()
        render_history()

    async def clear_history(e=None):
        state["history"] = []
        try:
            await prefs.remove(HISTORY_KEY)
        except Exception:
            pass
        render_history()

    def choose_quiz_question():
        q = random.choice(QUIZ_QUESTIONS)
        opts = list(q["options"])
        random.shuffle(opts)
        state["quiz_current"] = q
        state["quiz_order"] = opts
        state["quiz_answered"] = False
        state["quiz_feedback"] = ""
        state["quiz_selected"] = None

    def answer_quiz(option_id):
        if state["quiz_answered"]:
            return
        current = state["quiz_current"]
        state["quiz_answered"] = True
        state["quiz_selected"] = option_id
        if option_id == current["correct"]:
            state["quiz_score"] += 1
            state["quiz_feedback"] = t("correct")
        else:
            correct_opt = next(item for item in current["options"] if item[0] == current["correct"])
            right_text = correct_opt[1] if state["lang"] == "en" else correct_opt[2]
            state["quiz_feedback"] = f"{t('incorrect')} {right_text}"
        render_quiz()

    def next_quiz(e=None):
        state["quiz_current"] = None
        state["quiz_answered"] = False
        choose_quiz_question()
        render_quiz()

    def render_quiz():
        state["screen"] = "practice"
        if state["quiz_current"] is None:
            choose_quiz_question()
        current = state["quiz_current"]
        qtext = current["question"][0] if state["lang"] == "en" else current["question"][1]
        controls = [
            ft.Text(t("practice_title"), size=22, weight=ft.FontWeight.BOLD),
            ft.Text(t("practice_intro"), size=13, color=ft.Colors.GREY_700),
            card(ft.Row(controls=[ft.Icon(ft.Icons.EMOJI_EVENTS, color=ft.Colors.AMBER_700, size=28),
                                  ft.Text(f"{t('score')}: {state['quiz_score']}", size=17, weight=ft.FontWeight.BOLD)])),
            card(ft.Column(spacing=14, controls=[ft.Text(qtext, size=18, weight=ft.FontWeight.BOLD)] + [
                ft.Button(
                    content=(option[1] if state["lang"] == "en" else option[2]),
                    on_click=lambda e, oid=option[0]: answer_quiz(oid),
                    disabled=state["quiz_answered"],
                    expand=True,
                ) for option in state["quiz_order"]
            ])),
        ]
        if state["quiz_feedback"]:
            controls.append(card(ft.Text(state["quiz_feedback"], size=15, weight=ft.FontWeight.BOLD,
                                          color=ft.Colors.TEAL_900 if state["quiz_selected"] == current["correct"] else ft.Colors.BLUE_GREY_800)))
        if state["quiz_answered"]:
            controls.append(ft.Button(content=t("next_question"), icon=ft.Icons.ARROW_FORWARD, on_click=next_quiz, expand=True))
        body.controls = controls
        update_page()

    def navigate(screen_key):
        if screen_key == "calculator":
            render_calculator()
        elif screen_key == "history":
            page.run_task(open_history)
        elif screen_key == "practice":
            render_quiz()

    def switch_language():
        state["lang"] = "ar" if state["lang"] == "en" else "en"
        if state["screen"] == "calculator":
            render_calculator()
        elif state["screen"] == "history":
            render_history()
        else:
            render_quiz()

    page.add(ft.SafeArea(content=ft.Column(controls=[header, nav, body], spacing=12, expand=True)))
    render_calculator()


if __name__ == "__main__":
    ft.run(main)
