from pathlib import Path

from postcanvas import generate
from postcanvas.models import (
    BackgroundConfig,
    CanvasConfig,
    ChartElementConfig,
    ChartSeriesConfig,
    ChartType,
    ShapeConfig,
    ShapeType,
    TextConfig,
)
from postcanvas.presets import instagram_portrait


OUT = Path('/mnt/data/apple_10k_carousel/output')
OUT.mkdir(parents=True, exist_ok=True)

# Apple FY2025 Form 10-K, USD billions unless otherwise noted.
revenue = [383.285, 391.035, 416.161]
net_income = [96.995, 93.736, 112.010]
ending_equity = {2022: 50.672, 2023: 62.146, 2024: 56.950, 2025: 73.733}
roe = [
    round(net_income[0] / ((ending_equity[2022] + ending_equity[2023]) / 2) * 100),
    round(net_income[1] / ((ending_equity[2023] + ending_equity[2024]) / 2) * 100),
    round(net_income[2] / ((ending_equity[2024] + ending_equity[2025]) / 2) * 100),
]

REG = '/usr/share/fonts/opentype/inter/Inter-Regular.otf'
MED = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'
BOLD = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
BLACK = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'

# Warm editorial palette inspired by the supplied coffee carousel.
PAPER = '#FCFAF5'
PAPER_2 = '#F5F0E6'
INK = '#1D1D19'
MUTED = '#777268'
GOLD = '#B77E00'
GOLD_DARK = '#946500'
GOLD_SOFT = '#EFE0B7'
LINE = '#DDD5C5'
WHITE = '#FFFFFF'
RUST = '#9A4C3B'


def text(
    content,
    x,
    y,
    size,
    color=INK,
    anchor='topleft',
    max_width=None,
    font=BOLD,
    align='left',
    line_spacing=1.14,
    letter_spacing=0,
    z=10,
):
    return TextConfig(
        content=content,
        x=x,
        y=y,
        font_path=font,
        font_size=size,
        color=color,
        anchor=anchor,
        max_width=max_width,
        align=align,
        line_spacing=line_spacing,
        letter_spacing=letter_spacing,
        z_index=z,
    )


def rect(
    x,
    y,
    w,
    h,
    fill=None,
    radius=0,
    anchor='topleft',
    stroke=None,
    stroke_width=0,
    rotation=0,
    z=1,
):
    return ShapeConfig(
        type=ShapeType.ROUNDED_RECTANGLE if radius else ShapeType.RECTANGLE,
        x=x,
        y=y,
        width=w,
        height=h,
        anchor=anchor,
        fill_color=fill,
        border_radius=radius,
        stroke_color=stroke,
        stroke_width=stroke_width,
        rotation=rotation,
        z_index=z,
    )


def circle(x, y, diameter, fill=None, stroke=None, stroke_width=0, anchor='center', z=1):
    return ShapeConfig(
        type=ShapeType.CIRCLE,
        x=x,
        y=y,
        width=diameter,
        height=diameter,
        anchor=anchor,
        fill_color=fill,
        stroke_color=stroke,
        stroke_width=stroke_width,
        z_index=z,
    )


def line(x, y, w, h=0, color=LINE, width=2, z=2):
    return ShapeConfig(
        type=ShapeType.LINE,
        x=x,
        y=y,
        width=w,
        height=h,
        anchor='topleft',
        fill_color=color,
        stroke_color=color,
        stroke_width=width,
        z_index=z,
    )


def pill(x, y, w, h, label, fill=GOLD, color=WHITE, size=22, anchor='topleft'):
    shape = rect(x, y, w, h, fill=fill, radius=h / 2, anchor=anchor, z=4)
    label_text = text(
        label,
        x + w / 2 if anchor == 'topleft' else x,
        y + h / 2 if anchor == 'topleft' else y,
        size,
        color,
        anchor='center',
        font=BOLD,
        align='center',
        letter_spacing=1,
        z=5,
    )
    return [shape], [label_text]


def decorative_rings(x, y, scale=1.0, dark=False):
    color = GOLD_SOFT if dark else GOLD
    return [
        circle(x, y, 150 * scale, fill=None, stroke=color, stroke_width=max(4, int(7 * scale)), z=1),
        circle(x + 95 * scale, y + 25 * scale, 150 * scale, fill=None, stroke=color, stroke_width=max(4, int(7 * scale)), z=1),
    ]


