# ClipSpark AI

AI 短视频剪辑工具 MVP。当前技术栈：

- 前端：Next.js + React + TypeScript
- 后端：Python + FastAPI
- AI：阿里云百炼 OpenAI 兼容 API
- 视频处理：预留 FFmpeg 服务层
- 存储：本地 `storage/`，生产可替换为 OSS

## 目录

```text
apps/web    Next.js 前端
apps/api    FastAPI 后端
docs        架构和技术方案
storage     本地开发存储目录
```

## 后端启动

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

健康检查：

```bash
curl http://localhost:8000/api/health
```

## 前端启动

```bash
cd apps/web
npm install
npm run dev
```

访问：

```text
http://localhost:3000
```

## 环境变量

后端读取 `apps/api/.env`。当前本地文件已按你的百炼 API Key 配好；不要把 `.env` 提交到仓库。

可参考：

```text
apps/api/.env.example
apps/web/.env.example
```

## MVP 当前能力

- 创建项目
- 上传视频素材
- 调用百炼生成剪辑计划
- 返回 3 条短视频候选方案
- 前端展示生成结果

下一步建议接入：

- ASR 字幕生成
- FFmpeg 裁剪和字幕烧录
- RenderJob 状态轮询
- OSS 存储
