"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  Asset,
  EditPlan,
  Project,
  analyzeAsset,
  createProject,
  generatePlans,
  listAssets,
  listEditPlans,
  listProjects,
  rerenderEditPlan,
  updateEditPlan,
  uploadAsset,
} from "../lib/api";

type Step = "idle" | "creating" | "uploading" | "generating" | "done" | "error";
type View = "create" | "templates" | "analysis" | "works" | "cover" | "viral" | "talking" | "sales";

const templates = [
  {
    id: "cinematic",
    name: "电影风短片",
    tone: "cinematic",
    platform: "douyin",
    ratio: "9:16",
    goal: "剪出有电影质感的品牌短片，保留情绪铺垫、慢切和氛围字幕。",
    tags: ["电影感", "胶片颗粒", "氛围 BGM"],
  },
  {
    id: "anime",
    name: "动漫弹幕风",
    tone: "anime",
    platform: "douyin",
    ratio: "9:16",
    goal: "剪出节奏轻快的动漫风短片，加入弹出字幕、速度线和活力 BGM。",
    tags: ["动漫风", "弹出字幕", "速度线"],
  },
  {
    id: "festival",
    name: "喜庆烟花版",
    tone: "festival",
    platform: "kuaishou",
    ratio: "9:16",
    goal: "剪出热闹喜庆的活动短片，强调开场冲击、烟花特效和高亮标题。",
    tags: ["烟花", "闪光转场", "热闹"],
  },
  {
    id: "high_energy",
    name: "高能卡点版",
    tone: "high_energy",
    platform: "tiktok",
    ratio: "9:16",
    goal: "剪出高能卡点短片，把高光片段前置，强化节奏闪白和鼓点转场。",
    tags: ["卡点", "闪白", "快节奏"],
  },
  {
    id: "clean_product",
    name: "产品卖点版",
    tone: "clean_product",
    platform: "xiaohongshu",
    ratio: "9:16",
    goal: "剪出干净清爽的产品种草短片，突出卖点、字幕层级和封面可读性。",
    tags: ["产品", "种草", "清爽"],
  },
];

const workflowModules = {
  viral: {
    eyebrow: "viral cutter",
    title: "爆款拆条",
    description: "把长视频拆成多个高开场、高冲突、高完播潜力的短片方向，适合访谈、直播、课程和活动素材。",
    projectName: "爆款拆条项目",
    tone: "high_energy",
    platform: "douyin",
    ratio: "9:16",
    goal: "从长视频里拆出 3 条爆款潜力短片：前三秒强钩子、冲突或结果前置、节奏快、字幕关键词突出。",
    cards: [
      ["痛点前置", "先把用户最关心的问题放在 0-3 秒，制造继续看的理由。"],
      ["结果先给", "先展示结论、成果或反差，再回到过程片段。"],
      ["高光连剪", "优先选择表情、动作、转折和信息密度高的片段。"],
    ],
  },
  talking: {
    eyebrow: "talking package",
    title: "口播包装",
    description: "面向口播、知识分享、课程讲解，把内容包装成标题清晰、字幕好读、节奏稳定的短片。",
    projectName: "口播包装项目",
    tone: "clean_product",
    platform: "xiaohongshu",
    ratio: "9:16",
    goal: "把口播视频包装成清晰易懂的短片：保留核心观点，生成大标题、分段字幕、关键词高亮和温和 BGM。",
    cards: [
      ["观点标题", "自动提炼一句主标题，让观众一眼知道这条讲什么。"],
      ["字幕分层", "短句字幕叠加关键词，让口播信息更容易扫读。"],
      ["停顿优化", "减少无效等待，保留自然语气和重点停顿。"],
    ],
  },
  sales: {
    eyebrow: "commerce clip",
    title: "带货短片",
    description: "适合产品介绍、探店、种草和直播切片，强调卖点、场景、价格/行动引导和封面可读性。",
    projectName: "带货短片项目",
    tone: "clean_product",
    platform: "xiaohongshu",
    ratio: "9:16",
    goal: "剪出 3 条带货短片：突出产品卖点、使用场景、信任背书和行动引导，封面标题要清楚可读。",
    cards: [
      ["卖点提纯", "从素材里提炼 1-2 个最容易转化的核心卖点。"],
      ["场景证明", "优先选择展示使用过程、对比效果和真实反馈的画面。"],
      ["转化结尾", "结尾补上收藏、咨询、下单或进店的轻量行动引导。"],
    ],
  },
} as const;

