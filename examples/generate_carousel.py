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


# =============================================================================
# EDITABLE SETTINGS
# Change the values in this section to reuse the carousel for another report.
# =============================================================================

SETTINGS = {
    'output_dir': Path('/mnt/data/apple_10k_carousel/output'),
    'output_name': 'apple_10k_carousel',
    'total_slides': 7,
    'brand_name': 'F / R',
    'brand_tagline': 'REPORT FINANZIARI',
    'company_period': 'APPLE FY2025',
    'source': 'Fonte: Apple FY2025 Form 10-K • USD • Contenuto informativo',
    'signature': 'postcanvas',
}

# Apple FY2025 Form 10-K, USD billions unless otherwise noted.
FINANCIALS = {
    'revenue': [383.285, 391.035, 416.161],
    'net_income': [96.995, 93.736, 112.010],
    'ending_equity': {2022: 50.672, 2023: 62.146, 2024: 56.950, 2025: 73.733},
    'revenue_mix': {
        'iPhone': ('$209,6B', '50,4% dei ricavi totali'),
        'Services': ('$109,2B', '26,2% • segmento a margine più alto'),
        'Wearables': ('$35,7B', ''),
        'Mac': ('$33,7B', ''),
        'iPad': ('$28,0B', ''),
    },
}
FINANCIALS['roe'] = [
    round(
        FINANCIALS['net_income'][0]
        / ((FINANCIALS['ending_equity'][2022] + FINANCIALS['ending_equity'][2023]) / 2)
        * 100
    ),
    round(
        FINANCIALS['net_income'][1]
        / ((FINANCIALS['ending_equity'][2023] + FINANCIALS['ending_equity'][2024]) / 2)
        * 100
    ),
    round(
        FINANCIALS['net_income'][2]
        / ((FINANCIALS['ending_equity'][2024] + FINANCIALS['ending_equity'][2025]) / 2)
        * 100
    ),
]

