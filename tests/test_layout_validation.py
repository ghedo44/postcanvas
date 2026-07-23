from postcanvas.models import LayoutPolicyConfig, PaddingConfig, PostConfig, TextConfig
from postcanvas.validation import validate_post


def test_detects_collisions_inside_same_group():
    post = PostConfig(
        width=500,
        height=500,
        layout_policy=LayoutPolicyConfig(
            collision="error",
            safe_area="ignore",
            canvas_bounds="ignore",
        ),
        texts=[
            TextConfig(
                content="One",
                id="one",
                collision_group="content",
                x=50,
                y=50,
                width=200,
                height=100,
                anchor="topleft",
            ),
            TextConfig(
                content="Two",
                id="two",
                collision_group="content",
                x=100,
                y=80,
                width=200,
                height=100,
                anchor="topleft",
            ),
        ],
    )
    report = validate_post(post)[0]
    assert any(issue.code == "collision" for issue in report.errors)


def test_allows_declared_overlap():
    post = PostConfig(
        width=500,
        height=500,
        layout_policy=LayoutPolicyConfig(
            collision="error",
            safe_area="ignore",
            canvas_bounds="ignore",
        ),
        texts=[
            TextConfig(
                content="One",
                id="one",
                collision_group="content",
                allow_overlap_with=["two"],
                x=50,
                y=50,
                width=200,
                height=100,
                anchor="topleft",
            ),
            TextConfig(
                content="Two",
                id="two",
                collision_group="content",
                x=100,
                y=80,
                width=200,
                height=100,
                anchor="topleft",
            ),
        ],
    )
    report = validate_post(post)[0]
    assert not any(issue.code == "collision" for issue in report.issues)


def test_detects_safe_area_violation():
    post = PostConfig(
        width=500,
        height=500,
        safe_area=PaddingConfig.all(50),
        layout_policy=LayoutPolicyConfig(
            collision="ignore",
            safe_area="error",
            canvas_bounds="ignore",
        ),
        texts=[
            TextConfig(
                content="Unsafe",
                id="unsafe",
                x=10,
                y=10,
                width=200,
                height=80,
                anchor="topleft",
            )
        ],
    )
    report = validate_post(post)[0]
    assert any(issue.code == "outside-safe-area" for issue in report.errors)
