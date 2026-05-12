# ClipSpark AI 技术方案

## 1. 技术选型结论

本项目采用以下技术路线：

- 前端：Next.js + React + TypeScript。
- 后端：Python + FastAPI。
- AI 能力：阿里云百炼，优先通过 OpenAI 兼容接口接入。
- 视频处理：FFmpeg 为核心，后续可引入 Remotion 承担复杂模板渲染。
- 数据库：PostgreSQL。
- 缓存与队列：Redis。
- 异步任务：Celery 或 RQ，MVP 推荐 Celery。
- 文件存储：本地开发使用本地目录，生产使用阿里云 OSS。
- 部署：前后端分离，AI 分析和视频渲染使用独立 Worker。

核心原则：

1. 前端只负责上传、配置、状态展示、预览和轻量编辑。
2. 后端负责业务状态、AI 编排、任务调度和数据持久化。
3. AI 调用统一封装为 Provider，避免业务代码直接依赖具体模型。
4. 视频分析、剪辑和渲染全部异步化。
5. 剪辑结果用结构化 Edit Plan 表达，再由渲染层生成视频。

## 2. 系统架构

```mermaid
flowchart TB
  Web["Next.js 前端"] --> API["Python FastAPI"]

  API --> DB["PostgreSQL"]
  API --> Redis["Redis"]
  API --> Storage["OSS / 本地文件存储"]
  API --> Queue["Celery Queue"]

  Queue --> AnalyzeWorker["AI 分析 Worker"]
  Queue --> RenderWorker["视频渲染 Worker"]

  AnalyzeWorker --> Bailian["阿里云百炼<br/>OpenAI 兼容 API"]
  AnalyzeWorker --> Storage
  AnalyzeWorker --> DB

  RenderWorker --> FFmpeg["FFmpeg"]
  RenderWorker --> Storage
  RenderWorker --> DB
```

## 3. 推荐目录结构

```text
clipspark-ai/
  apps/
    web/                         # Next.js 前端
      app/
      components/
      features/
      lib/
      public/
      package.json

    api/                         # Python FastAPI 后端
      app/
        api/
          routes/
        core/
        db/
        models/
        schemas/
        services/
          ai/
          video/
          storage/
          edit_plan/
        workers/
        main.py
      pyproject.toml

  docs/
    architecture.md
    technical-solution.md

  storage/                       # 本地开发用，生产替换为 OSS
    uploads/
    processed/
    renders/
```

## 4. 前端方案

### 4.1 技术栈

- Next.js App Router
- React
- TypeScript
- Tailwind CSS
- Zustand
- TanStack Query
- video.js 或原生 video 标签
- tus-js-client 或自研分片上传

### 4.2 页面设计

MVP 页面：

- `/`：项目列表和新建入口。
- `/projects/new`：上传素材。
- `/projects/[id]`：项目详情、任务状态、生成结果。
- `/projects/[id]/edit/[renderId]`：轻量编辑。
- `/templates`：模板列表。

### 4.3 前端核心状态

前端不保存复杂剪辑状态，只保存用户操作状态和接口返回结果。

主要状态：

- 当前项目。
- 上传进度。
- 任务状态。
- 视频预览地址。
- 选中的生成版本。
- 字幕编辑草稿。
- 模板配置。

### 4.4 前端组件拆分

```text
components/
  upload/
    VideoUploader.tsx
    UploadProgress.tsx
  project/
    ProjectStatus.tsx
    RenderResultList.tsx
    VideoPreview.tsx
  editor/
    SubtitleEditor.tsx
    TemplateSelector.tsx
    CoverSelector.tsx
    BgmSelector.tsx
  common/
    Button.tsx
    Modal.tsx
    Toast.tsx
```

### 4.5 前端与后端交互原则

- 上传完成后只拿到 asset_id，不直接触发复杂逻辑。
- 用户点击“开始生成”后，由后端创建任务。
- 前端轮询任务状态，MVP 可用轮询，后续改 SSE 或 WebSocket。
- 视频预览使用后端返回的 signed URL 或静态访问 URL。

## 5. 后端方案

### 5.1 技术栈

- Python 3.11+
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Redis
- Celery
- FFmpeg
- OpenAI Python SDK，用于调用百炼 OpenAI 兼容 API

### 5.2 后端分层

```text
app/
  api/            # HTTP 路由
  schemas/        # 请求和响应 DTO
  models/         # SQLAlchemy 模型
  services/       # 业务服务
  workers/        # Celery 任务
  core/           # 配置、日志、异常、鉴权
```

分层职责：

- Routes：参数校验、鉴权、调用 Service。
- Services：业务逻辑编排。
- Models：数据库表结构。
- Schemas：API 入参和出参。
- Workers：长任务执行。
- Providers：第三方能力封装。

