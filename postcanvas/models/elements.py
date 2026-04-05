from __future__ import annotations
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
from .enums import ImageFit, BlendMode, ShapeType, ChartType, TextAlign, Dimension
from .primitives import ShadowConfig, BorderConfig, FilterConfig, GradientConfig
from .text import TextConfig

class ImageElementConfig(BaseModel):
    src: str                                 # local path or URL

    # Position & size
    x:      Dimension         = "50%"
    y:      Dimension         = "50%"
    width:  Optional[Dimension] = None       # None = intrinsic
    height: Optional[Dimension] = None
    fit:    ImageFit          = ImageFit.CONTAIN
    anchor: str               = "center"

    # Visual
    border_radius:   float  = 0.0
    opacity:         float  = Field(default=1.0, ge=0.0, le=1.0)
    rotation:        float  = 0.0
    flip_horizontal: bool   = False
    flip_vertical:   bool   = False

    # Adjustments (1.0 = neutral)
    brightness: float = 1.0
    contrast:   float = 1.0
    saturation: float = 1.0

    # Decorations
    shadow: Optional[ShadowConfig] = None
    border: Optional[BorderConfig] = None
    texts:  List[TextConfig]       = Field(default_factory=list)

    # Compositing
    blend_mode: BlendMode = BlendMode.NORMAL
    z_index:    int       = 5
    visible:    bool      = True
    filters:    List[FilterConfig] = Field(default_factory=list)

class ShapeConfig(BaseModel):
    type: ShapeType = ShapeType.RECTANGLE

    # Position & size
    x:      Dimension = 0
    y:      Dimension = 0
    width:  Dimension = 100
    height: Dimension = 100
    anchor: str       = "topleft"

    # Fill
    fill_color:     Optional[str]            = None
    fill_gradient:  Optional[GradientConfig] = None

    # Stroke
    stroke_color: Optional[str] = None
    stroke_width: int           = 0

    # Shape-specific
    border_radius: float              = 0.0       # ROUNDED_RECTANGLE
    sides:         int                = 6         # POLYGON (regular)
    star_points:   int                = 5         # STAR
    star_inner_r:  float              = 0.4       # STAR inner ratio
    points:        Optional[List[Tuple[float, float]]] = None  # POLYGON custom

    # Compositing
    opacity:    float     = Field(default=1.0, ge=0.0, le=1.0)
    rotation:   float     = 0.0
    blend_mode: BlendMode = BlendMode.NORMAL
    z_index:    int       = 1
    visible:    bool      = True
    shadow:     Optional[ShadowConfig] = None
    texts:      List[TextConfig]       = Field(default_factory=list)

class TableElementConfig(BaseModel):
    # Data
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str | int | float]] = Field(default_factory=list)
    column_widths: Optional[List[float]] = None

    # Position & size
    x:      Dimension = "50%"
    y:      Dimension = "50%"
    width:  Dimension = "80%"
    height: Dimension = "45%"
    anchor: str       = "center"

    # Typography
    font_family:      Optional[str] = None
    font_path:        Optional[str] = None
    font_size:        int           = 24
    header_font_size: Optional[int] = None
    cell_align:       TextAlign     = TextAlign.LEFT
    header_align:     TextAlign     = TextAlign.CENTER

    # Colors and framing
    text_color:              str = "#0f172a"
    header_text_color:       str = "#f8fafc"
    background_color:        str = "rgba(248,250,252,0.92)"
    header_background_color: str = "#1e293b"
    row_background_colors:   List[str] = Field(default_factory=lambda: [
        "rgba(241,245,249,0.78)",
        "rgba(226,232,240,0.78)",
    ])
    border_color:  str = "rgba(148,163,184,0.85)"
    border_width:  int = 2
    grid_color:    str = "rgba(148,163,184,0.55)"
    grid_width:    int = 1
    border_radius: float = 14.0

    # Layout controls
    show_header:   bool                = True
    cell_padding:  int                 = 12
    row_height:    Optional[Dimension] = None
    header_height: Optional[Dimension] = None

    # Compositing
    opacity:    float     = Field(default=1.0, ge=0.0, le=1.0)
    rotation:   float     = 0.0
    blend_mode: BlendMode = BlendMode.NORMAL
    z_index:    int       = 6
    visible:    bool      = True
    shadow:     Optional[ShadowConfig] = None

class ChartSeriesConfig(BaseModel):
    name:   Optional[str] = None
    values: List[float]   = Field(default_factory=list)
    color:  Optional[str] = None

    # Applies to line charts (fallback to chart-level values when omitted)
    line_width:   int = 3
    point_radius: int = 4

class ChartElementConfig(BaseModel):
    type:   ChartType = ChartType.BAR
    labels: List[str] = Field(default_factory=list)
    series: List[ChartSeriesConfig] = Field(default_factory=list)

    # Position & size
    x:      Dimension = "50%"
    y:      Dimension = "50%"
    width:  Dimension = "82%"
    height: Dimension = "48%"
    anchor: str       = "center"

    # Typography
    title:           Optional[str] = None
    font_family:     Optional[str] = None
    font_path:       Optional[str] = None
    font_size:       int           = 18
    title_font_size: int           = 26
    label_color:     str           = "#334155"
    title_color:     str           = "#0f172a"

    # Value scale
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    grid_steps: int            = Field(default=4, ge=1, le=12)

    # Chart options
    show_grid:   bool  = True
    show_legend: bool  = True
    show_points: bool  = True
    line_width:  int   = 4
    point_radius: int  = 4
    bar_group_padding: float = Field(default=0.24, ge=0.0, le=0.8)
    bar_radius:        int   = 6
    palette: List[str] = Field(default_factory=lambda: [
        "#0ea5e9",
        "#2563eb",
        "#22c55e",
        "#f97316",
        "#e11d48",
        "#a855f7",
    ])

    # Colors and framing
    background_color:       str           = "rgba(248,250,252,0.92)"
    chart_background_color: Optional[str] = "rgba(255,255,255,0.75)"
    axis_color:             str           = "#475569"
    grid_color:             str           = "rgba(148,163,184,0.42)"
    border_color:           str           = "rgba(148,163,184,0.72)"
    border_width:           int           = 2
    border_radius:          float         = 14.0

    # Plot area padding
    padding_left:   int = 72
    padding_right:  int = 28
    padding_top:    int = 42
    padding_bottom: int = 70

    # Compositing
    opacity:    float     = Field(default=1.0, ge=0.0, le=1.0)
    rotation:   float     = 0.0
    blend_mode: BlendMode = BlendMode.NORMAL
    z_index:    int       = 7
    visible:    bool      = True
    shadow:     Optional[ShadowConfig] = None
