# 🧬 Frankenstein_AI

A modular multi-API AI orchestration engine that combines outputs from different intelligence sources into one unified response.

🚀 Overview

Frankenstein_AI is a backend system that routes user prompts to multiple AI services (text, code, image, search), executes them in parallel, and stitches their outputs together into a single response.

Instead of relying on one model, it builds intelligence by combining multiple specialized systems.

⚙️ Core Features
🧠 Multi-API Routing
Text generation
Code generation
Image generation
Web search
⚡ Parallel Execution
Uses ThreadPoolExecutor to run multiple AI tools simultaneously
🧩 Dynamic Intent Classification
Automatically detects what type of response is needed
💾 Smart Caching
SHA256-based caching system to avoid repeated API calls
🌐 Offline Mode
Fallback logic when external APIs are unavailable
🖼️ Auto Image Extraction
Pulls images from search results and injects them into output

🏗️ Architecture
User Prompt  -> Intent Classifier-> Task Router ->Text API with image API and code API with search API in Parallel Execution , Aggregation = Final Output

🧪 Example Flow

Input: "Generate a Python function and explain it"

System Behavior:
- Detects: code + text
- Calls code generator API and text generator API
- Runs both in parallel
- Returns combined output

## Qwen-Image-2.1 (optional local image backend)

Frankenstein AI can use the open-weight Qwen-Image-2.1 model for text-to-image generation and single-image editing. The default checkpoint is **Qwen-Image-2.1-Turbo**, which uses its published 8-step schedule. The original Qwen-Image-2.1 checkpoint can also be selected.

Install the optional dependencies in the same Python environment as Frankenstein AI:

```bash
pip install -r requirements-qwen-image.txt
```

Select Qwen instead of the existing Hugging Face image provider:

```bash
# Windows PowerShell
$env:IMAGE_PROVIDER = "qwen"

# Linux / macOS
export IMAGE_PROVIDER=qwen
```

Optional configuration:

| Variable | Default | Purpose |
|---|---|---|
| `QWEN_IMAGE_MODEL` | `Qwen/Qwen-Image-2.1-Turbo` | Model ID; use `Qwen/Qwen-Image-2.1` for the standard checkpoint |
| `QWEN_IMAGE_DEVICE` | `auto` | `auto`, `cuda`, or `cpu` |
| `QWEN_IMAGE_CPU_OFFLOAD` | `1` | Sequential CPU offload to reduce peak VRAM use |
| `QWEN_IMAGE_STEPS` | `40` | Denoising steps for the standard checkpoint; Turbo uses its checkpoint schedule |

The model downloads on first image request and is kept loaded for subsequent requests. Generated files are saved under `images/`. The provider is lazy-loaded, so existing users do not need Qwen dependencies unless they select it.

**Hardware note:** Qwen-Image-2.1 has a 7B visual generation component and a large text encoder. CPU offload can reduce VRAM requirements but increases system-RAM use and generation time; it does not make a 4GB GPU a practical full-speed setup. For a 4GB RTX 3050 Ti / 16GB RAM machine, use a dedicated remote ComfyUI/SGLang host or a machine with substantially more memory for reliable inference. Do not expect this configuration to run comfortably as-is.

**License note:** Qwen publishes the weights under the Qwen Research License Agreement. Review that license before commercial deployment; "open-weight" does not automatically mean unrestricted commercial use.

Upstream model and implementation:
- https://github.com/QwenLM/Qwen-Image-2.1
- https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo

## 🚫 License

This project is proprietary software.
Unauthorized use, copying, or distribution is strictly prohibited.