export function Generator() {
  const [view, setView] = useState<View>("create");
  const [projectName, setProjectName] = useState("我的第一条 AI 剪辑项目");
  const [targetPlatform, setTargetPlatform] = useState("douyin");
  const [aspectRatio, setAspectRatio] = useState("9:16");
  const [creativeTone, setCreativeTone] = useState("auto");
  const [aiProvider, setAiProvider] = useState("gemini");
  const [userGoal, setUserGoal] = useState("剪出 3 条可以直接发的短视频");
  const [file, setFile] = useState<File | null>(null);
  const [analysisFile, setAnalysisFile] = useState<File | null>(null);
  const [analysisResult, setAnalysisResult] = useState<Record<string, any> | null>(null);
  const [step, setStep] = useState<Step>("idle");
  const [error, setError] = useState("");
  const [project, setProject] = useState<Project | null>(null);
  const [asset, setAsset] = useState<Asset | null>(null);
  const [plans, setPlans] = useState<EditPlan[]>([]);
  const [editingId, setEditingId] = useState("");
  const [editError, setEditError] = useState("");
  const [libraryProjects, setLibraryProjects] = useState<Project[]>([]);
  const [libraryAssets, setLibraryAssets] = useState<Record<string, Asset[]>>({});
  const [libraryPlans, setLibraryPlans] = useState<EditPlan[]>([]);
  const [libraryLoading, setLibraryLoading] = useState(false);
  const [selectedCoverPlanId, setSelectedCoverPlanId] = useState("");
  const [coverTitle, setCoverTitle] = useState("");

  const allPlans = useMemo(() => [...plans, ...libraryPlans], [plans, libraryPlans]);
  const selectedCoverPlan = allPlans.find((item) => item.id === selectedCoverPlanId) ?? allPlans[0];

  useEffect(() => {
    if ((view === "works" || view === "cover") && libraryProjects.length === 0) {
      void refreshLibrary();
    }
  }, [view]);

  useEffect(() => {
    if (selectedCoverPlan && !selectedCoverPlanId) {
      setSelectedCoverPlanId(selectedCoverPlan.id);
      setCoverTitle(String(selectedCoverPlan.plan.title ?? selectedCoverPlan.plan.cover?.title ?? ""));
    }
  }, [selectedCoverPlan, selectedCoverPlanId]);

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
        aiProvider,
      });
      setPlans(generatedPlans);
      setStep("done");
      await refreshLibrary();
    } catch (err) {
      setStep("error");
      setError(err instanceof Error ? err.message : "生成失败");
    }
  }

  async function runAnalysis(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!analysisFile) {
      setError("请先选择一个要分析的视频文件。");
      return;
    }
    setError("");
    setAnalysisResult(null);
    try {
      setStep("creating");
      const createdProject = await createProject(`素材分析 - ${analysisFile.name}`);
      setProject(createdProject);
      setStep("uploading");
      const uploadedAsset = await uploadAsset(createdProject.id, analysisFile);
      setAsset(uploadedAsset);
      setStep("generating");
      const result = await analyzeAsset(createdProject.id, uploadedAsset.id);
      setAnalysisResult(result);
      setStep("done");
      await refreshLibrary();
    } catch (err) {
      setStep("error");
      setError(err instanceof Error ? err.message : "素材分析失败");
    }
  }

  async function refreshLibrary() {
    setLibraryLoading(true);
    try {
      const projects = await listProjects();
      setLibraryProjects(projects);
      const pairs = await Promise.all(
        projects.slice(0, 12).map(async (item) => {
          const [projectAssets, projectPlans] = await Promise.all([listAssets(item.id), listEditPlans(item.id)]);
          return { project: item, assets: projectAssets, plans: projectPlans };
        }),
      );
      setLibraryAssets(Object.fromEntries(pairs.map((item) => [item.project.id, item.assets])));
      setLibraryPlans(pairs.flatMap((item) => item.plans));
    } finally {
      setLibraryLoading(false);
    }
  }

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
      replaceLibraryPlan(rendered);
      if (rendered.status === "render_failed") {
        setEditError(String(rendered.plan.render_error ?? "重渲染失败"));
      }
    } catch (err) {
      setEditError(err instanceof Error ? err.message : "编辑失败");
    } finally {
      setEditingId("");
    }
  }

  async function regenerateCover() {
    if (!selectedCoverPlan) return;
    setEditingId(selectedCoverPlan.id);
    setEditError("");
    try {
      const updated = await updateEditPlan(selectedCoverPlan.id, {
        title: coverTitle,
        hook: String(selectedCoverPlan.plan.hook ?? ""),
        caption_lines: normalizeCaptionLines(selectedCoverPlan.plan.caption_lines),
        visual_style: String(selectedCoverPlan.plan.visual_style ?? "vivid_pain_point"),
        effect_style: String(selectedCoverPlan.plan.effect_style ?? "vignette_focus"),
        bgm_style: String(selectedCoverPlan.plan.bgm?.style ?? "tech_pulse"),
        bgm_volume: Number(selectedCoverPlan.plan.bgm?.volume ?? 0.22),
      });
      const rendered = await rerenderEditPlan(updated.id);
      replacePlan(rendered);
      replaceLibraryPlan(rendered);
    } catch (err) {
      setEditError(err instanceof Error ? err.message : "封面重生成失败");
    } finally {
      setEditingId("");
    }
  }

  function applyTemplate(template: (typeof templates)[number]) {
    setCreativeTone(template.tone);
    setTargetPlatform(template.platform);
    setAspectRatio(template.ratio);
    setUserGoal(template.goal);
    setView("create");
  }

  function applyWorkflow(kind: keyof typeof workflowModules) {
    const workflow = workflowModules[kind];
    setProjectName(workflow.projectName);
    setCreativeTone(workflow.tone);
    setTargetPlatform(workflow.platform);
    setAspectRatio(workflow.ratio);
    setUserGoal(workflow.goal);
    setView("create");
  }

  function updateLocalPlan(id: string, updater: (plan: Record<string, any>) => Record<string, any>) {
    setPlans((current) => current.map((item) => (item.id === id ? { ...item, plan: updater({ ...item.plan }) } : item)));
    setLibraryPlans((current) => current.map((item) => (item.id === id ? { ...item, plan: updater({ ...item.plan }) } : item)));
  }

  function replacePlan(next: EditPlan) {
    setPlans((current) => current.map((item) => (item.id === next.id ? next : item)));
  }

  function replaceLibraryPlan(next: EditPlan) {
    setLibraryPlans((current) => current.map((item) => (item.id === next.id ? next : item)));
  }

  return (
    <>
      <header className="topbar">
        <div className="brand">ClipSpark AI</div>
        <nav className="nav">
          <button className={navClass(["create", "viral", "talking", "sales", "cover"].includes(view))} onClick={() => setView("create")}>AI 创作</button>
          <button className={navClass(view === "templates")} onClick={() => setView("templates")}>模板库</button>
          <button className={navClass(view === "analysis")} onClick={() => setView("analysis")}>素材分析</button>
          <button className={navClass(view === "works")} onClick={() => setView("works")}>作品</button>
        </nav>
        <button className="loginButton" onClick={() => void refreshLibrary()}>刷新</button>
      </header>
      <div className="subnav">
        <button className={subnavClass(view === "create")} onClick={() => setView("create")}>一键成片</button>
        <button className={subnavClass(view === "viral")} onClick={() => setView("viral")}>爆款拆条</button>
        <button className={subnavClass(view === "talking")} onClick={() => setView("talking")}>口播包装</button>
        <button className={subnavClass(view === "sales")} onClick={() => setView("sales")}>带货短片</button>
        <button className={subnavClass(view === "cover")} onClick={() => setView("cover")}>封面生成</button>
      </div>

      {view === "create" && renderCreate()}
      {view === "templates" && renderTemplates()}
      {view === "analysis" && renderAnalysis()}
      {view === "works" && renderWorks()}
      {view === "cover" && renderCover()}
      {view === "viral" && renderWorkflow("viral")}
      {view === "talking" && renderWorkflow("talking")}
      {view === "sales" && renderWorkflow("sales")}
    </>
  );

  function renderCreate() {
    const isWorking = ["creating", "uploading", "generating"].includes(step);
    return (
      <main className="main">
        <section className="intro">
          <p className="eyebrow">AI video studio</p>
          <h1>上传长视频，生成可预览、可微调的短片</h1>
          <p className="introText">自动理解素材、匹配基调、渲染预览视频和封面，再按你的标题、字幕、模板和 BGM 重新出片。</p>
          <div className="toneChips">{templates.slice(0, 4).map((item) => <span key={item.id}>{item.tags[0]}</span>)}</div>
        </section>

        <section className="panel generatorPanel">
          <div className="panelTitle"><span>生成设置</span><strong>01</strong></div>
          <form onSubmit={onSubmit}>
            <ProjectFormFields />
            <button className="button" disabled={isWorking} type="submit">{isWorking ? "生成中..." : "上传并生成剪辑方案"}</button>
          </form>
          <StatusBlock />
        </section>

        <section className="panel resultsPanel">
          <div className="panelTitle"><span>生成结果</span><strong>{plans.length || "待生成"}</strong></div>
          <div className="stack">
            {project && <ProjectSummary project={project} asset={asset} />}
            {plans.length === 0 && <p className="muted">上传视频后，这里会展示 AI 生成的 3 条短视频剪辑方案。</p>}
            {plans.map((item, index) => <PlanCard item={item} index={index} key={item.id} editable />)}
          </div>
        </section>
      </main>
    );
  }

  function renderTemplates() {
    return (
      <main className="wideMain">
        <section className="intro">
          <p className="eyebrow">template library</p>
          <h1>模板库</h1>
          <p className="introText">选择一个剪辑基调，系统会回填平台、比例、风格目标和特效策略，再进入一键成片。</p>
        </section>
        <section className="templateGrid">
          {templates.map((item) => (
            <article className="templateCard" key={item.id}>
              <div className={`templatePreview ${item.id}`} />
              <h3>{item.name}</h3>
              <p>{item.goal}</p>
              <p>{item.tags.map((tag) => <span className="pill" key={tag}>{tag}</span>)}</p>
              <button className="button" type="button" onClick={() => applyTemplate(item)}>套用模板</button>
            </article>
          ))}
        </section>
      </main>
    );
  }

  function renderWorkflow(kind: keyof typeof workflowModules) {
    const workflow = workflowModules[kind];
    return (
      <main className="main">
        <section className="intro">
          <p className="eyebrow">{workflow.eyebrow}</p>
          <h1>{workflow.title}</h1>
          <p className="introText">{workflow.description}</p>
          <div className="toneChips">{workflow.cards.map(([title]) => <span key={title}>{title}</span>)}</div>
        </section>

        <section className="panel generatorPanel">
          <div className="panelTitle"><span>{workflow.title}设置</span><strong>已实现</strong></div>
          <label className="field">
            <span className="label">推荐平台</span>
            <input className="input" value={platformLabel(workflow.platform)} readOnly />
          </label>
          <label className="field">
            <span className="label">推荐比例</span>
            <input className="input" value={workflow.ratio} readOnly />
          </label>
          <label className="field">
            <span className="label">策略目标</span>
            <textarea className="textarea" value={workflow.goal} readOnly />
          </label>
          <button className="button" type="button" onClick={() => applyWorkflow(kind)}>套用并去生成</button>
        </section>

        <section className="panel resultsPanel">
          <div className="panelTitle"><span>剪辑策略</span><strong>3 步</strong></div>
          <div className="templateGrid workflowGrid">
            {workflow.cards.map(([title, body], index) => (
              <article className="templateCard workflowCard" key={title}>
                <div className={`workflowNumber n${index + 1}`}>{index + 1}</div>
                <h3>{title}</h3>
                <p>{body}</p>
              </article>
            ))}
          </div>
          <div className="workflowAction">
            <button className="button compactButton" type="button" onClick={() => applyWorkflow(kind)}>使用这个流程</button>
          </div>
        </section>
      </main>
    );
  }

  function renderAnalysis() {
    return (
      <main className="main">
        <section className="intro">
          <p className="eyebrow">asset intelligence</p>
          <h1>素材分析</h1>
          <p className="introText">单独上传素材，查看基础信息、关键帧、视觉理解状态和适合的剪辑基调。</p>
        </section>
        <section className="panel generatorPanel">
          <div className="panelTitle"><span>上传分析</span><strong>02</strong></div>
          <form onSubmit={runAnalysis}>
            <label className="field">
              <span className="label">视频素材</span>
              <input className="input" type="file" accept="video/*" onChange={(event) => setAnalysisFile(event.target.files?.[0] ?? null)} />
            </label>
            <label className="field">
              <span className="label">AI 模型</span>
              <ModelSelect />
            </label>
            <button className="button" type="submit">开始分析</button>
          </form>
          <StatusBlock />
        </section>
        <section className="panel resultsPanel">
          <div className="panelTitle"><span>分析结果</span><strong>{analysisResult ? "完成" : "待分析"}</strong></div>
          {!analysisResult && <p className="muted">分析后会展示关键帧、视频元数据和视觉模型返回摘要。</p>}
          {analysisResult && (
            <div className="analysisGrid">
              <InfoRow label="文件" value={String(analysisResult.filename ?? "-")} />
              <InfoRow label="时长" value={`${analysisResult.duration_seconds ?? "-"} 秒`} />
              <InfoRow label="尺寸" value={`${analysisResult.width ?? "-"} x ${analysisResult.height ?? "-"}`} />
              <InfoRow label="帧率" value={String(analysisResult.fps ?? "-")} />
              <InfoRow label="视觉摘要" value={String(analysisResult.analysis?.summary ?? "-")} wide />
              <InfoRow label="ASR 状态" value={String(analysisResult.analysis?.audio?.status ?? "-")} />
              <div className="frameStrip">
                {Array.isArray(analysisResult.analysis?.frames) && analysisResult.analysis.frames.map((url: string) => (
                  <img src={url} alt="关键帧" key={url} />
                ))}
              </div>
            </div>
          )}
        </section>
      </main>
    );
  }

  function renderWorks() {
    return (
      <main className="wideMain">
        <section className="intro">
          <p className="eyebrow">works</p>
          <h1>作品</h1>
          <p className="introText">查看最近项目、上传素材和已经渲染的短视频预览。</p>
          <button className="button compactButton" type="button" onClick={() => void refreshLibrary()}>{libraryLoading ? "刷新中..." : "刷新作品"}</button>
        </section>
        <section className="workGrid">
          {libraryProjects.length === 0 && <div className="panel emptyPanel">还没有项目。先去一键成片上传一个视频。</div>}
          {libraryProjects.map((item) => {
            const projectPlans = libraryPlans.filter((plan) => plan.project_id === item.id);
            return (
              <article className="workCard" key={item.id}>
                <h3>{item.name}</h3>
                <p><span className="pill">{item.status}</span><span className="pill">{projectPlans.length} 个方案</span></p>
                {(libraryAssets[item.id] ?? []).map((projectAsset) => (
                  <p className="muted" key={projectAsset.id}>{projectAsset.filename} · {projectAsset.duration_seconds ?? "-"}s</p>
                ))}
                <div className="miniPreviewGrid">
                  {projectPlans.slice(0, 3).map((plan) => <MiniPreview plan={plan} key={plan.id} />)}
                </div>
              </article>
            );
          })}
        </section>
      </main>
    );
  }

  function renderCover() {
    return (
      <main className="main">
        <section className="intro">
          <p className="eyebrow">cover studio</p>
          <h1>封面生成</h1>
          <p className="introText">选择一个已有剪辑方案，修改封面标题并重新渲染封面图和预览。</p>
        </section>
        <section className="panel generatorPanel">
          <div className="panelTitle"><span>封面设置</span><strong>04</strong></div>
          <label className="field">
            <span className="label">选择方案</span>
            <select
              className="select"
              value={selectedCoverPlan?.id ?? ""}
              onChange={(event) => {
                const next = allPlans.find((item) => item.id === event.target.value);
                setSelectedCoverPlanId(event.target.value);
                setCoverTitle(String(next?.plan.title ?? next?.plan.cover?.title ?? ""));
              }}
            >
              {allPlans.map((item) => <option value={item.id} key={item.id}>{String(item.plan.title ?? item.id)}</option>)}
            </select>
          </label>
          <label className="field">
            <span className="label">封面标题</span>
            <input className="input" value={coverTitle} onChange={(event) => setCoverTitle(event.target.value)} />
          </label>
          <button className="button" disabled={!selectedCoverPlan || editingId === selectedCoverPlan.id} onClick={() => void regenerateCover()}>
            {editingId === selectedCoverPlan?.id ? "生成中..." : "重新生成封面"}
          </button>
          {editError && <p className="muted">{editError}</p>}
        </section>
        <section className="panel resultsPanel">
          <div className="panelTitle"><span>封面预览</span><strong>{selectedCoverPlan ? "可编辑" : "暂无"}</strong></div>
          {!selectedCoverPlan && <p className="muted">先生成一个剪辑方案，或刷新作品后选择历史方案。</p>}
          {selectedCoverPlan && <PlanCard item={selectedCoverPlan} index={0} />}
        </section>
      </main>
    );
  }

  function ProjectFormFields() {
    return (
      <>
        <label className="field"><span className="label">项目名称</span><input className="input" value={projectName} onChange={(event) => setProjectName(event.target.value)} /></label>
        <label className="field"><span className="label">视频素材</span><input className="input" type="file" accept="video/*" onChange={(event) => setFile(event.target.files?.[0] ?? null)} /></label>
        <label className="field"><span className="label">目标平台</span><PlatformSelect /></label>
        <label className="field"><span className="label">画面比例</span><RatioSelect /></label>
        <label className="field"><span className="label">效果基调</span><ToneSelect /></label>
        <label className="field"><span className="label">AI 模型</span><ModelSelect /></label>
        <label className="field"><span className="label">生成目标</span><textarea className="textarea" value={userGoal} onChange={(event) => setUserGoal(event.target.value)} /></label>
      </>
    );
  }

  function PlatformSelect() {
    return (
      <select className="select" value={targetPlatform} onChange={(event) => setTargetPlatform(event.target.value)}>
        <option value="douyin">抖音</option>
        <option value="xiaohongshu">小红书</option>
        <option value="kuaishou">快手</option>
        <option value="tiktok">TikTok</option>
        <option value="youtube_shorts">YouTube Shorts</option>
      </select>
    );
  }

  function RatioSelect() {
    return (
      <select className="select" value={aspectRatio} onChange={(event) => setAspectRatio(event.target.value)}>
        <option value="9:16">9:16 竖屏</option>
        <option value="1:1">1:1 方形</option>
        <option value="16:9">16:9 横屏</option>
      </select>
    );
  }

  function ToneSelect() {
    return (
      <select className="select" value={creativeTone} onChange={(event) => setCreativeTone(event.target.value)}>
        <option value="auto">AI 自动判断</option>
        <option value="festival">喜庆烟花</option>
        <option value="cinematic">电影风</option>
        <option value="anime">动漫风</option>
        <option value="high_energy">高能卡点</option>
        <option value="clean_product">干净产品风</option>
      </select>
    );
  }

  function ModelSelect() {
    return (
      <select className="select" value={aiProvider} onChange={(event) => setAiProvider(event.target.value)}>
        <option value="gemini">Gemini Flash 免费层（推荐视频理解）</option>
        <option value="openrouter_free">OpenRouter 免费路由（备选）</option>
        <option value="ollama">本地 Ollama 多模态（无云端费用）</option>
        <option value="bailian">百炼普通 API（非 Coding Plan）</option>
      </select>
    );
  }

  function StatusBlock() {
    return (
      <>
        {step !== "idle" && <p className="muted">当前状态：<span className={step === "done" ? "status" : ""}>{stepLabel(step)}</span></p>}
        {error && <p className="muted">{error}</p>}
      </>
    );
  }

  function PlanCard({ item, index, editable = false }: { item: EditPlan; index: number; editable?: boolean }) {
    return (
      <article className="result">
        <div className="mediaPair">
          {typeof item.plan.cover_url === "string" && (
            <div className="coverFrame"><img className="coverImage" src={String(item.plan.cover_url)} alt={`方案 ${index + 1} 封面`} /><span className="mediaBadge">Cover</span></div>
          )}
          {typeof item.plan.preview_url === "string" && (
            <div className="previewFrame"><video className="previewVideo" controls preload="metadata" src={buildPreviewUrl(item.plan)} /><span className="durationBadge">{item.duration_seconds ?? item.plan.duration ?? "-"}s</span></div>
          )}
        </div>
        <h3>方案 {index + 1}：{String(item.plan.title ?? "未命名方案")}</h3>
        <p>{String(item.plan.hook ?? "暂无钩子文案")}</p>
        <p className="muted">时长：{item.duration_seconds ?? item.plan.duration ?? "-"} 秒</p>
        <p><span className="pill">{item.target_platform}</span><span className="pill">{item.aspect_ratio}</span><span className="pill">{item.plan.preview_type === "rendered_clip" ? "已渲染预览" : item.status}</span></p>
        <p className="muted">AI 风格：{String(item.plan.visual_style ?? "-")} / {String(item.plan.effect_style ?? "-")} / {String(item.plan.bgm?.style ?? "-")}</p>
        {item.plan.analysis_summary && <p className="muted">素材理解：{String(item.plan.analysis_summary)}</p>}
        {item.plan.strategy_note && <p className="muted">策略：{String(item.plan.strategy_note)}</p>}
        <p className="muted">{String(item.plan.publish_copy?.caption ?? "")}</p>
        {editable && <PlanEditor item={item} />}
      </article>
    );
  }

  function PlanEditor({ item }: { item: EditPlan }) {
    return (
      <div className="editBox">
        <label className="field"><span className="label">标题修改</span><input className="input" value={String(item.plan.title ?? "")} onChange={(event) => updateLocalPlan(item.id, (plan) => ({ ...plan, title: event.target.value, cover: { ...(typeof plan.cover === "object" ? plan.cover : {}), title: event.target.value } }))} /></label>
        <label className="field"><span className="label">字幕轻量编辑</span><textarea className="textarea" value={normalizeCaptionLines(item.plan.caption_lines).join("\n")} onChange={(event) => updateLocalPlan(item.id, (plan) => ({ ...plan, caption_lines: event.target.value.split("\n") }))} /></label>
        <div className="editGrid">
          <label className="field"><span className="label">模板选择</span><select className="select" value={String(item.plan.visual_style ?? "vivid_pain_point")} onChange={(event) => updateLocalPlan(item.id, (plan) => ({ ...plan, visual_style: event.target.value }))}>{visualOptions()}</select></label>
          <label className="field"><span className="label">BGM 配置</span><select className="select" value={String(item.plan.bgm?.style ?? "tech_pulse")} onChange={(event) => updateLocalPlan(item.id, (plan) => ({ ...plan, bgm: { ...(plan.bgm ?? {}), style: event.target.value } }))}>{bgmOptions()}</select></label>
        </div>
        <label className="field"><span className="label">BGM 音量：{Number(item.plan.bgm?.volume ?? 0.22).toFixed(2)}</span><input type="range" min="0" max="0.8" step="0.01" value={Number(item.plan.bgm?.volume ?? 0.22)} onChange={(event) => updateLocalPlan(item.id, (plan) => ({ ...plan, bgm: { ...(plan.bgm ?? {}), volume: Number(event.target.value) } }))} /></label>
        <button className="button" type="button" disabled={editingId === item.id} onClick={() => void applyPlanEdit(item)}>{editingId === item.id ? "重渲染中..." : "应用并重渲染"}</button>
        {editError && <p className="muted">{editError}</p>}
      </div>
    );
  }
}