### 5.3 核心服务

```text
services/
  ai/
    provider.py              # AI Provider 抽象
    bailian_provider.py      # 百炼实现
    prompts.py               # Prompt 模板
  video/
    ffmpeg_service.py        # 转码、抽音频、裁剪、拼接
    frame_service.py         # 抽帧
    render_service.py        # 渲染编排
  storage/
    local_storage.py
    oss_storage.py
  edit_plan/
    planner.py               # 生成剪辑方案
    validator.py             # 校验剪辑方案
```

## 6. 百炼 AI 接入方案

### 6.1 接入方式

百炼官方支持 OpenAI 兼容接口和 DashScope SDK。为了降低后续迁移成本，MVP 推荐先使用 OpenAI 兼容接口。

Python 客户端配置：

```python
from openai import OpenAI

client = OpenAI(
    api_key=settings.DASHSCOPE_API_KEY,
    base_url=settings.BAILIAN_BASE_URL,
)
```

推荐环境变量：

```text
DASHSCOPE_API_KEY=your_api_key
BAILIAN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
BAILIAN_TEXT_MODEL=qwen-plus
BAILIAN_VISION_MODEL=qwen-vl-plus
BAILIAN_EMBEDDING_MODEL=text-embedding-v4
```

说明：

- 华北 2 北京地域常用 `https://dashscope.aliyuncs.com/compatible-mode/v1`。
- 不同地域的 base_url 可能不同，生产环境应按实际开通地域配置。
- 模型名称以百炼控制台可用模型为准，不建议硬编码在业务逻辑中。

### 6.2 AI Provider 抽象

业务代码不直接调用百炼，而是调用统一接口。

```python
class AIProvider:
    async def summarize_transcript(self, transcript: str) -> dict:
        raise NotImplementedError

    async def detect_highlights(self, transcript: str, scenes: list[dict]) -> dict:
        raise NotImplementedError

    async def generate_edit_plan(self, context: dict) -> dict:
        raise NotImplementedError

    async def generate_publish_copy(self, context: dict) -> dict:
        raise NotImplementedError
```

百炼实现：

```python
class BailianProvider(AIProvider):
    def __init__(self, client: OpenAI, text_model: str, vision_model: str):
        self.client = client
        self.text_model = text_model
        self.vision_model = vision_model

    async def generate_edit_plan(self, context: dict) -> dict:
        response = self.client.chat.completions.create(
            model=self.text_model,
            messages=[
                {"role": "system", "content": "你是一个短视频剪辑导演，只输出 JSON。"},
                {"role": "user", "content": build_edit_plan_prompt(context)},
            ],
            response_format={"type": "json_object"},
        )
        return parse_json(response.choices[0].message.content)
```

### 6.3 AI 能力拆分

MVP 需要的 AI 能力：

1. 文本摘要：根据字幕理解视频主题。
2. 高光识别：从字幕和时间戳中找出适合剪辑的片段。
3. 剪辑方案生成：输出结构化 Edit Plan。
4. 标题生成：生成视频标题。
5. 发布文案生成：生成平台文案和话题标签。

第二阶段增加：

1. 视觉理解：对抽帧图片进行场景、人物、商品、画质分析。
2. 封面策略：从候选帧中选封面并生成标题。
3. 模板推荐：根据内容类型匹配模板。
4. 向量检索：素材库、片段检索、历史风格学习。

### 6.4 Prompt 输出约束

所有 AI 生成的核心结果必须是 JSON，不能只返回自然语言。

高光识别输出：

```json
{
  "highlights": [
    {
      "start": 12.3,
      "end": 38.6,
      "score": 0.92,
      "hook": "你是不是也遇到过剪视频太慢的问题？",
      "reason": "开头有明确痛点，适合做短视频开场"
    }
  ]
}
```

剪辑方案输出：

```json
{
  "target_platform": "douyin",
  "aspect_ratio": "9:16",
  "duration": 42.5,
  "clips": [
    {
      "asset_id": "asset_001",
      "source_start": 12.3,
      "source_end": 28.7,
      "timeline_start": 0,
      "timeline_end": 16.4
    }
  ],
  "title": "AI 一键剪出爆款短视频",
  "subtitle_style": {
    "font_size": 48,
    "position": "bottom",
    "keyword_highlight": true
  },
  "bgm": {
    "style": "light_trend",
    "volume": 0.18
  },
  "cover": {
    "source_time": 16.8,
    "title": "一键生成短视频"
  },
  "publish_copy": {
    "caption": "上传长视频，AI 自动剪出可发布短视频。",
    "hashtags": ["AI剪辑", "短视频工具", "内容创作"]
  }
}
```

### 6.5 AI 调用策略

为了控制成本：