# All visible copy is centralized here.
SLIDE_COPY = {
    1: {
        'filename': 'apple_10k_01_cover',
        'header_label': 'REPORT PER IL PORTAFOGLIO',
        'title': 'Cosa ha mosso\nApple',
        'subtitle': 'Una lettura chiara di ricavi, margini, mix di business e rischi del FY2025.',
        'cta': 'LEGGI IL REPORT  →',
        'main_metric': '$416,2B',
        'main_metric_label': 'RICAVI FY2025',
        'main_metric_delta': '+6,4% YoY',
        'bubble_1_value': '112',
        'bubble_1_label': 'UTILE',
        'bubble_2_value': '46,9%',
        'bubble_2_label': 'MARGINE LORDO',
        'tagline': 'FINANZA, SENZA RUMORE',
    },
    2: {
        'filename': 'apple_10k_02_summary',
        'header_label': 'SINTESI ESECUTIVA',
        'badge': 'RECORD',
        'metric': '$112,0B',
        'metric_label': 'UTILE NETTO',
        'title': 'Utile netto',
        'subtitle': 'L’utile cresce più dei ricavi e porta il margine netto al 26,9%.',
        'delta': '+19,5%',
        'delta_label': 'anno su anno',
        'summary_title': 'IL REPORT IN BREVE',
        'summary': (
            'Services migliora il mix e la redditività. iPhone pesa ancora circa metà dei ricavi, '
            'mentre i buyback continuano a modificare equity e ROE.'
        ),
    },
    3: {
        'filename': 'apple_10k_03_metrics',
        'header_label': 'NUMERI CHIAVE',
        'title': 'I numeri che contano',
        'subtitle': 'Sei dati per leggere il report FY2025.',
        'left_rows': [
            ('01', 'Ricavi', '$416,2B', '+6,4% YoY'),
            ('02', 'Utile netto', '$112,0B', 'Margine netto 26,9%'),
            ('03', 'Margine lordo', '46,9%', '+0,7 punti percentuali'),
        ],
        'right_rows': [
            ('04', 'Services', '$109,2B', '+14% anno su anno'),
            ('05', 'Buyback', '$90,1B', 'Capitale restituito nel FY2025'),
            ('06', 'Dividendi', '$15,4B', 'Cassa pagata agli azionisti'),
        ],
    },
    4: {
        'filename': 'apple_10k_04_trends',
        'header_label': 'TRE ANNI IN SINTESI',
        'title': 'I ricavi tornano ad accelerare',
        'subtitle': 'Il 2025 rompe la quasi-stasi vista nel 2024.',
        'revenue_label': 'RICAVI',
        'revenue_value': '$416,2B',
        'revenue_delta': '+6,4%',
        'revenue_delta_label': '2025 YoY',
        'profitability_label': 'REDDITIVITÀ',
        'profitability_title': 'L’utile netto accelera più dei ricavi.',
        'profit_values': [('$97,0B', '2023'), ('$93,7B', '2024'), ('$112,0B', '2025')],
    },
    5: {
        'filename': 'apple_10k_05_mix',
        'header_label': 'MIX DEI RICAVI',
        'title': 'Da dove arrivano i ricavi',
        'subtitle': 'Una lettura semplice del mix FY2025.',
        'badge': 'MOTORE PRINCIPALE',
        'focus_value': '50,4%',
        'focus_label': 'QUOTA IPHONE',
        'focus_note': 'Services è la leva più chiara\nper migliorare il mix.',
    },
    6: {
        'filename': 'apple_10k_06_roe',
        'header_label': 'RITORNO SUL CAPITALE',
        'title': 'Il ROE va letto con contesto',
        'subtitle': 'Un rapporto molto alto può raccontare solo una parte della storia.',
        'badge': 'DA LEGGERE BENE',
        'body_title': 'I buyback riducono l’equity contabile.',
        'body': (
            'Un denominatore più piccolo può far apparire il ROE insolitamente alto. '
            'È un segnale di efficienza, non una promessa di rendimento.'
        ),
        'roe_value': '≈171%',
        'roe_label': 'ROE FY2025',
        'roe_note': 'calcolato su equity media',
        'bottom_metrics': [('BUYBACK', '$90,1B'), ('EQUITY FINALE', '$73,7B')],
    },
    7: {
        'filename': 'apple_10k_07_risks',
        'header_label': 'COSA MONITORARE',
        'title': 'Cosa monitorare ora',
        'subtitle': 'Quattro rischi che possono cambiare la qualità del prossimo report.',
        'risk_rows': [
            ('01', 'REGOLAZIONE', 'App Store, antitrust e accordi di distribuzione.'),
            ('02', 'SUPPLY CHAIN', 'Produzione concentrata, componenti, tariffe e geopolitica.'),
            ('03', 'COMPETIZIONE', 'AI, cicli di prodotto e innovazione con margini potenzialmente più bassi.'),
            ('04', 'CINA, FX E MACRO', 'Domanda internazionale, valute e tensioni commerciali.'),
        ],
        'cta': 'SALVA IL REPORT',
        'closing_title': 'Numeri forti.\nAspettative più alte.',
        'closing_body': (
            'Il prossimo test è mantenere crescita e margini mentre aumentano pressione '
            'regolatoria e rischi di supply chain.'
        ),
    },
}

# Typography scale. Increase/decrease these values to resize the entire carousel.
TYPE = {
    'brand': 23,
    'brand_tagline': 16,
    'header_label': 19,
    'page_number': 19,
    'footer': 17,
    'slide_title': 56,
    'slide_subtitle': 25,
    'eyebrow': 20,
    'body': 25,
    'body_small': 21,
    'metric_label': 25,
    'metric_detail': 20,
    'metric_value': 30,
    'large_metric': 76,
    'large_metric_label': 21,
    'large_delta': 30,
    'badge': 21,
}

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

SETTINGS['output_dir'].mkdir(parents=True, exist_ok=True)


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


def decorative_rings(x, y, scale=1.0, dark=False):
    color = GOLD_SOFT if dark else GOLD
    return [
        circle(x, y, 150 * scale, fill=None, stroke=color, stroke_width=max(4, int(7 * scale)), z=1),
        circle(
            x + 95 * scale,
            y + 25 * scale,
            150 * scale,
            fill=None,
            stroke=color,
            stroke_width=max(4, int(7 * scale)),
            z=1,
        ),
    ]


