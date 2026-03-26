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

   Input:  "Generate a Python function and explain it"

System Behavior:

Detects: code + text
Calls:
Code generator API
Text generator API
Runs both in parallel
Returns combined output