def brand_header(n, total=7, dark=False, right_label='APPLE FY2025'):
    main = WHITE if dark else INK
    secondary = '#D6D2C8' if dark else MUTED
    shapes = [
        rect(926, 28, 94, 48, fill=main, radius=24, z=8),
    ]
    texts = [
        text('F / R', 58, 48, 20, main, anchor='left', font=BLACK, letter_spacing=2),
        text('FINANCE REPORTS', 58, 78, 13, secondary, anchor='left', font=MED, letter_spacing=2),
        text(right_label, 880, 54, 16, secondary, anchor='right', font=MED, letter_spacing=1),
        text(f'{n}/{total}', 973, 52, 16, INK if dark else WHITE, anchor='center', font=BOLD),
    ]
    return shapes, texts


def footer(n, dark=False):
    color = '#BEB9AF' if dark else MUTED
    return [
        text(
            'Fonte: Apple FY2025 Form 10-K • USD • Contenuto informativo',
            58,
            1304,
            15,
            color,
            anchor='bottomleft',
            font=REG,
        ),
        text('postcanvas', 1022, 1304, 15, color, anchor='bottomright', font=MED, letter_spacing=1),
    ]


def metric_row(x, y, width, code, label, value, detail, accent=GOLD):
    return (
        [
            circle(x + 38, y + 38, 76, fill=PAPER_2, stroke=LINE, stroke_width=2, anchor='center', z=2),
            line(x + 96, y + 96, width - 96, 0, LINE, 2, z=2),
        ],
        [
            text(code, x + 38, y + 38, 20, accent, anchor='center', font=BLACK, align='center'),
            text(label, x + 96, y + 7, 21, INK, font=BOLD),
            text(detail, x + 96, y + 42, 17, MUTED, font=REG, max_width=width - 220),
            text(value, x + width, y + 17, 24, accent, anchor='topright', font=BLACK),
        ],
    )


slides = []

# Slide 1 — Cover: editorial copy + large circular financial motif.
s1_shapes, s1_texts = brand_header(1, dark=False, right_label='REPORT FOR YOUR PORTFOLIO')
s1_shapes += decorative_rings(920, 260, 1.05)
s1_shapes += [
    circle(875, 805, 610, fill=INK, z=1),
    circle(875, 805, 430, fill=PAPER_2, stroke=GOLD, stroke_width=10, z=2),
    circle(710, 666, 112, fill=GOLD, z=3),
    circle(987, 972, 140, fill=GOLD_SOFT, z=3),
    rect(58, 642, 205, 62, fill=GOLD, radius=31, z=4),
]
s1_texts += [
    text('We Know What\nMoved Apple', 58, 186, 64, INK, max_width=640, font=BLACK, line_spacing=1.02),
    text(
        'A clean reading of revenue, margins, business mix and the risks behind FY2025.',
        60,
        405,
        25,
        MUTED,
        max_width=560,
        font=REG,
        line_spacing=1.28,
    ),
    text('READ THE REPORT  →', 161, 673, 18, WHITE, anchor='center', font=BOLD, letter_spacing=1),
    text('$416.2B', 875, 742, 72, INK, anchor='center', font=BLACK, align='center'),
    text('REVENUE FY2025', 875, 824, 19, GOLD_DARK, anchor='center', font=BOLD, align='center', letter_spacing=2),
    text('+6.4% YoY', 875, 868, 25, INK, anchor='center', font=BOLD, align='center'),
    text('112', 710, 651, 33, WHITE, anchor='center', font=BLACK),
    text('NET', 710, 687, 13, WHITE, anchor='center', font=BOLD, letter_spacing=1),
    text('46.9%', 987, 952, 23, INK, anchor='center', font=BLACK),
    text('GROSS MARGIN', 987, 985, 11, GOLD_DARK, anchor='center', font=BOLD, letter_spacing=1),
    text('www.finance-reports.com', 58, 1194, 16, MUTED, font=REG),
    *footer(1),
]
slides.append(
    CanvasConfig(
        output_filename='apple_10k_01_cover',
        background=BackgroundConfig(color=PAPER),
        shapes=s1_shapes,
        texts=s1_texts,
    )
)