- 先用 ASR 字幕做文本分析，不要一开始对全视频高频抽帧。
- 抽帧优先按场景变化或固定低频抽取，例如每 3 到 5 秒一帧。
- 先让模型筛选候选片段，再对候选片段做更细分析。
- 相同素材的分析结果必须缓存。
- 每个项目记录 AI token 使用量和模型调用次数。

## 7. 视频处理方案

### 7.1 处理流水线

```mermaid
flowchart LR
  A["原始视频"] --> B["读取元数据"]
  B --> C["转码为标准格式"]
  C --> D["提取音频"]
  D --> E["ASR 生成字幕"]
  C --> F["抽帧"]
  E --> G["AI 分析"]
  F --> G
  G --> H["生成 Edit Plan"]
  H --> I["FFmpeg 渲染"]
  I --> J["成品 MP4"]
```

### 7.2 标准中间格式

为了降低渲染复杂度，上传后统一生成中间文件：

- 视频编码：H.264
- 音频编码：AAC
- 容器：MP4
- 帧率：30 fps
- 分辨率：保留原始分辨率，必要时生成 1080p 代理文件

### 7.3 渲染能力

MVP 渲染能力：

- 裁剪片段。
- 拼接片段。
- 生成 9:16 视频。
- 添加字幕。
- 添加标题文字。
- 混合 BGM。
- 输出 MP4。
- 截取封面图。

第二阶段：

- 关键词高亮字幕。
- 转场动画。
- 模板化版式。
- 多平台比例导出。
- 批量生成多个版本。

## 8. 数据库设计

### 8.1 projects

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  user_id UUID,
  name TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
