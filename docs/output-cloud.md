# Output, bytes and cloud storage

## Save files

```python
paths = generate(post)
```

Output behavior is controlled by `output_dir`, `output_filename`, `output_format`, `quality`, `dpi`, and per-canvas filenames.

## Return PIL images

```python
images = generate(post, save=False, return_images=True)
image = images[0]
```

## Return paths and images

```python
result = generate(post, save=True, return_images=True)

print(result.paths)
print(result.images)
print(result.reports)
```

## Structured render result

```python
result = render(post, save=False)

for image, report in zip(result.images, result.reports):
    print(image.size, report.warnings)
```

## Encode to bytes

```python
from postcanvas import image_to_bytes
from postcanvas.models import OutputFormat

png = image_to_bytes(image, format=OutputFormat.PNG)
webp = image_to_bytes(image, format=OutputFormat.WEBP, quality=88)
jpeg = image_to_bytes(image, format=OutputFormat.JPEG, quality=92)
```

## Save to a custom path

```python
from postcanvas import save_image_to_path

save_image_to_path(image, "./public/og/home.webp")
```

## Upload to S3-compatible storage

```python
payload = image_to_bytes(image, format=OutputFormat.WEBP, quality=90)

s3.put_object(
    Bucket="media",
    Key="campaign/launch.webp",
    Body=payload,
    ContentType="image/webp",
)
```

## Upload through HTTP

```python
payload = image_to_bytes(image, format=OutputFormat.PNG)

response = requests.put(
    upload_url,
    data=payload,
    headers={"Content-Type": "image/png"},
)
response.raise_for_status()
```

## In-memory API response

```python
from io import BytesIO

payload = image_to_bytes(image, format=OutputFormat.PNG)
stream = BytesIO(payload)
```

In FastAPI or Flask, return the bytes with the correct media type.

## Output formats

| Format | Typical use |
|---|---|
| PNG | sharp text, graphics, transparency |
| JPEG/JPG | photo-heavy images and smaller files |
| WebP | modern web delivery and compact mixed content |

## Quality and file-size limits

```python
post.output_format = "webp"
post.quality = 88
post.max_file_size_bytes = 2_000_000
post.layout_policy.file_size = "error"
```

File-size validation encodes the final image using the configured format and quality.

## Carousels

Each slide is written separately. Use deterministic filenames.

```python
CanvasConfig(output_filename="01-cover")
CanvasConfig(output_filename="02-insight")
```

## Metadata

`MetaConfig` is not rendered. It is useful for content IDs, CMS integration, provenance, and downstream publishing.

```python
post.meta.title = "Launch announcement"
post.meta.tags = ["launch", "instagram"]
post.meta.custom["campaign_id"] = "cmp_2026_09"
```

## Batch rendering

Use templates to build posts from data records, process them sequentially or in a worker pool, keep font files/assets available in every worker, and use strict validation before upload.