# Slide 2 — Record result, inspired by the reference's "New / About" layout.
s2_shapes, s2_texts = brand_header(2, right_label='EXECUTIVE SUMMARY')
s2_shapes += decorative_rings(110, 480, 0.9)
s2_shapes += [
    circle(350, 388, 390, fill=INK, z=1),
    circle(350, 388, 255, fill=PAPER_2, stroke=GOLD, stroke_width=8, z=2),
    rect(472, 170, 170, 92, fill=GOLD, radius=30, z=4),
    line(548, 770, 390, 0, GOLD, 4, z=2),
]
s2_texts += [
    text('RECORD', 557, 215, 30, WHITE, anchor='center', font=BLACK, letter_spacing=1),
    text('$112.0B', 350, 350, 56, INK, anchor='center', font=BLACK),
    text('NET INCOME', 350, 420, 18, GOLD_DARK, anchor='center', font=BOLD, letter_spacing=2),
    text('Net income', 666, 305, 28, INK, font=BOLD),
    text(
        'Profit expanded faster than revenue, lifting net margin to 26.9%.',
        666,
        356,
        20,
        MUTED,
        max_width=330,
        font=REG,
        line_spacing=1.28,
    ),
    text('+19.5%', 666, 476, 40, GOLD, font=BLACK),
    text('year over year', 668, 527, 17, MUTED, font=REG),
    text('ABOUT THE REPORT', 548, 828, 23, INK, anchor='topcenter', font=BLACK, align='center', letter_spacing=1),
    text(
        'Services improved the revenue mix and profitability. iPhone still contributes roughly half of sales, while buybacks continue to reshape equity and ROE.',
        548,
        887,
        25,
        MUTED,
        anchor='topcenter',
        max_width=810,
        font=REG,
        align='center',
        line_spacing=1.34,
    ),
    *footer(2),
]
slides.append(
    CanvasConfig(
        output_filename='apple_10k_02_summary',
        background=BackgroundConfig(color=PAPER),
        shapes=s2_shapes,
        texts=s2_texts,
    )
)

# Slide 3 — Metric menu: two-column list with circular markers and thin dividers.
s3_shapes, s3_texts = brand_header(3, right_label='KEY METRICS')
s3_shapes += decorative_rings(910, 126, 0.55)
s3_texts += [
    text('Our Best Numbers', 58, 148, 47, INK, font=BLACK),
    text('Six data points that frame the FY2025 report.', 60, 214, 20, MUTED, font=REG),
]
left_rows = [
    ('01', 'Revenue', '$416.2B', '+6.4% YoY'),
    ('02', 'Net income', '$112.0B', '26.9% net margin'),
    ('03', 'Gross margin', '46.9%', '+0.7 percentage points'),
]
right_rows = [
    ('04', 'Services', '$109.2B', '+14% year over year'),
    ('05', 'Buybacks', '$90.1B', 'capital returned in FY2025'),
    ('06', 'Dividends', '$15.4B', 'cash paid to shareholders'),
]
for idx, row in enumerate(left_rows):
    sh, tx = metric_row(58, 320 + idx * 235, 450, *row)
    s3_shapes += sh
    s3_texts += tx
for idx, row in enumerate(right_rows):
    sh, tx = metric_row(570, 320 + idx * 235, 450, *row)
    s3_shapes += sh
    s3_texts += tx
s3_texts += footer(3)
slides.append(
    CanvasConfig(
        output_filename='apple_10k_03_metrics',
        background=BackgroundConfig(color=PAPER),
        shapes=s3_shapes,
        texts=s3_texts,
    )
)

