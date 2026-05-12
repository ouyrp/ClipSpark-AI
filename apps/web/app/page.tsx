import { Generator } from "../components/Generator";

export default function Home() {
  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">ClipSpark AI</div>
        <div className="muted">AI 一键生成可发布短视频</div>
      </header>
      <Generator />
    </div>
  );
}