def brand_header(n, total=None, dark=False, right_label=None):
    total = total or SETTINGS['total_slides']
    right_label = right_label or SETTINGS['company_period']
    main = WHITE if dark else INK
    secondary = '#D6D2C8' if dark else MUTED
    shapes = [rect(918, 26, 104, 52, fill=main, radius=26, z=8)]
    texts = [
        text(SETTINGS['brand_name'], 58, 48, TYPE['brand'], main, anchor='left', font=BLACK, letter_spacing=2),
        text(
            SETTINGS['brand_tagline'],
            58,
            82,
            TYPE['brand_tagline'],
            secondary,
            anchor='left',
            font=MED,
            letter_spacing=2,
        ),
        text(right_label, 870, 54, TYPE['header_label'], secondary, anchor='right', font=MED, letter_spacing=1),
        text(
            f'{n}/{total}',
            970,
            52,
            TYPE['page_number'],
            INK if dark else WHITE,
            anchor='center',
            font=BOLD,
        ),
    ]
    return shapes, texts


def footer(dark=False):
    color = '#BEB9AF' if dark else MUTED
    return [
        text(
            SETTINGS['source'],
            58,
            1304,
            TYPE['footer'],
            color,
            anchor='bottomleft',
            font=REG,
        ),
        text(
            SETTINGS['signature'],
            1022,
            1304,
            TYPE['footer'],
            color,
            anchor='bottomright',
            font=MED,
            letter_spacing=1,
        ),
    ]


def metric_row(x, y, width, code, label, value, detail, accent=GOLD):
    return (
        [
            circle(x + 41, y + 41, 82, fill=PAPER_2, stroke=LINE, stroke_width=2, anchor='center', z=2),
            line(x + 102, y + 104, width - 102, 0, LINE, 2, z=2),
        ],
        [
            text(code, x + 41, y + 41, 22, accent, anchor='center', font=BLACK, align='center'),
            text(label, x + 102, y + 2, TYPE['metric_label'], INK, font=BOLD),
            text(
                detail,
                x + 102,
                y + 42,
                TYPE['metric_detail'],
                MUTED,
                font=REG,
                max_width=width - 238,
                line_spacing=1.16,
            ),
            text(value, x + width, y + 12, TYPE['metric_value'], accent, anchor='topright', font=BLACK),
        ],
    )


slides = []

# Slide 1 — Cover
copy = SLIDE_COPY[1]
s1_shapes, s1_texts = brand_header(1, right_label=copy['header_label'])
s1_shapes += decorative_rings(920, 260, 1.05)
s1_shapes += [
    circle(875, 805, 610, fill=INK, z=1),
    circle(875, 805, 430, fill=PAPER_2, stroke=GOLD, stroke_width=10, z=2),
    circle(710, 666, 112, fill=GOLD, z=3),
    circle(987, 972, 140, fill=GOLD_SOFT, z=3),
    rect(58, 642, 230, 66, fill=GOLD, radius=33, z=4),
]
s1_texts += [
    text(copy['title'], 58, 176, 74, INK, max_width=660, font=BLACK, line_spacing=1.00),
    text(
        copy['subtitle'],
        60,
        420,
        30,
        MUTED,
        max_width=600,
        font=REG,
        line_spacing=1.25,
    ),
    text(copy['cta'], 173, 675, TYPE['badge'], WHITE, anchor='center', font=BOLD, letter_spacing=1),
    text(copy['main_metric'], 875, 735, 80, INK, anchor='center', font=BLACK, align='center'),
    text(
        copy['main_metric_label'],
        875,
        825,
        TYPE['large_metric_label'],
        GOLD_DARK,
        anchor='center',
        font=BOLD,
        align='center',
        letter_spacing=2,
    ),
    text(copy['main_metric_delta'], 875, 874, TYPE['large_delta'], INK, anchor='center', font=BOLD, align='center'),
    text(copy['bubble_1_value'], 710, 648, 37, WHITE, anchor='center', font=BLACK),
    text(copy['bubble_1_label'], 710, 691, 15, WHITE, anchor='center', font=BOLD, letter_spacing=1),
    text(copy['bubble_2_value'], 987, 949, 27, INK, anchor='center', font=BLACK),
    text(copy['bubble_2_label'], 987, 986, 13, GOLD_DARK, anchor='center', font=BOLD, letter_spacing=1),
    text(copy['tagline'], 58, 1188, 19, MUTED, font=MED, letter_spacing=1),
    *footer(),
]
slides.append(
    CanvasConfig(
        output_filename=copy['filename'],
        background=BackgroundConfig(color=PAPER),
        shapes=s1_shapes,
        texts=s1_texts,
    )
)