# Slide 4 — Trend charts, kept intentionally spare and flat.
s4_shapes, s4_texts = brand_header(4, right_label='THREE-YEAR TREND')
s4_shapes += decorative_rings(930, 225, 0.48)
s4_shapes += [
    rect(58, 300, 964, 430, fill=WHITE, radius=34, stroke=LINE, stroke_width=2, z=1),
    rect(58, 790, 964, 315, fill=PAPER_2, radius=34, z=1),
]
s4_texts += [
    text('Revenue Keeps Climbing', 58, 145, 47, INK, font=BLACK),
    text('The 2025 result breaks the near-flat growth seen in 2024.', 60, 211, 20, MUTED, font=REG),
    text('REVENUE', 104, 332, 16, GOLD_DARK, font=BOLD, letter_spacing=2),
    text('$416.2B', 104, 365, 42, INK, font=BLACK),
    text('+6.4%', 908, 346, 29, GOLD, anchor='topright', font=BLACK),
    text('2025 YoY', 908, 387, 15, MUTED, anchor='topright', font=REG),
    text('PROFITABILITY', 104, 835, 16, GOLD_DARK, font=BOLD, letter_spacing=2),
    text('Net income accelerated faster than sales.', 104, 880, 28, INK, font=BOLD, max_width=420),
    text('$97.0B', 114, 980, 24, MUTED, font=BLACK),
    text('2023', 114, 1018, 15, MUTED, font=REG),
    text('$93.7B', 385, 980, 24, MUTED, font=BLACK),
    text('2024', 385, 1018, 15, MUTED, font=REG),
    text('$112.0B', 656, 980, 29, GOLD, font=BLACK),
    text('2025', 656, 1022, 15, MUTED, font=REG),
    *footer(4),
]
s4_chart = ChartElementConfig(
    type=ChartType.LINE,
    labels=['2023', '2024', '2025'],
    series=[ChartSeriesConfig(name='Revenue ($B)', values=revenue, color=GOLD, line_width=6, point_radius=8)],
    x=104,
    y=425,
    width=870,
    height=255,
    anchor='topleft',
    min_value=370,
    max_value=425,
    grid_steps=3,
    show_legend=False,
    show_points=True,
    line_width=6,
    point_radius=8,
    font_path=REG,
    font_size=18,
    label_color=MUTED,
    axis_color=MUTED,
    grid_color='rgba(119,114,104,0.18)',
    background_color='rgba(255,255,255,0)',
    chart_background_color='rgba(255,255,255,0)',
    border_width=0,
    padding_left=60,
    padding_right=26,
    padding_top=18,
    padding_bottom=48,
)
slides.append(
    CanvasConfig(
        output_filename='apple_10k_04_trends',
        background=BackgroundConfig(color=PAPER),
        shapes=s4_shapes,
        texts=s4_texts,
        charts=[s4_chart],
    )
)

# Slide 5 — Revenue mix: list + large cropped circular focus.
s5_shapes, s5_texts = brand_header(5, right_label='REVENUE MIX')
s5_shapes += decorative_rings(172, 1190, 0.75)
s5_shapes += [
    circle(930, 780, 620, fill=INK, z=1),
    circle(930, 780, 415, fill=PAPER_2, stroke=GOLD, stroke_width=10, z=2),
    rect(735, 438, 195, 76, fill=GOLD, radius=30, z=4),
]
s5_texts += [
    text('Where Revenue Comes From', 58, 148, 47, INK, font=BLACK),
    text('A simple view of the FY2025 business mix.', 60, 214, 20, MUTED, font=REG),
    text('iPhone', 60, 330, 23, INK, font=BOLD),
    text('$209.6B', 470, 330, 24, GOLD, anchor='topright', font=BLACK),
    text('50.4% of total revenue', 60, 372, 18, MUTED, font=REG),
    text('Services', 60, 470, 23, INK, font=BOLD),
    text('$109.2B', 470, 470, 24, GOLD, anchor='topright', font=BLACK),
    text('26.2% • highest-margin segment', 60, 512, 18, MUTED, font=REG),
    text('Wearables', 60, 610, 23, INK, font=BOLD),
    text('$35.7B', 470, 610, 24, GOLD, anchor='topright', font=BLACK),
    text('Mac', 60, 750, 23, INK, font=BOLD),
    text('$33.7B', 470, 750, 24, GOLD, anchor='topright', font=BLACK),
    text('iPad', 60, 890, 23, INK, font=BOLD),
    text('$28.0B', 470, 890, 24, GOLD, anchor='topright', font=BLACK),
    text('CORE ENGINE', 832, 476, 18, WHITE, anchor='center', font=BOLD, letter_spacing=1),
    text('50.4%', 930, 730, 70, INK, anchor='center', font=BLACK),
    text('IPHONE SHARE', 930, 808, 18, GOLD_DARK, anchor='center', font=BOLD, letter_spacing=2),
    text('Services is now the clearest\nsource of mix improvement.', 930, 870, 17, MUTED, anchor='topcenter', max_width=290, font=MED, align='center', line_spacing=1.18),
    *footer(5),
]
for y in (425, 565, 705, 845, 985):
    s5_shapes.append(line(60, y, 410, 0, LINE, 2, z=2))
slides.append(
    CanvasConfig(
        output_filename='apple_10k_05_mix',
        background=BackgroundConfig(color=PAPER),
        shapes=s5_shapes,
        texts=s5_texts,
    )
)

