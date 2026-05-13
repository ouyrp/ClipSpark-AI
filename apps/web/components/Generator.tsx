"use client";

import { FormEvent, useState } from "react";

import {
  Asset,
  EditPlan,
  Project,
  createProject,
  generatePlans,
  rerenderEditPlan,
  updateEditPlan,
  uploadAsset,
} from "../lib/api";

type Step = "idle" | "creating" | "uploading" | "generating" | "done" | "error";

export function Generator() {
  const [projectName, setProjectName] = useState("我的第一条 AI 剪辑项目");
  const [targetPlatform, setTargetPlatform] = useState("douyin");
  const [aspectRatio, setAspectRatio] = useState("9:16");
  const [creativeTone, setCreativeTone] = useState("auto");
  const [userGoal, setUserGoal] = useState("剪出 3 条可以直接发的短视频");
  const [file, setFile] = useState<File | null>(null);
  const [step, setStep] = useState<Step>("idle");
  const [error, setError] = useState("");
  const [project, setProject] = useState<Project | null>(null);
  const [asset, setAsset] = useState<Asset | null>(null);
  const [plans, setPlans] = useState<EditPlan[]>([]);
  const [editingId, setEditingId] = useState("");
  const [editError, setEditError] = useState("");

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
        creativeTone,
      });
      setPlans(generatedPlans);
      setStep("done");
    } catch (err) {
      setStep("error");
      setError(err instanceof Error ? err.message : "生成失败");
    }
  }

  const isWorking = ["creating", "uploading", "generating"].includes(step);

  async function applyPlanEdit(item: EditPlan) {
    setEditingId(item.id);
    setEditError("");
    try {
      const updated = await updateEditPlan(item.id, {
        title: String(item.plan.title ?? ""),
        hook: String(item.plan.hook ?? ""),
        caption_lines: normalizeCaptionLines(item.plan.caption_lines),
        visual_style: String(item.plan.visual_style ?? "vivid_pain_point"),
        effect_style: String(item.plan.effect_style ?? "vignette_focus"),
        bgm_style: String(item.plan.bgm?.style ?? "tech_pulse"),
        bgm_volume: Number(item.plan.bgm?.volume ?? 0.22),
      });
      const rendered = await rerenderEditPlan(updated.id);
      replacePlan(rendered);
      if (rendered.status === "render_failed") {
        setEditError(String(rendered.plan.render_error ?? "重渲染失败"));
      }
    } catch (err) {
      setEditError(err instanceof Error ? err.message : "编辑失败");
    } finally {
      setEditingId("");
    }
  }

  function updateLocalPlan(id: string, updater: (plan: Record<string, any>) => Record<string, any>) {
    setPlans((current) => current.map((item) => (item.id === id ? { ...item, plan: updater({ ...item.plan }) } : item)));
  }

  function replacePlan(next: EditPlan) {
    setPlans((current) => current.map((item) => (item.id === next.id ? next : item)));
  }

  return (
    <main className="main">
      <section className="intro">
        <p className="eyebrow">AI video studio</p>
        <h1>上传长视频，生成可预览、可微调的短片</h1>
        <p className="introText">自动理解素材、匹配基调、渲染预览视频和封面，再按你的标题、字幕、模板和 BGM 重新出片。</p>
        <div className="toneChips">
          <span>电影风</span>
          <span>动漫风</span>
          <span>喜庆烟花</span>
          <span>高能卡点</span>
        </div>
      </section>

      <section className="panel generatorPanel">
        <div className="panelTitle">
          <span>生成设置</span>
          <strong>01</strong>
        </div>
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
            <span className="label">效果基调</span>
            <select className="select" value={creativeTone} onChange={(event) => setCreativeTone(event.target.value)}>
              <option value="auto">AI 自动判断</option>
              <option value="festival">喜庆烟花</option>
              <option value="cinematic">电影风</option>
              <option value="anime">动漫风</option>
              <option value="high_energy">高能卡点</option>
              <option value="clean_product">干净产品风</option>
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

      <section className="panel resultsPanel">
        <div className="panelTitle">
          <span>生成结果</span>
          <strong>{plans.length || "待生成"}</strong>
        </div>
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
              <div className="mediaPair">
                {typeof item.plan.cover_url === "string" && (
                  <div className="coverFrame">
                    <img className="coverImage" src={String(item.plan.cover_url)} alt={`方案 ${index + 1} 封面`} />
                    <span className="mediaBadge">Cover</span>
                  </div>
                )}
                {typeof item.plan.preview_url === "string" && (
                  <div className="previewFrame">
                    <video
                      className="previewVideo"
                      controls
                      preload="metadata"
                      src={buildPreviewUrl(item.plan)}
                    />
                    <span className="durationBadge">{item.duration_seconds ?? item.plan.duration ?? "-"}s</span>
                  </div>
                )}
              </div>
              <h3>方案 {index + 1}：{String(item.plan.title ?? "未命名方案")}</h3>
              <p>{String(item.plan.hook ?? "暂无钩子文案")}</p>
              <p className="muted">时长：{item.duration_seconds ?? item.plan.duration ?? "-"} 秒</p>
              <p>
                <span className="pill">{item.target_platform}</span>
                <span className="pill">{item.aspect_ratio}</span>
                <span className="pill">{item.plan.preview_type === "rendered_clip" ? "已渲染预览" : item.status}</span>
              </p>
              {Array.isArray(item.plan.render_features) && (
                <p className="muted">
                  AI 风格：{String(item.plan.visual_style ?? "-")} / {String(item.plan.effect_style ?? "-")} /{" "}
                  {String(item.plan.bgm?.style ?? "-")}
                </p>
              )}
              {item.plan.analysis_summary && <p className="muted">素材理解：{String(item.plan.analysis_summary)}</p>}
              {item.plan.strategy_note && <p className="muted">策略：{String(item.plan.strategy_note)}</p>}
              <p className="muted">{String(item.plan.publish_copy?.caption ?? "")}</p>
              <div className="editBox">
                <label className="field">
                  <span className="label">标题修改</span>
                  <input
                    className="input"
                    value={String(item.plan.title ?? "")}
                    onChange={(event) =>
                      updateLocalPlan(item.id, (plan) => ({
                        ...plan,
                        title: event.target.value,
                        cover: { ...(typeof plan.cover === "object" ? plan.cover : {}), title: event.target.value },
                      }))
                    }
                  />
                </label>
                <label className="field">
                  <span className="label">字幕轻量编辑</span>
                  <textarea
                    className="textarea"
                    value={normalizeCaptionLines(item.plan.caption_lines).join("\n")}
                    onChange={(event) =>
                      updateLocalPlan(item.id, (plan) => ({ ...plan, caption_lines: event.target.value.split("\n") }))
                    }
                  />
                </label>
                <div className="editGrid">
                  <label className="field">
                    <span className="label">模板选择</span>
                    <select
                      className="select"
                      value={String(item.plan.visual_style ?? "vivid_pain_point")}
                      onChange={(event) => updateLocalPlan(item.id, (plan) => ({ ...plan, visual_style: event.target.value }))}
                    >
                      <option value="vivid_pain_point">痛点大字版</option>
                      <option value="fast_impact">高能卡点版</option>
                      <option value="clean_product">干净产品版</option>
                      <option value="festival_bright">喜庆烟花版</option>
                      <option value="cinematic_warm">电影质感版</option>
                      <option value="anime_pop">动漫弹出版</option>
                    </select>
                  </label>
                  <label className="field">
                    <span className="label">BGM 配置</span>
                    <select
                      className="select"
                      value={String(item.plan.bgm?.style ?? "tech_pulse")}
                      onChange={(event) =>
                        updateLocalPlan(item.id, (plan) => ({ ...plan, bgm: { ...(plan.bgm ?? {}), style: event.target.value } }))
                      }
                    >
                      <option value="tech_pulse">科技律动</option>
                      <option value="upbeat_drive">高能节奏</option>
                      <option value="warm_brand">温暖品牌</option>
                      <option value="festival_pulse">喜庆热闹</option>
                      <option value="cinematic_rise">电影铺垫</option>
                      <option value="anime_upbeat">动漫活力</option>
                    </select>
                  </label>
                </div>
                <label className="field">
                  <span className="label">BGM 音量：{Number(item.plan.bgm?.volume ?? 0.22).toFixed(2)}</span>
                  <input
                    type="range"
                    min="0"
                    max="0.8"
                    step="0.01"
                    value={Number(item.plan.bgm?.volume ?? 0.22)}
                    onChange={(event) =>
                      updateLocalPlan(item.id, (plan) => ({
                        ...plan,
                        bgm: { ...(plan.bgm ?? {}), volume: Number(event.target.value) },
                      }))
                    }
                  />
                </label>
                <button className="button" type="button" disabled={editingId === item.id} onClick={() => applyPlanEdit(item)}>
                  {editingId === item.id ? "重渲染中..." : "应用并重渲染"}
                </button>
              </div>
              {editError && <p className="muted">{editError}</p>}
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

function normalizeCaptionLines(value: unknown) {
  if (Array.isArray(value)) {
    return value.map((line) => String(line)).filter(Boolean);
  }
  return [];
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
  if (plan.preview_type === "rendered_clip") {
    return String(plan.preview_url);
  }
  const clips = Array.isArray(plan.clips) ? plan.clips : [];
  const firstClip = clips[0];
  const start = Number(firstClip?.source_start ?? 0);
  const end = Number(firstClip?.source_end ?? 0);
  const fragment = Number.isFinite(end) && end > start ? `#t=${start},${end}` : `#t=${start}`;
  return `${plan.preview_url}${fragment}`;
}