# Slide 2 — Executive summary
copy = SLIDE_COPY[2]
s2_shapes, s2_texts = brand_header(2, right_label=copy['header_label'])
s2_shapes += decorative_rings(110, 480, 0.9)
s2_shapes += [
    circle(350, 388, 390, fill=INK, z=1),
    circle(350, 388, 255, fill=PAPER_2, stroke=GOLD, stroke_width=8, z=2),
    rect(472, 164, 184, 100, fill=GOLD, radius=32, z=4),
    line(548, 782, 390, 0, GOLD, 4, z=2),
]
s2_texts += [
    text(copy['badge'], 564, 214, 34, WHITE, anchor='center', font=BLACK, letter_spacing=1),
    text(copy['metric'], 350, 342, 62, INK, anchor='center', font=BLACK),
    text(copy['metric_label'], 350, 420, 21, GOLD_DARK, anchor='center', font=BOLD, letter_spacing=2),
    text(copy['title'], 666, 295, 34, INK, font=BOLD),
    text(
        copy['subtitle'],
        666,
        354,
        25,
        MUTED,
        max_width=350,
        font=REG,
        line_spacing=1.24,
    ),
    text(copy['delta'], 666, 492, 48, GOLD, font=BLACK),
    text(copy['delta_label'], 668, 551, 21, MUTED, font=REG),
    text(copy['summary_title'], 548, 835, 27, INK, anchor='topcenter', font=BLACK, align='center', letter_spacing=1),
    text(
        copy['summary'],
        548,
        900,
        30,
        MUTED,
        anchor='topcenter',
        max_width=860,
        font=REG,
        align='center',
        line_spacing=1.30,
    ),
    *footer(),
]
slides.append(
    CanvasConfig(
        output_filename=copy['filename'],
        background=BackgroundConfig(color=PAPER),
        shapes=s2_shapes,
        texts=s2_texts,
    )
)

# Slide 3 — Key metrics
copy = SLIDE_COPY[3]
s3_shapes, s3_texts = brand_header(3, right_label=copy['header_label'])
s3_shapes += decorative_rings(910, 126, 0.55)
s3_texts += [
    text(copy['title'], 58, 142, TYPE['slide_title'], INK, font=BLACK),
    text(copy['subtitle'], 60, 222, TYPE['slide_subtitle'], MUTED, font=REG),
]
for idx, row in enumerate(copy['left_rows']):
    sh, tx = metric_row(58, 322 + idx * 235, 450, *row)
    s3_shapes += sh
    s3_texts += tx
for idx, row in enumerate(copy['right_rows']):
    sh, tx = metric_row(570, 322 + idx * 235, 450, *row)
    s3_shapes += sh
    s3_texts += tx
s3_texts += footer()
slides.append(
    CanvasConfig(
        output_filename=copy['filename'],
        background=BackgroundConfig(color=PAPER),
        shapes=s3_shapes,
        texts=s3_texts,
    )
)

# Slide 4 — Trends
copy = SLIDE_COPY[4]
s4_shapes, s4_texts = brand_header(4, right_label=copy['header_label'])
s4_shapes += decorative_rings(930, 225, 0.48)
s4_shapes += [
    rect(58, 310, 964, 430, fill=WHITE, radius=34, stroke=LINE, stroke_width=2, z=1),
    rect(58, 795, 964, 315, fill=PAPER_2, radius=34, z=1),
]
s4_texts += [
    text(copy['title'], 58, 140, TYPE['slide_title'], INK, font=BLACK),
    text(copy['subtitle'], 60, 220, TYPE['slide_subtitle'], MUTED, font=REG),
    text(copy['revenue_label'], 104, 342, TYPE['eyebrow'], GOLD_DARK, font=BOLD, letter_spacing=2),
    text(copy['revenue_value'], 104, 380, 50, INK, font=BLACK),
    text(copy['revenue_delta'], 908, 350, 35, GOLD, anchor='topright', font=BLACK),
    text(copy['revenue_delta_label'], 908, 397, 19, MUTED, anchor='topright', font=REG),
    text(copy['profitability_label'], 104, 838, TYPE['eyebrow'], GOLD_DARK, font=BOLD, letter_spacing=2),
    text(copy['profitability_title'], 104, 887, 32, INK, font=BOLD, max_width=500),
]
profit_x = [114, 385, 656]
for idx, (value, year) in enumerate(copy['profit_values']):
    is_latest = idx == len(copy['profit_values']) - 1
    s4_texts += [
        text(value, profit_x[idx], 996, 32 if is_latest else 28, GOLD if is_latest else MUTED, font=BLACK),
        text(year, profit_x[idx], 1041, 19, MUTED, font=REG),
    ]
