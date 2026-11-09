"""Optional local Qwen-Image-2.1 backend.

The model is loaded lazily on the first request so importing Frankenstein AI
does not download weights or allocate GPU memory.
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from threading import Lock
from typing import Optional

_PIPELINE = None
_PIPELINE_LOCK = Lock()


def _load_pipeline():
    global _PIPELINE
    if _PIPELINE is not None:
        return _PIPELINE

    with _PIPELINE_LOCK:
        if _PIPELINE is not None:
            return _PIPELINE

        try:
            import torch
            from diffusers import QwenImage21Pipeline
        except ImportError as exc:
            raise RuntimeError(
                "Qwen backend dependencies are missing. Install "
                "requirements-qwen-image.txt in the active environment."
            ) from exc

        model_id = os.getenv("QWEN_IMAGE_MODEL", "Qwen/Qwen-Image-2.1-Turbo")
        device = os.getenv("QWEN_IMAGE_DEVICE", "auto").lower()
        offload = os.getenv("QWEN_IMAGE_CPU_OFFLOAD", "1").lower() in {
            "1", "true", "yes", "on"
        }

        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"

        # BF16 is the upstream recommended dtype. CPU execution uses float32
        # for broader compatibility; CUDA uses BF16.
        dtype = torch.bfloat16 if device == "cuda" else torch.float32
        pipe = QwenImage21Pipeline.from_pretrained(model_id, dtype=dtype)

        if device == "cuda":
            if offload:
                # Lowest-VRAM mode; substantially slower due to CPU/GPU transfers.
                pipe.enable_sequential_cpu_offload()
            else:
                pipe.to("cuda")
        else:
            pipe.to("cpu")

        _PIPELINE = pipe
        return _PIPELINE


def qwen_generate_image(
    prompt: str,
    image_path: Optional[str] = None,
    output_dir: str = "images",
    seed: Optional[int] = None,
):
    """Generate an image or edit one input image with Qwen-Image-2.1(-Turbo)."""
    try:
        import torch
        from PIL import Image

        prompt = (prompt or "").strip()
        if not prompt:
            return {
                "ok": False,
                "text": "Prompt cannot be empty.",
                "path": None,
                "provider": "qwen-image-2.1",
            }

        pipe = _load_pipeline()
        model_id = os.getenv("QWEN_IMAGE_MODEL", "Qwen/Qwen-Image-2.1-Turbo")
        is_turbo = "turbo" in model_id.lower()

        generator_device = "cpu" if os.getenv(
            "QWEN_IMAGE_CPU_OFFLOAD", "1"
        ).lower() in {"1", "true", "yes", "on"} else (
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        generator = None
        if seed is not None:
            generator = torch.Generator(device=generator_device).manual_seed(int(seed))

        call_args = {
            "prompt": prompt,
            "use_kv_cache": True,
        }
        if generator is not None:
            call_args["generator"] = generator

        # Turbo's checkpoint carries its own 8-step schedule. Do not override it.
        if not is_turbo:
            steps = int(os.getenv("QWEN_IMAGE_STEPS", "40"))
            call_args["num_inference_steps"] = max(1, steps)

        if image_path:
            source = Path(image_path).expanduser()
            if not source.is_file():
                raise FileNotFoundError(f"Input image not found: {source}")
            call_args["image"] = Image.open(source).convert("RGBA")

        result = pipe(**call_args).images[0]

        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        filename = f"qwen_image_{int(time.time() * 1000)}.png"
        output_path = (destination / filename).resolve()
        result.save(output_path)

        return {
            "ok": True,
            "text": "image generated" if not image_path else "image edited",
            "path": str(output_path),
            "provider": "qwen-image-2.1",
            "model": model_id,
            "mode": "image-to-image" if image_path else "text-to-image",
        }
    except Exception as exc:
        return {
            "ok": False,
            "text": f"Qwen Image error: {exc}",
            "path": None,
            "provider": "qwen-image-2.1",
        }
