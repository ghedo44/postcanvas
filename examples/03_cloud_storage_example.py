"""
Cloud Storage Integration Example

This example demonstrates how to use postcanvas with cloud storage.
Three common approaches are shown:

1. Generate and save to local disk (default behavior)
2. Generate without saving, get raw PIL Images for custom handling
3. Generate and upload to cloud (AWS S3 example)
"""

from postcanvas import generate, image_to_bytes, save_image_to_path, GenerateResult
from postcanvas.presets import instagram_post, instagram_story
from postcanvas.models import (
    BackgroundConfig,
    TextConfig,
    OutputFormat,
    ShadowConfig,
)


# ─── Setup: Create a simple post config ──────────────────────────────────────
def create_simple_post():
    """Create a basic Instagram post for demonstration."""
    return instagram_post(
        background=BackgroundConfig(color="#1a1a2e"),
        texts=[
            TextConfig(
                content="Cloud Storage Ready!",
                y="50%",
                font_size=96,
                color="#e94560",
                shadow=ShadowConfig(blur_radius=12),
            )
        ],
        output_dir="./output/cloud_examples",
    )


# ─── Approach 1: Default behavior (save to disk) ──────────────────────────────
def example_local_save():
    """Default behavior - saves to local disk and returns file paths."""
    print("\n🔹 Example 1: Local save (default behavior)")
    post = create_simple_post()

    # This is the default behavior - backward compatible
    paths = generate(post)
    print(f"Saved files: {paths}")
    return paths


# ─── Approach 2: Get raw images without saving ──────────────────────────────
def example_return_raw_images():
    """Generate images without saving to disk, get PIL Image objects."""
    print("\n🔹 Example 2: Return raw images (no disk save)")
    post = create_simple_post()

    # Generate images without saving to disk
    images = generate(post, save=False, return_images=True)
    print(f"Generated {len(images)} image(s) (PIL Image objects)")

    # Now you can process these images any way you want
    for i, img in enumerate(images):
        print(f"  Image {i+1}: {img.size} pixels, mode: {img.mode}")

        # Convert to bytes for storage
        data = image_to_bytes(img, format=OutputFormat.PNG)
        print(f"  → Bytes size: {len(data)} bytes")

    return images


# ─── Approach 3: Get both paths and images ────────────────────────────────────
def example_save_and_get_images():
    """Save to disk AND get PIL Image objects."""
    print("\n🔹 Example 3: Save to disk and get images")
    post = create_simple_post()

    # Generate, save to disk, AND return GenerateResult
    result = generate(post, save=True, return_images=True)

    # result is a GenerateResult dataclass with guaranteed structure
    assert isinstance(result, GenerateResult), "Expected GenerateResult when both save and return_images are True"
    
    print(f"Result: {result}")  # Nice repr: "GenerateResult(1 image(s), 1 files saved)"
    print(f"Saved to disk: {result.paths}")
    print(f"Got {len(result.images)} PIL Image object(s)")

    return result


# ─── Approach 4: Custom cloud storage upload (AWS S3 example) ────────────────
def example_upload_to_cloud():
    """Upload images to cloud storage without saving locally."""
    print("\n🔹 Example 4: Cloud storage upload (conceptual)")
    post = create_simple_post()

    # Generate images without saving locally
    images = generate(post, save=False, return_images=True)

    print(f"Generated {len(images)} image(s) for cloud upload")

    # This is a conceptual example. In real usage:
    # - Import boto3 for AWS S3
    # - Use Google Cloud Storage client for GCS
    # - Use Azure Storage SDK for Azure Blob Storage

    for i, img in enumerate(images):
        # Convert image to bytes
        image_bytes = image_to_bytes(img, format=OutputFormat.PNG)

        # Conceptual AWS S3 upload
        # s3_client = boto3.client('s3')
        # s3_client.put_object(
        #     Bucket='my-bucket',
        #     Key=f'images/post_{i+1:02d}.png',
        #     Body=image_bytes,
        #     ContentType='image/png'
        # )

        print(f"  ✓ Image {i+1} ready to upload ({len(image_bytes)} bytes)")


