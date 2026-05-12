import "./globals.css";

export const metadata = {
  title: "ClipSpark AI",
  description: "AI short video clipping tool",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