function ProjectSummary({ project, asset }: { project: Project; asset: Asset | null }) {
  return (
    <div className="result">
      <h3>{project.name}</h3>
      <p className="muted">项目 ID：{project.id}</p>
      {asset && <p className="muted">素材：{asset.filename} · {asset.duration_seconds ?? "-"}s</p>}
    </div>
  );
}

function InfoRow({ label, value, wide = false }: { label: string; value: string; wide?: boolean }) {
  return <div className={wide ? "infoRow wide" : "infoRow"}><span>{label}</span><strong>{value}</strong></div>;
}

function MiniPreview({ plan }: { plan: EditPlan }) {
  return (
    <div className="miniPreview">
      {typeof plan.plan.cover_url === "string" && <img src={String(plan.plan.cover_url)} alt={String(plan.plan.title ?? "作品封面")} />}
      <strong>{String(plan.plan.title ?? "未命名方案")}</strong>
    </div>
  );
}

function visualOptions() {
  return (
    <>
      <option value="vivid_pain_point">痛点大字版</option>
      <option value="fast_impact">高能卡点版</option>
      <option value="clean_product">干净产品版</option>
      <option value="festival_bright">喜庆烟花版</option>
      <option value="cinematic_warm">电影质感版</option>
      <option value="anime_pop">动漫弹出版</option>
    </>
  );
}

function bgmOptions() {
  return (
    <>
      <option value="tech_pulse">科技律动</option>
      <option value="upbeat_drive">高能节奏</option>
      <option value="warm_brand">温暖品牌</option>
      <option value="festival_pulse">喜庆热闹</option>
      <option value="cinematic_rise">电影铺垫</option>
      <option value="anime_upbeat">动漫活力</option>
    </>
  );
}

function navClass(active: boolean) {
  return active ? "navItem active" : "navItem";
}

function subnavClass(active: boolean) {
  return active ? "subnavItem active" : "subnavItem";
}

function platformLabel(value: string) {
  const labels: Record<string, string> = {
    douyin: "抖音",
    xiaohongshu: "小红书",
    kuaishou: "快手",
    tiktok: "TikTok",
    youtube_shorts: "YouTube Shorts",
  };
  return labels[value] ?? value;
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
    generating: "AI 生成与素材理解",
    done: "完成",
    error: "失败",
  };
  return labels[step];
}

function buildPreviewUrl(plan: Record<string, any>) {
  const url = String(plan.preview_url ?? "");
  if (!url || url.startsWith("http")) {
    return url;
  }
  return `http://localhost:8000${url}`;
}
