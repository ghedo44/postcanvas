from __future__ import annotations

from typing import Any

from ..models import PaddingConfig, Platform, PlatformProfile, PostConfig, PostFormat

_PROFILES: dict[str, PlatformProfile] = {
    "instagram_square": PlatformProfile(
        name="instagram_square",
        width=1080,
        height=1080,
        safe_area=PaddingConfig.all(64),
        description="Instagram square feed image",
    ),
    "instagram_portrait": PlatformProfile(
        name="instagram_portrait",
        width=1080,
        height=1350,
        safe_area=PaddingConfig.symmetric(vertical=80, horizontal=64),
        description="Instagram portrait feed image",
    ),
    "instagram_story": PlatformProfile(
        name="instagram_story",
        width=1080,
        height=1920,
        safe_area=PaddingConfig(top=250, right=80, bottom=320, left=80),
        description="Instagram Story with conservative UI-safe insets",
    ),
    "instagram_reel_cover": PlatformProfile(
        name="instagram_reel_cover",
        width=1080,
        height=1920,
        safe_area=PaddingConfig(top=250, right=80, bottom=350, left=80),
        crop_width=1080,
        crop_height=1350,
        description="Instagram Reel cover with feed-crop metadata",
    ),
    "x_landscape": PlatformProfile(
        name="x_landscape",
        width=1600,
        height=900,
        safe_area=PaddingConfig.symmetric(vertical=64, horizontal=80),
        description="X landscape post",
    ),
    "x_banner": PlatformProfile(
        name="x_banner",
        width=1500,
        height=500,
        safe_area=PaddingConfig.symmetric(vertical=48, horizontal=120),
        description="X profile banner",
    ),
    "reddit_landscape": PlatformProfile(
        name="reddit_landscape",
        width=1920,
        height=1080,
        safe_area=PaddingConfig.all(80),
        description="Reddit landscape post",
    ),
    "blog_og": PlatformProfile(
        name="blog_og",
        width=1200,
        height=628,
        safe_area=PaddingConfig.symmetric(vertical=48, horizontal=64),
        description="Open Graph landscape image",
    ),
    "linkedin_square": PlatformProfile(
        name="linkedin_square",
        width=1080,
        height=1080,
        safe_area=PaddingConfig.all(64),
        description="LinkedIn square feed image",
    ),
    "linkedin_landscape": PlatformProfile(
        name="linkedin_landscape",
        width=1200,
        height=627,
        safe_area=PaddingConfig.symmetric(vertical=48, horizontal=64),
        description="LinkedIn landscape feed image",
    ),
    "youtube_thumbnail": PlatformProfile(
        name="youtube_thumbnail",
        width=1280,
        height=720,
        safe_area=PaddingConfig.symmetric(vertical=48, horizontal=64),
        description="YouTube thumbnail",
    ),
    "facebook_square": PlatformProfile(
        name="facebook_square",
        width=1080,
        height=1080,
        safe_area=PaddingConfig.all(64),
        description="Facebook square feed image",
    ),
    "facebook_story": PlatformProfile(
        name="facebook_story",
        width=1080,
        height=1920,
        safe_area=PaddingConfig(top=220, right=80, bottom=300, left=80),
        description="Facebook Story",
    ),
    "tiktok_story": PlatformProfile(
        name="tiktok_story",
        width=1080,
        height=1920,
        safe_area=PaddingConfig(top=180, right=140, bottom=320, left=80),
        description="TikTok vertical image with conservative UI-safe insets",
    ),
}

_LEGACY_SIZES: dict[Platform, dict[PostFormat, tuple[int, int]]] = {
    Platform.INSTAGRAM: {
        PostFormat.SQUARE: (1080, 1080),
        PostFormat.PORTRAIT: (1080, 1350),
        PostFormat.LANDSCAPE: (1080, 566),
        PostFormat.STORY: (1080, 1920),
    },
    Platform.X: {
        PostFormat.SQUARE: (1080, 1080),
        PostFormat.LANDSCAPE: (1600, 900),
        PostFormat.BANNER: (1500, 500),
    },
    Platform.REDDIT: {
        PostFormat.LANDSCAPE: (1920, 1080),
        PostFormat.SQUARE: (1080, 1080),
    },
    Platform.BLOG: {
        PostFormat.LANDSCAPE: (1200, 628),
        PostFormat.COVER: (1600, 900),
        PostFormat.BANNER: (2560, 1440),
    },
    Platform.LINKEDIN: {
        PostFormat.SQUARE: (1080, 1080),
        PostFormat.LANDSCAPE: (1200, 627),
        PostFormat.BANNER: (1584, 396),
    },
    Platform.FACEBOOK: {
        PostFormat.SQUARE: (1080, 1080),
        PostFormat.LANDSCAPE: (1200, 630),
        PostFormat.COVER: (820, 312),
        PostFormat.STORY: (1080, 1920),
    },
    Platform.TIKTOK: {
        PostFormat.STORY: (1080, 1920),
        PostFormat.SQUARE: (1080, 1080),
    },
    Platform.YOUTUBE: {
        PostFormat.LANDSCAPE: (1280, 720),
        PostFormat.BANNER: (2560, 1440),
        PostFormat.COVER: (1280, 720),
    },
}

