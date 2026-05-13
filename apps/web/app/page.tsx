import { Generator } from "../components/Generator";

export default function Home() {
  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">ClipSpark AI</div>
        <nav className="nav">
          <span className="navItem active">AI 创作</span>
          <span className="navItem">模板库</span>
          <span className="navItem">素材分析</span>
          <span className="navItem">作品</span>
        </nav>
        <button className="loginButton">本地预览</button>
      </header>
      <div className="subnav">
        <span className="subnavItem active">一键成片</span>
        <span className="subnavItem">爆款拆条</span>
        <span className="subnavItem">口播包装</span>
        <span className="subnavItem">带货短片</span>
        <span className="subnavItem">封面生成</span>
      </div>
      <Generator />
    </div>
  );
}