s4_texts += footer()
s4_chart = ChartElementConfig(
    type=ChartType.LINE,
    labels=['2023', '2024', '2025'],
    series=[
        ChartSeriesConfig(
            name='Revenue ($B)',
            values=FINANCIALS['revenue'],
            color=GOLD,
            line_width=6,
            point_radius=8,
        )
    ],
    x=104,
    y=450,
    width=870,
    height=245,
    anchor='topleft',
    min_value=370,
    max_value=425,
    grid_steps=3,
    show_legend=False,
    show_points=True,
    line_width=6,
    point_radius=8,
    font_path=REG,
    font_size=21,
    label_color=MUTED,
    axis_color=MUTED,
    grid_color='rgba(119,114,104,0.18)',
    background_color='rgba(255,255,255,0)',
    chart_background_color='rgba(255,255,255,0)',
    border_width=0,
    padding_left=66,
    padding_right=26,
    padding_top=18,
    padding_bottom=52,
)
slides.append(
    CanvasConfig(
        output_filename=copy['filename'],
        background=BackgroundConfig(color=PAPER),
        shapes=s4_shapes,
        texts=s4_texts,
        charts=[s4_chart],
    )
)

# Slide 5 — Revenue mix
copy = SLIDE_COPY[5]
s5_shapes, s5_texts = brand_header(5, right_label=copy['header_label'])
s5_shapes += decorative_rings(172, 1190, 0.75)
s5_shapes += [
    circle(930, 780, 620, fill=INK, z=1),
    circle(930, 780, 415, fill=PAPER_2, stroke=GOLD, stroke_width=10, z=2),
    rect(720, 430, 220, 82, fill=GOLD, radius=32, z=4),
]
s5_texts += [
    text(copy['title'], 58, 142, TYPE['slide_title'], INK, font=BLACK),
    text(copy['subtitle'], 60, 222, TYPE['slide_subtitle'], MUTED, font=REG),
]
list_y = [325, 465, 605, 745, 885]
for idx, (label, (value, detail)) in enumerate(FINANCIALS['revenue_mix'].items()):
    y = list_y[idx]
    s5_texts += [
        text(label, 60, y, 27, INK, font=BOLD),
        text(value, 480, y, 29, GOLD, anchor='topright', font=BLACK),
    ]
    if detail:
        s5_texts.append(text(detail, 60, y + 46, 21, MUTED, font=REG))
s5_texts += [
    text(copy['badge'], 830, 471, 18, WHITE, anchor='center', font=BOLD, letter_spacing=1),
    text(copy['focus_value'], 930, 720, 82, INK, anchor='center', font=BLACK),
    text(copy['focus_label'], 930, 814, 21, GOLD_DARK, anchor='center', font=BOLD, letter_spacing=2),
    text(
        copy['focus_note'],
        930,
        875,
        22,
        MUTED,
        anchor='topcenter',
        max_width=330,
        font=MED,
        align='center',
        line_spacing=1.20,
    ),
    *footer(),
]
for y in (430, 570, 710, 850, 990):
    s5_shapes.append(line(60, y, 420, 0, LINE, 2, z=2))
slides.append(
    CanvasConfig(
        output_filename=copy['filename'],
        background=BackgroundConfig(color=PAPER),
        shapes=s5_shapes,
        texts=s5_texts,
    )
)

