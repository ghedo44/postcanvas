from __future__ import annotations
from ..models import PostConfig, Platform, PostFormat

_SIZES: dict = {
    Platform.INSTAGRAM: {
        PostFormat.SQUARE:    (1080, 1080),
        PostFormat.PORTRAIT:  (1080, 1350),
        PostFormat.LANDSCAPE: (1080,  566),
        PostFormat.STORY:     (1080, 1920),
    },
    Platform.X: {
        PostFormat.SQUARE:    (1080, 1080),
        PostFormat.LANDSCAPE: (1600,  900),
        PostFormat.BANNER:    (1500,  500),
    },
    Platform.REDDIT: {
        PostFormat.LANDSCAPE: (1920, 1080),
        PostFormat.SQUARE:    (1080, 1080),
    },
    Platform.BLOG: {
        PostFormat.LANDSCAPE: (1200, 628),
        PostFormat.COVER:     (1600, 900),
        PostFormat.BANNER:    (2560, 1440),
    },
    Platform.LINKEDIN: {
        PostFormat.SQUARE:    (1080, 1080),
        PostFormat.LANDSCAPE: (1200,  627),
        PostFormat.BANNER:    (1584,  396),
    },
    Platform.FACEBOOK: {
        PostFormat.SQUARE:    (1080, 1080),
        PostFormat.LANDSCAPE: (1200,  630),
        PostFormat.COVER:     ( 820,  312),
        PostFormat.STORY:     (1080, 1920),
    },
    Platform.TIKTOK: {
        PostFormat.STORY:     (1080, 1920),
        PostFormat.SQUARE:    (1080, 1080),
    },
    Platform.YOUTUBE: {
        PostFormat.LANDSCAPE: (1280, 720),
        PostFormat.BANNER:    (2560, 1440),
        PostFormat.COVER:     (1280, 720),
    },
}

def preset(platform: Platform, format: PostFormat = PostFormat.SQUARE, **kwargs) -> PostConfig:
    """Return a PostConfig pre-configured for the given platform + format."""
    w, h = _SIZES.get(platform, {}).get(format, (1080, 1080))
    return PostConfig(platform=platform, format=format, width=w, height=h, **kwargs)

# ── Convenience helpers ───────────────────────────────────────────────────────
def instagram_post(**kw)    -> PostConfig: return preset(Platform.INSTAGRAM, PostFormat.SQUARE,    **kw)
def instagram_portrait(**kw)-> PostConfig: return preset(Platform.INSTAGRAM, PostFormat.PORTRAIT,  **kw)
def instagram_story(**kw)   -> PostConfig: return preset(Platform.INSTAGRAM, PostFormat.STORY,     **kw)
def x_post(**kw)            -> PostConfig: return preset(Platform.X,         PostFormat.LANDSCAPE,  **kw)
def x_banner(**kw)          -> PostConfig: return preset(Platform.X,         PostFormat.BANNER,     **kw)
def reddit_post(**kw)       -> PostConfig: return preset(Platform.REDDIT,    PostFormat.LANDSCAPE,  **kw)
def blog_og(**kw)           -> PostConfig: return preset(Platform.BLOG,      PostFormat.LANDSCAPE,  **kw)
def blog_cover(**kw)        -> PostConfig: return preset(Platform.BLOG,      PostFormat.COVER,      **kw)
def linkedin_post(**kw)     -> PostConfig: return preset(Platform.LINKEDIN,  PostFormat.SQUARE,     **kw)
def youtube_thumbnail(**kw) -> PostConfig: return preset(Platform.YOUTUBE,   PostFormat.LANDSCAPE,  **kw)
def facebook_post(**kw)     -> PostConfig: return preset(Platform.FACEBOOK,  PostFormat.SQUARE,     **kw)
def tiktok_story(**kw)      -> PostConfig: return preset(Platform.TIKTOK,    PostFormat.STORY,      **kw)