# ─── Approach 5: Carousel with cloud storage ──────────────────────────────────
def example_carousel_to_cloud():
    """Generate carousel images and upload each to cloud."""
    print("\n🔹 Example 5: Carousel images to cloud")

    # Create a multi-slide post (carousel)
    post = instagram_post(
        canvases=[
            create_simple_post().canvases[0] if create_simple_post().canvases
            else None
        ]
        or [
            instagram_story(
                background=BackgroundConfig(color="#1a1a2e"),
                texts=[TextConfig(content=f"Slide {i+1}", y="50%", font_size=96)]
            ).canvases[0]
            if instagram_story(
                background=BackgroundConfig(color="#1a1a2e"),
                texts=[TextConfig(content=f"Slide {i+1}", y="50%", font_size=96)]
            ).canvases
            else None
            for i in range(3)
        ],
        output_dir="./output/carousel",
    )

    # Generate all slides without saving
    images = generate(post, save=False, return_images=True)
    print(f"Generated {len(images)} carousel slide(s)")

    for i, img in enumerate(images):
        # Convert each slide to bytes
        data = image_to_bytes(img, format=OutputFormat.WEBP)  # WEBP for smaller size
        print(f"  Slide {i+1}: {len(data)} bytes (WEBP format)")


# ─── Approach 6: Custom save location ────────────────────────────────────────
def example_custom_save_location():
    """Generate images and save to custom locations using helper function."""
    print("\n🔹 Example 6: Custom save location")

    post = create_simple_post()

    # Get raw images without default saving
    images = generate(post, save=False, return_images=True)

    # Save to custom locations with custom names
    custom_paths = []
    for i, img in enumerate(images):
        custom_path = f"./output/custom_location/my_custom_image_{i:03d}.jpg"
        path = save_image_to_path(img, custom_path, format=OutputFormat.JPEG, quality=90)
        custom_paths.append(path)
        print(f"  ✓ Saved: {path}")

    return custom_paths


# ─── Approach 7: Error handling and validation ────────────────────────────────
def example_error_handling():
    """Demonstrate error handling with invalid parameter combinations."""
    print("\n🔹 Example 7: Error handling")
    post = create_simple_post()

    # ✅ Valid combinations
    print("  Valid combinations:")
    try:
        result1 = generate(post, save=True, return_images=False)
        print(f"    ✓ save=True, return_images=False → {type(result1).__name__} (List[str])")
    except ValueError as e:
        print(f"    ✗ Error: {e}")

    try:
        result2 = generate(post, save=False, return_images=True)
        print(f"    ✓ save=False, return_images=True → {type(result2).__name__} (List[Image.Image])")
    except ValueError as e:
        print(f"    ✗ Error: {e}")

    try:
        result3 = generate(post, save=True, return_images=True)
        print(f"    ✓ save=True, return_images=True → {type(result3).__name__} (GenerateResult)")
    except ValueError as e:
        print(f"    ✗ Error: {e}")

    # ❌ Invalid combination - neither saving nor returning
    print("\n  Invalid combination:")
    try:
        result_invalid = generate(post, save=False, return_images=False)
        print(f"    ✗ Should have raised ValueError!")
    except ValueError as e:
        print(f"    ✓ Caught expected error: {e}")


# ─── Approach 8: Type-safe usage with GenerateResult ─────────────────────────
def example_type_safe_usage():
    """Demonstrate type-safe usage with GenerateResult."""
    print("\n🔹 Example 8: Type-safe usage with GenerateResult")
    post = create_simple_post()

    # When you use save=True, return_images=True, you know exactly what you get
    result = generate(post, save=True, return_images=True)

    # The type is always GenerateResult - no runtime guessing!
    if isinstance(result, GenerateResult):
        print( "  Result type: GenerateResult ✓")
        print(f"  Images available: {result.images}")
        print(f"  Paths available: {result.paths}")
        
        # Safe attribute access - no "did I get a tuple or a result?" confusion
        for i, path in enumerate(result.paths):
            print(f"    [{i}] {path}")
    else:
        print(f"  Unexpected type: {type(result)}")

    return result


# ─── Main execution ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 70)
    print("postcanvas - Cloud Storage Integration Examples")
    print("=" * 70)

    # Run all examples
    example_local_save()
    example_return_raw_images()
    example_save_and_get_images()
    example_upload_to_cloud()
    example_carousel_to_cloud()
    example_custom_save_location()
    example_error_handling()
    example_type_safe_usage()

    print("\n" + "=" * 70)
    print("✅ All examples completed!")
    print("\nKey takeaways:")
    print("• generate(post) → List[str]")
    print("    - Default: save to disk, return file paths")
    print("• generate(post, save=False, return_images=True) → List[Image.Image]")
    print("    - No disk I/O: return PIL Images only")
    print("• generate(post, save=True, return_images=True) → GenerateResult")
    print("    - Save to disk AND return images with consistent structure")
    print("• image_to_bytes(img) → bytes")
    print("    - Convert PIL Image to bytes for cloud upload")
    print("• save_image_to_path(img, path) → str")
    print("    - Save PIL Image to custom location")
    print("\nError handling:")
    print("• generate(save=False, return_images=False) raises ValueError")
    print("    - Must specify at least one output type")
    print("=" * 70)
