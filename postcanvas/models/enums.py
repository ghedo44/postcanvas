from enum import Enum

class Platform(str, Enum):
    INSTAGRAM = "instagram"
    X         = "x"
    TWITTER   = "twitter"
    REDDIT    = "reddit"
    BLOG      = "blog"
    LINKEDIN  = "linkedin"
    FACEBOOK  = "facebook"
    TIKTOK    = "tiktok"
    YOUTUBE   = "youtube"
    CUSTOM    = "custom"

class PostFormat(str, Enum):
    SQUARE    = "square"
    PORTRAIT  = "portrait"
    LANDSCAPE = "landscape"
    STORY     = "story"
    COVER     = "cover"
    BANNER    = "banner"
    CUSTOM    = "custom"

class GradientType(str, Enum):
    LINEAR = "linear"
    RADIAL = "radial"
    CONIC  = "conic"

class ImageFit(str, Enum):
    COVER   = "cover"
    CONTAIN = "contain"
    FILL    = "fill"
    CENTER  = "center"

class TextAlign(str, Enum):
    LEFT    = "left"
    CENTER  = "center"
    RIGHT   = "right"
    JUSTIFY = "justify"

class FontWeight(str, Enum):
    THIN      = "thin"
    LIGHT     = "light"
    REGULAR   = "regular"
    MEDIUM    = "medium"
    SEMIBOLD  = "semibold"
    BOLD      = "bold"
    EXTRABOLD = "extrabold"
    BLACK     = "black"

class ShapeType(str, Enum):
    RECTANGLE         = "rectangle"
    CIRCLE            = "circle"
    ELLIPSE           = "ellipse"
    LINE              = "line"
    ROUNDED_RECTANGLE = "rounded_rectangle"
    TRIANGLE          = "triangle"
    POLYGON           = "polygon"
    STAR              = "star"

class ChartType(str, Enum):
    BAR  = "bar"
    LINE = "line"

class BlendMode(str, Enum):
    NORMAL     = "normal"
    MULTIPLY   = "multiply"
    SCREEN     = "screen"
    OVERLAY    = "overlay"
    DARKEN     = "darken"
    LIGHTEN    = "lighten"
    DIFFERENCE = "difference"
    EXCLUSION  = "exclusion"

class OutputFormat(str, Enum):
    PNG  = "png"
    JPEG = "jpeg"
    JPG  = "jpg"
    WEBP = "webp"

class FilterType(str, Enum):
    NONE       = "none"
    BLUR       = "blur"
    SHARPEN    = "sharpen"
    GRAYSCALE  = "grayscale"
    SEPIA      = "sepia"
    BRIGHTNESS = "brightness"
    CONTRAST   = "contrast"
    SATURATION = "saturation"
    INVERT     = "invert"
    VIGNETTE   = "vignette"

class TextTransform(str, Enum):
    NONE       = "none"
    UPPERCASE  = "uppercase"
    LOWERCASE  = "lowercase"
    CAPITALIZE = "capitalize"

# Dimension type: int/float = absolute px, str "50%" = relative
Dimension = int | float | str
