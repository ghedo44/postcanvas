from __future__ import annotations

from typing import Any

from .models import ExclusionZone, OutputFormat, PaddingConfig, Platform, PlatformProfile, PostConfig, PostFormat


def install() -> None:
    """Enrich platform presets with UI zones, export guidance, and new surfaces."""

    from .presets import platforms

    if getattr(platforms, "_advanced_installed", False):
        return

    def update(name: str, **values: Any) -> None:
        if name in platforms._PROFILES:
            platforms._PROFILES[name] = platforms._PROFILES[name].model_copy(update=values)

    update("instagram_story", exclusion_zones=[
        ExclusionZone(name="story-header", x=0, y=0, width="100%", height=180),
        ExclusionZone(name="story-reply", x=0, y=1660, width="100%", height=260),
    ])
    update("tiktok_story", exclusion_zones=[
        ExclusionZone(name="tiktok-actions", x=900, y=300, width=180, height=1150),
        ExclusionZone(name="tiktok-caption", x=0, y=1500, width="100%", height=420),
    ])
    update("x_banner", exclusion_zones=[
        ExclusionZone(name="profile-avatar", x=40, y=250, width=300, height=250),
    ])
    update("youtube_thumbnail", max_file_size_bytes=2_000_000, recommended_format=OutputFormat.JPEG)

    platforms._PROFILES["instagram_reel_cover"] = PlatformProfile(
        name="instagram_reel_cover",
        width=1080,
        height=1920,
        safe_area=PaddingConfig(top=250, right=80, bottom=350, left=80),
        exclusion_zones=[
            ExclusionZone(name="reel-actions", x=900, y=300, width=180, height=1200),
            ExclusionZone(name="reel-caption", x=0, y=1500, width="100%", height=420),
        ],
        crop_width=1080,
        crop_height=1350,
        description="Instagram Reel cover with feed crop and UI exclusion zones",
    )
    platforms._PROFILES["youtube_banner"] = PlatformProfile(
        name="youtube_banner",
        width=2560,
        height=1440,
        safe_area=PaddingConfig(top=509, right=507, bottom=509, left=507),
        max_file_size_bytes=6_000_000,
        description="YouTube banner with conservative all-device safe region",
    )

    original_preset = platforms.preset

    def preset(platform: Platform, format: PostFormat = PostFormat.SQUARE, **kwargs: Any) -> PostConfig:
        post = original_preset(platform, format, **kwargs)
        profile_name = platforms._PAIR_TO_PROFILE.get((platform, format))
        if not profile_name:
            return post
        profile = platforms.get_profile(profile_name)
        updates: dict[str, Any] = {"profile_name": profile.name}
        if "padding" not in kwargs:
            updates["padding"] = profile.safe_area
        if "safe_area" not in kwargs:
            updates["safe_area"] = profile.safe_area
        if "exclusion_zones" not in kwargs:
            updates["exclusion_zones"] = profile.exclusion_zones
        if "max_file_size_bytes" not in kwargs:
            updates["max_file_size_bytes"] = profile.max_file_size_bytes
        if "output_format" not in kwargs:
            updates["output_format"] = profile.recommended_format
        return post.model_copy(update=updates)

    def instagram_reel_cover(**kwargs: Any) -> PostConfig:
        profile = platforms.get_profile("instagram_reel_cover")
        defaults = dict(
            profile_name=profile.name, width=profile.width, height=profile.height,
            padding=profile.safe_area, safe_area=profile.safe_area,
            exclusion_zones=profile.exclusion_zones,
            max_file_size_bytes=profile.max_file_size_bytes,
            output_format=profile.recommended_format,
        )
        defaults.update(kwargs)
        return PostConfig(platform=Platform.INSTAGRAM, format=PostFormat.STORY, **defaults)

    def youtube_banner(**kwargs: Any) -> PostConfig:
        profile = platforms.get_profile("youtube_banner")
        defaults = dict(
            profile_name=profile.name, width=profile.width, height=profile.height,
            padding=profile.safe_area, safe_area=profile.safe_area,
            exclusion_zones=profile.exclusion_zones,
            max_file_size_bytes=profile.max_file_size_bytes,
            output_format=profile.recommended_format,
        )
        defaults.update(kwargs)
        return PostConfig(platform=Platform.YOUTUBE, format=PostFormat.BANNER, **defaults)

    platforms.preset = preset
    platforms.instagram_reel_cover = instagram_reel_cover
    platforms.youtube_banner = youtube_banner
    platforms._advanced_installed = True