_PAIR_TO_PROFILE: dict[tuple[Platform, PostFormat], str] = {
    (Platform.INSTAGRAM, PostFormat.SQUARE): "instagram_square",
    (Platform.INSTAGRAM, PostFormat.PORTRAIT): "instagram_portrait",
    (Platform.INSTAGRAM, PostFormat.STORY): "instagram_story",
    (Platform.X, PostFormat.LANDSCAPE): "x_landscape",
    (Platform.X, PostFormat.BANNER): "x_banner",
    (Platform.REDDIT, PostFormat.LANDSCAPE): "reddit_landscape",
    (Platform.BLOG, PostFormat.LANDSCAPE): "blog_og",
    (Platform.LINKEDIN, PostFormat.SQUARE): "linkedin_square",
    (Platform.LINKEDIN, PostFormat.LANDSCAPE): "linkedin_landscape",
    (Platform.YOUTUBE, PostFormat.LANDSCAPE): "youtube_thumbnail",
    (Platform.FACEBOOK, PostFormat.SQUARE): "facebook_square",
    (Platform.FACEBOOK, PostFormat.STORY): "facebook_story",
    (Platform.TIKTOK, PostFormat.STORY): "tiktok_story",
}


def get_profile(name: str) -> PlatformProfile:
    try:
        return _PROFILES[name].model_copy(deep=True)
    except KeyError as exc:
        available = ", ".join(sorted(_PROFILES))
        raise KeyError(
            f"Unknown platform profile {name!r}. Available: {available}"
        ) from exc


def list_profiles() -> list[PlatformProfile]:
    return [profile.model_copy(deep=True) for profile in _PROFILES.values()]


def preset(
    platform: Platform,
    format: PostFormat = PostFormat.SQUARE,
    **kwargs: Any,
) -> PostConfig:
    profile_name = _PAIR_TO_PROFILE.get((platform, format))
    if platform == Platform.CUSTOM or format == PostFormat.CUSTOM:
        width = int(kwargs.pop("width", 1080))
        height = int(kwargs.pop("height", 1080))
        return PostConfig(
            platform=platform,
            format=format,
            width=width,
            height=height,
            **kwargs,
        )
    if profile_name is None:
        default_width, default_height = _LEGACY_SIZES.get(platform, {}).get(
            format, (1080, 1080)
        )
        width = int(kwargs.pop("width", default_width))
        height = int(kwargs.pop("height", default_height))
        return PostConfig(
            platform=platform,
            format=format,
            width=width,
            height=height,
            **kwargs,
        )
    profile = get_profile(profile_name)
    kwargs.setdefault("padding", profile.safe_area)
    kwargs.setdefault("safe_area", profile.safe_area)
    return PostConfig(
        platform=platform,
        format=format,
        width=profile.width,
        height=profile.height,
        **kwargs,
    )


def instagram_post(**kwargs: Any) -> PostConfig:
    return preset(Platform.INSTAGRAM, PostFormat.SQUARE, **kwargs)


def instagram_portrait(**kwargs: Any) -> PostConfig:
    return preset(Platform.INSTAGRAM, PostFormat.PORTRAIT, **kwargs)


def instagram_story(**kwargs: Any) -> PostConfig:
    return preset(Platform.INSTAGRAM, PostFormat.STORY, **kwargs)


def instagram_reel_cover(**kwargs: Any) -> PostConfig:
    profile = get_profile("instagram_reel_cover")
    kwargs.setdefault("padding", profile.safe_area)
    kwargs.setdefault("safe_area", profile.safe_area)
    return PostConfig(
        platform=Platform.INSTAGRAM,
        format=PostFormat.STORY,
        width=profile.width,
        height=profile.height,
        **kwargs,
    )


def x_post(**kwargs: Any) -> PostConfig:
    return preset(Platform.X, PostFormat.LANDSCAPE, **kwargs)


def x_banner(**kwargs: Any) -> PostConfig:
    return preset(Platform.X, PostFormat.BANNER, **kwargs)


def reddit_post(**kwargs: Any) -> PostConfig:
    return preset(Platform.REDDIT, PostFormat.LANDSCAPE, **kwargs)


def blog_og(**kwargs: Any) -> PostConfig:
    return preset(Platform.BLOG, PostFormat.LANDSCAPE, **kwargs)


def blog_cover(**kwargs: Any) -> PostConfig:
    return preset(Platform.BLOG, PostFormat.COVER, **kwargs)


def linkedin_post(**kwargs: Any) -> PostConfig:
    return preset(Platform.LINKEDIN, PostFormat.SQUARE, **kwargs)


def youtube_thumbnail(**kwargs: Any) -> PostConfig:
    return preset(Platform.YOUTUBE, PostFormat.LANDSCAPE, **kwargs)


def facebook_post(**kwargs: Any) -> PostConfig:
    return preset(Platform.FACEBOOK, PostFormat.SQUARE, **kwargs)


def tiktok_story(**kwargs: Any) -> PostConfig:
    return preset(Platform.TIKTOK, PostFormat.STORY, **kwargs)