```

### 8.2 assets

```sql
CREATE TABLE assets (
  id UUID PRIMARY KEY,
  project_id UUID NOT NULL REFERENCES projects(id),
  type TEXT NOT NULL,
  original_url TEXT NOT NULL,
  processed_url TEXT,
  duration_seconds DOUBLE PRECISION,
  width INTEGER,
  height INTEGER,
  fps DOUBLE PRECISION,
  metadata JSONB,
  created_at TIMESTAMP NOT NULL
);
```

### 8.3 analysis_results

```sql
CREATE TABLE analysis_results (
  id UUID PRIMARY KEY,
  project_id UUID NOT NULL REFERENCES projects(id),
  asset_id UUID NOT NULL REFERENCES assets(id),
  transcript JSONB,
  scenes JSONB,
  highlights JSONB,
  summary JSONB,
  ai_usage JSONB,
  created_at TIMESTAMP NOT NULL
);
```

### 8.4 edit_plans

```sql
CREATE TABLE edit_plans (
  id UUID PRIMARY KEY,
  project_id UUID NOT NULL REFERENCES projects(id),
  analysis_result_id UUID REFERENCES analysis_results(id),
  template_id UUID,
  target_platform TEXT,
  aspect_ratio TEXT,
  duration_seconds DOUBLE PRECISION,
  plan JSONB NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
```

### 8.5 render_jobs

```sql
CREATE TABLE render_jobs (
  id UUID PRIMARY KEY,
  project_id UUID NOT NULL REFERENCES projects(id),
  edit_plan_id UUID NOT NULL REFERENCES edit_plans(id),
  status TEXT NOT NULL,
  progress INTEGER NOT NULL DEFAULT 0,
  output_video_url TEXT,
  output_cover_url TEXT,
  error_message TEXT,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
```

### 8.6 templates

```sql
CREATE TABLE templates (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  platform TEXT,
  content_type TEXT,
  config JSONB NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
```

## 9. API 设计

### 9.1 项目

```http
POST /api/projects
GET /api/projects
GET /api/projects/{project_id}
DELETE /api/projects/{project_id}
```

创建项目请求：

```json
{
  "name": "直播回放剪辑"
}
```

### 9.2 素材

```http
POST /api/projects/{project_id}/assets
GET /api/projects/{project_id}/assets
GET /api/assets/{asset_id}
```

MVP 可以先用普通表单上传，后续再升级分片上传。

### 9.3 生成任务

```http
POST /api/projects/{project_id}/generate
GET /api/projects/{project_id}/jobs
GET /api/render-jobs/{job_id}
```

生成请求：

```json
{
  "asset_id": "asset_001",
  "target_platform": "douyin",
  "aspect_ratio": "9:16",
  "template_id": "template_douyin_talk_001",
  "version_count": 3
}
```

### 9.4 预览和导出

```http
GET /api/projects/{project_id}/renders
GET /api/renders/{render_id}
POST /api/renders/{render_id}/regenerate
POST /api/renders/{render_id}/export
```

### 9.5 轻量编辑

```http
PATCH /api/edit-plans/{edit_plan_id}
POST /api/edit-plans/{edit_plan_id}/render
```

支持用户改：

- 字幕文本。
- 标题。
- 片段起止时间。
- 模板。
- BGM。
- 封面时间点。

## 10. 异步任务设计

### 10.1 任务拆分

```text
process_asset_task
  -> transcode video
  -> extract audio
  -> extract frames

analyze_asset_task
  -> ASR
  -> transcript summary
  -> highlight detection
  -> scene analysis

generate_edit_plan_task
  -> build context
  -> call Bailian
  -> validate plan
  -> create edit_plans

render_video_task
  -> render video by edit_plan
  -> generate cover
  -> update render_jobs
```

### 10.2 任务状态

```text
uploaded
processing
analyzing
planning
rendering
completed
failed
```

每个任务必须记录：

- status
- progress
- current_step
- error_message
- started_at
- finished_at

## 11. 安全与配置

### 11.1 环境变量

```text
APP_ENV=development
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/clipspark
REDIS_URL=redis://localhost:6379/0

DASHSCOPE_API_KEY=
BAILIAN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
BAILIAN_TEXT_MODEL=qwen-plus
BAILIAN_VISION_MODEL=qwen-vl-plus
BAILIAN_EMBEDDING_MODEL=text-embedding-v4

STORAGE_DRIVER=local
LOCAL_STORAGE_ROOT=./storage

OSS_ENDPOINT=
OSS_BUCKET=
OSS_ACCESS_KEY_ID=
OSS_ACCESS_KEY_SECRET=
```

### 11.2 安全要求

- API Key 只放后端环境变量，不暴露给前端。
- 上传文件限制大小、类型和时长。
- 用户只能访问自己的项目和素材。
- OSS 文件使用私有读写和签名 URL。
- 渲染命令参数必须由后端结构化生成，避免直接拼接用户输入。

## 12. MVP 实施计划

### 第 1 周：项目骨架

- 搭建 Next.js 项目。
- 搭建 FastAPI 项目。
- 接入 PostgreSQL、Redis。
- 建立 Project、Asset、RenderJob 数据模型。
- 完成普通视频上传。

### 第 2 周：视频预处理

- 接入 FFmpeg。
- 实现视频元数据读取。
- 实现音频提取。
- 实现视频标准化转码。
- 实现抽帧。

### 第 3 周：百炼接入和 AI 分析

- 封装 BailianProvider。
- 实现字幕摘要。
- 实现高光片段识别。
- 实现标题、文案、标签生成。
- 保存 analysis_results。

### 第 4 周：剪辑方案和渲染

- 实现 Edit Plan 生成。
- 实现 Edit Plan 校验。
- 实现 FFmpeg 裁剪、拼接、字幕烧录。
- 生成 3 个短视频版本。
- 生成封面图。

### 第 5 周：前端闭环

- 项目详情页。
- 任务状态展示。
- 视频结果预览。
- 下载 MP4。
- 简单重新生成。

### 第 6 周：体验优化

- 字幕轻量编辑。
- 标题修改。
- 模板选择。
- BGM 配置。
- 错误提示和重试。

## 13. 后续演进

### 13.1 从下载到发布

先实现下载，后续逐步接入：

- 抖音开放平台。
- 小红书发布链路。
- 视频号助手。
- TikTok / YouTube Shorts。

### 13.2 从单视频到批量生产

演进方向：

- 批量上传。
- 批量生成。
- 模板批处理。
- 品牌素材库。
- 多账号内容风格。

### 13.3 从规则剪辑到智能导演

演进方向：

- 引入视觉理解。
- 引入历史爆款样本。
- 根据行业优化剪辑策略。
- 用户反馈反哺模板推荐。
- 使用 Embedding 做片段检索和风格匹配。

## 14. 官方资料参考

- 阿里云百炼介绍：`https://www.alibabacloud.com/help/zh/doc-detail/2579562.html`
- 百炼 SDK 安装说明：`https://www.alibabacloud.com/help/zh/doc-detail/2712193.html`
- 百炼 Embedding 文档：`https://www.alibabacloud.com/help/zh/doc-detail/2842587.html`

## 15. 总结

这套技术方案的核心是：

1. 用 Next.js 做轻量、顺滑的创作工作台。
2. 用 Python FastAPI 承担业务编排和 AI 工作流。
3. 用百炼提供文本、视觉和向量模型能力。
4. 用 FFmpeg 建立稳定的视频处理底座。
5. 用异步任务系统承载长耗时分析和渲染。
6. 用结构化 Edit Plan 连接 AI 决策和视频渲染。

MVP 不追求完整专业剪辑器，而是先把“上传一个长视频，自动生成 3 条可发布短视频”做稳定。这个闭环跑通后，再扩展模板、视觉理解、平台发布和商业化能力。