# Slide 6 — ROE interpretation with one strong circular number.
s6_shapes, s6_texts = brand_header(6, right_label='RETURN ON EQUITY')
s6_shapes += decorative_rings(930, 242, 0.9)
s6_shapes += [
    circle(792, 740, 540, fill=INK, z=1),
    circle(792, 740, 350, fill=GOLD_SOFT, stroke=GOLD, stroke_width=9, z=2),
    rect(58, 320, 255, 72, fill=GOLD, radius=28, z=4),
    line(58, 1078, 520, 0, GOLD, 4, z=2),
]
s6_texts += [
    text('ROE Needs Context', 58, 148, 47, INK, font=BLACK),
    text('A very high ratio can still tell an incomplete story.', 60, 214, 20, MUTED, font=REG),
    text('READ CAREFULLY', 185, 356, 18, WHITE, anchor='center', font=BOLD, letter_spacing=1),
    text('Buybacks reduce book equity.', 58, 465, 31, INK, font=BLACK, max_width=460),
    text(
        'That smaller denominator can make return on equity look unusually high. It is a useful efficiency signal, not a promise of investment returns.',
        58,
        540,
        22,
        MUTED,
        max_width=470,
        font=REG,
        line_spacing=1.34,
    ),
    text('≈171%', 792, 680, 74, INK, anchor='center', font=BLACK),
    text('ROE FY2025', 792, 766, 19, GOLD_DARK, anchor='center', font=BOLD, letter_spacing=2),
    text('based on average equity', 792, 814, 17, MUTED, anchor='center', font=REG),
    text('BUYBACK', 58, 1120, 16, GOLD_DARK, font=BOLD, letter_spacing=2),
    text('$90.1B', 58, 1152, 34, INK, font=BLACK),
    text('ENDING EQUITY', 350, 1120, 16, GOLD_DARK, font=BOLD, letter_spacing=2),
    text('$73.7B', 350, 1152, 34, INK, font=BLACK),
    *footer(6),
]
slides.append(
    CanvasConfig(
        output_filename='apple_10k_06_roe',
        background=BackgroundConfig(color=PAPER),
        shapes=s6_shapes,
        texts=s6_texts,
    )
)

# Slide 7 — Risks and conclusion, echoing the reference's final CTA panel.
s7_shapes, s7_texts = brand_header(7, right_label='WHAT TO WATCH')
s7_shapes += decorative_rings(930, 205, 0.65)
s7_shapes += [
    circle(930, 1095, 610, fill=INK, z=1),
    rect(720, 790, 235, 92, fill=GOLD, radius=32, z=4),
]
s7_texts += [
    text('What To Watch Next', 58, 148, 47, INK, font=BLACK),
    text('Four risks that can change the quality of the next report.', 60, 214, 20, MUTED, font=REG),
]
risk_rows = [
    ('01', 'REGULATION', 'App Store rules, antitrust and distribution agreements.'),
    ('02', 'SUPPLY CHAIN', 'Production concentration, components, tariffs and geopolitics.'),
    ('03', 'COMPETITION', 'AI, product cycles and innovation that may carry lower margins.'),
    ('04', 'CHINA, FX & MACRO', 'International demand, currencies and trade tension.'),
]
for i, (number, title_label, detail) in enumerate(risk_rows):
    y = 325 + i * 155
    s7_shapes += [
        circle(92, y + 28, 56, fill=PAPER_2, stroke=LINE, stroke_width=2, z=2),
        line(132, y + 79, 488, 0, LINE, 2, z=2),
    ]
    s7_texts += [
        text(number, 92, y + 28, 17, GOLD, anchor='center', font=BLACK),
        text(title_label, 142, y, 19, INK, font=BLACK, letter_spacing=1),
        text(detail, 142, y + 37, 18, MUTED, max_width=450, font=REG, line_spacing=1.2),
    ]
s7_texts += [
    text('SAVE REPORT', 837, 836, 22, WHITE, anchor='center', font=BLACK, letter_spacing=1),
    text('Strong numbers.\nHigher expectations.', 830, 976, 39, WHITE, anchor='topcenter', max_width=390, font=BLACK, align='center', line_spacing=1.08),
    text(
        'The next test is sustaining growth and margins while regulation and supply-chain pressure rise.',
        830,
        1095,
        20,
        '#C9C5BB',
        anchor='topcenter',
        max_width=370,
        font=REG,
        align='center',
        line_spacing=1.28,
    ),
    *footer(7, dark=True),
]
slides.append(
    CanvasConfig(
        output_filename='apple_10k_07_risks',
        background=BackgroundConfig(color=PAPER),
        shapes=s7_shapes,
        texts=s7_texts,
    )
)

post = instagram_portrait(
    canvases=slides,
    text_font_path=REG,
    output_dir=str(OUT),
    output_filename='apple_10k_carousel',
)


if __name__ == '__main__':
    paths = generate(post)
    print('\n'.join(paths))
