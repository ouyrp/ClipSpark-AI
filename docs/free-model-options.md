# ClipSpark AI 免费/试用模型接入方案

## 推荐默认方案

### 1. Gemini API 免费层

- 配置项：`AI_PROVIDER=gemini`
- 推荐模型：
  - 文本剪辑方案：`gemini-2.5-flash-lite`
  - 关键帧视觉理解：`gemini-2.5-flash`
- 优点：官方支持图片、视频、音频等多模态输入；免费层支持 text/image/video 输入输出 token。
- 适合：MVP、视频理解、关键帧分析、字幕/标题/剪辑策略生成。
- 注意：免费层内容可能用于产品改进；生产环境建议升级付费层。

## 免费备选方案

### 2. OpenRouter Free Router

- 配置项：`AI_PROVIDER=openrouter_free`
- 推荐模型：`openrouter/free`
- 优点：自动路由到当前可用免费模型，支持低成本试验。
- 适合：文本剪辑方案、部分视觉分析备选。
- 注意：免费模型可用性、延迟、结构化输出能力会变化，不建议作为唯一生产链路。

### 3. 本地 Ollama

- 配置项：`AI_PROVIDER=ollama`
- 推荐模型：
  - 文本：`qwen2.5:7b`
  - 视觉：`qwen2.5vl:7b`
- 优点：无云端 API 费用，素材不出本机。
- 适合：离线开发、隐私敏感素材、演示环境。
- 注意：需要本机显存/内存，模型质量和速度取决于机器性能。

## 保留但不默认

### 4. 百炼普通 API

- 配置项：`AI_PROVIDER=bailian`
- 要求：使用普通 DashScope API Key，通常是 `sk-...`。
- 注意：`sk-sp-...` 是 Coding Plan 专属 Key，和百炼通用 API Base URL 不互通，不适合当前后端调用。

## 第一阶段落地策略

1. 默认使用 Gemini：先解决视觉理解和视频理解的稳定性。
2. OpenRouter 作为免费兜底：当 Gemini key 没配或额度不足时，可切到免费路由。
3. Ollama 作为本地兜底：后续可做“隐私模式”。
4. 每次生成都记录 `ai_provider` 和 `ai_model`，方便后续对比出片质量。

## 环境变量示例

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_TEXT_MODEL=gemini-2.5-flash-lite
GEMINI_VISION_MODEL=gemini-2.5-flash

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_TEXT_MODEL=openrouter/free
OPENROUTER_VISION_MODEL=openrouter/free

OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_TEXT_MODEL=qwen2.5:7b
OLLAMA_VISION_MODEL=qwen2.5vl:7b
```
