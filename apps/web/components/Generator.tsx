"use client";

import { FormEvent, useState } from "react";

import { Asset, EditPlan, Project, createProject, generatePlans, uploadAsset } from "../lib/api";

type Step = "idle" | "creating" | "uploading" | "generating" | "done" | "error";

export function Generator() {
  const [projectName, setProjectName] = useState("我的第一条 AI 剪辑项目");
  const [targetPlatform, setTargetPlatform] = useState("douyin");
  const [aspectRatio, setAspectRatio] = useState("9:16");
  const [userGoal, setUserGoal] = useState("剪出 3 条可以直接发的短视频");
  const [file, setFile] = useState<File | null>(null);
  const [step, setStep] = useState<Step>("idle");
  const [error, setError] = useState("");
  const [project, setProject] = useState<Project | null>(null);
  const [asset, setAsset] = useState<Asset | null>(null);
  const [plans, setPlans] = useState<EditPlan[]>([]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("请先选择一个视频文件。");
      return;
    }

    setError("");
    setPlans([]);
    try {
      setStep("creating");
      const createdProject = await createProject(projectName);
      setProject(createdProject);

      setStep("uploading");
      const uploadedAsset = await uploadAsset(createdProject.id, file);
      setAsset(uploadedAsset);

      setStep("generating");
      const generatedPlans = await generatePlans({
        projectId: createdProject.id,
        assetId: uploadedAsset.id,
        targetPlatform,
        aspectRatio,
        versionCount: 3,
        userGoal,
      });
      setPlans(generatedPlans);
      setStep("done");
    } catch (err) {
      setStep("error");
      setError(err instanceof Error ? err.message : "生成失败");
    }
  }

  const isWorking = ["creating", "uploading", "generating"].includes(step);

  return (
    <main className="main">
      <section className="panel">
        <h2>一键生成</h2>
        <form onSubmit={onSubmit}>
          <label className="field">
            <span className="label">项目名称</span>
            <input className="input" value={projectName} onChange={(event) => setProjectName(event.target.value)} />
          </label>

          <label className="field">
            <span className="label">视频素材</span>
            <input
              className="input"
              type="file"
              accept="video/*"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
          </label>

          <label className="field">
            <span className="label">目标平台</span>
            <select className="select" value={targetPlatform} onChange={(event) => setTargetPlatform(event.target.value)}>
              <option value="douyin">抖音</option>
              <option value="xiaohongshu">小红书</option>
              <option value="kuaishou">快手</option>
              <option value="tiktok">TikTok</option>
              <option value="youtube_shorts">YouTube Shorts</option>
            </select>
          </label>

          <label className="field">
            <span className="label">画面比例</span>
            <select className="select" value={aspectRatio} onChange={(event) => setAspectRatio(event.target.value)}>
              <option value="9:16">9:16 竖屏</option>
              <option value="1:1">1:1 方形</option>
              <option value="16:9">16:9 横屏</option>
            </select>
          </label>

          <label className="field">
            <span className="label">生成目标</span>
            <textarea className="textarea" value={userGoal} onChange={(event) => setUserGoal(event.target.value)} />
          </label>

          <button className="button" disabled={isWorking} type="submit">
            {isWorking ? "生成中..." : "上传并生成剪辑方案"}
          </button>
        </form>

        {step !== "idle" && (
          <p className="muted">
            当前状态：<span className={step === "done" ? "status" : ""}>{stepLabel(step)}</span>
          </p>
        )}
        {error && <p className="muted">{error}</p>}
      </section>

      <section className="panel">
        <h2>生成结果</h2>
        <div className="stack">
          {project && (
            <div className="result">
              <h3>{project.name}</h3>
              <p className="muted">项目 ID：{project.id}</p>
              {asset && <p className="muted">素材：{asset.filename}</p>}
            </div>
          )}

          {plans.length === 0 && <p className="muted">上传视频后，这里会展示 AI 生成的 3 条短视频剪辑方案。</p>}

          {plans.map((item, index) => (
            <article className="result" key={item.id}>
              {typeof item.plan.preview_url === "string" && (
                <div className="previewFrame">
                  <video
                    className="previewVideo"
                    controls
                    preload="metadata"
                    src={buildPreviewUrl(item.plan)}
                  />
                </div>
              )}
              <h3>方案 {index + 1}：{String(item.plan.title ?? "未命名方案")}</h3>
              <p>{String(item.plan.hook ?? "暂无钩子文案")}</p>
              <p className="muted">时长：{item.duration_seconds ?? item.plan.duration ?? "-"} 秒</p>
              <p>
                <span className="pill">{item.target_platform}</span>
                <span className="pill">{item.aspect_ratio}</span>
                <span className="pill">{item.plan.preview_type === "rendered_clip" ? "已渲染预览" : item.status}</span>
              </p>
              {Array.isArray(item.plan.render_features) && (
                <p className="muted">处理：裁剪、比例适配、标题叠加、调色、淡入淡出、自动背景音</p>
              )}
              <p className="muted">{String(item.plan.publish_copy?.caption ?? "")}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

function stepLabel(step: Step) {
  const labels: Record<Step, string> = {
    idle: "等待开始",
    creating: "创建项目",
    uploading: "上传素材",
    generating: "调用百炼生成剪辑方案",
    done: "完成",
    error: "失败",
  };
  return labels[step];
}

function buildPreviewUrl(plan: Record<string, any>) {
  const clips = Array.isArray(plan.clips) ? plan.clips : [];
  const firstClip = clips[0];
  const start = Number(firstClip?.source_start ?? 0);
  const end = Number(firstClip?.source_end ?? 0);
  const fragment = Number.isFinite(end) && end > start ? `#t=${start},${end}` : `#t=${start}`;
  return `${plan.preview_url}${fragment}`;
}