# Slide 6 — ROE interpretation
copy = SLIDE_COPY[6]
s6_shapes, s6_texts = brand_header(6, right_label=copy['header_label'])
s6_shapes += decorative_rings(930, 242, 0.9)
s6_shapes += [
    circle(792, 740, 540, fill=INK, z=1),
    circle(792, 740, 350, fill=GOLD_SOFT, stroke=GOLD, stroke_width=9, z=2),
    rect(58, 320, 270, 76, fill=GOLD, radius=30, z=4),
    line(58, 1078, 540, 0, GOLD, 4, z=2),
]
s6_texts += [
    text(copy['title'], 58, 142, TYPE['slide_title'], INK, font=BLACK),
    text(copy['subtitle'], 60, 222, TYPE['slide_subtitle'], MUTED, font=REG, max_width=820),
    text(copy['badge'], 193, 358, TYPE['badge'], WHITE, anchor='center', font=BOLD, letter_spacing=1),
    text(copy['body_title'], 58, 462, 36, INK, font=BLACK, max_width=500),
    text(
        copy['body'],
        58,
        550,
        26,
        MUTED,
        max_width=490,
        font=REG,
        line_spacing=1.30,
    ),
    text(copy['roe_value'], 792, 672, 86, INK, anchor='center', font=BLACK),
    text(copy['roe_label'], 792, 770, 22, GOLD_DARK, anchor='center', font=BOLD, letter_spacing=2),
    text(copy['roe_note'], 792, 822, 20, MUTED, anchor='center', font=REG),
]
metric_x = [58, 365]
for idx, (label, value) in enumerate(copy['bottom_metrics']):
    s6_texts += [
        text(label, metric_x[idx], 1118, 19, GOLD_DARK, font=BOLD, letter_spacing=2),
        text(value, metric_x[idx], 1156, 39, INK, font=BLACK),
    ]
s6_texts += footer()
slides.append(
    CanvasConfig(
        output_filename=copy['filename'],
        background=BackgroundConfig(color=PAPER),
        shapes=s6_shapes,
        texts=s6_texts,
    )
)

# Slide 7 — Risks and conclusion
copy = SLIDE_COPY[7]
s7_shapes, s7_texts = brand_header(7, right_label=copy['header_label'])
s7_shapes += decorative_rings(930, 205, 0.65)
s7_shapes += [
    circle(930, 1095, 610, fill=INK, z=1),
    rect(705, 785, 265, 96, fill=GOLD, radius=34, z=4),
]
s7_texts += [
    text(copy['title'], 58, 142, TYPE['slide_title'], INK, font=BLACK),
    text(copy['subtitle'], 60, 222, TYPE['slide_subtitle'], MUTED, font=REG, max_width=800),
]
for i, (number, title_label, detail) in enumerate(copy['risk_rows']):
    y = 325 + i * 155
    s7_shapes += [
        circle(92, y + 31, 62, fill=PAPER_2, stroke=LINE, stroke_width=2, z=2),
        line(136, y + 84, 492, 0, LINE, 2, z=2),
    ]
    s7_texts += [
        text(number, 92, y + 31, 20, GOLD, anchor='center', font=BLACK),
        text(title_label, 146, y, 22, INK, font=BLACK, letter_spacing=1),
        text(detail, 146, y + 42, 21, MUTED, max_width=470, font=REG, line_spacing=1.18),
    ]
s7_texts += [
    text(copy['cta'], 838, 833, 22, WHITE, anchor='center', font=BLACK, letter_spacing=1),
    text(
        copy['closing_title'],
        830,
        968,
        46,
        WHITE,
        anchor='topcenter',
        max_width=410,
        font=BLACK,
        align='center',
        line_spacing=1.06,
    ),
    text(
        copy['closing_body'],
        830,
        1102,
        23,
        '#C9C5BB',
        anchor='topcenter',
        max_width=390,
        font=REG,
        align='center',
        line_spacing=1.24,
    ),
    *footer(dark=True),
]
slides.append(
    CanvasConfig(
        output_filename=copy['filename'],
        background=BackgroundConfig(color=PAPER),
        shapes=s7_shapes,
        texts=s7_texts,
    )
)

post = instagram_portrait(
    canvases=slides,
    text_font_path=REG,
    output_dir=str(SETTINGS['output_dir']),
    output_filename=SETTINGS['output_name'],
)


if __name__ == '__main__':
    paths = generate(post)
    print('\n'.join(paths))
