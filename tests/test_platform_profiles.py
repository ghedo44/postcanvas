from postcanvas.presets import get_profile, instagram_reel_cover, youtube_banner, youtube_thumbnail


def test_profiles_include_export_and_ui_metadata():
    reel = get_profile("instagram_reel_cover")
    assert reel.crop_height == 1350
    assert reel.exclusion_zones
    youtube = get_profile("youtube_thumbnail")
    assert youtube.max_file_size_bytes == 2_000_000


def test_new_profile_helpers_apply_metadata():
    reel = instagram_reel_cover()
    banner = youtube_banner()
    thumbnail = youtube_thumbnail()
    assert reel.profile_name == "instagram_reel_cover"
    assert reel.exclusion_zones
    assert banner.profile_name == "youtube_banner"
    assert banner.max_file_size_bytes == 6_000_000
    assert thumbnail.profile_name == "youtube_thumbnail"
