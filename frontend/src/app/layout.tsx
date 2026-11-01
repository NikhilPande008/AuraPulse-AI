import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AuraPulse AI | Multimodal Event Planning & Reactive Contingency Engine",
  description: "Autonomous Multimodal Event Planning & Reactive Contingency Engine powered by Gemini 2.5 and Google Antigravity.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased selection:bg-purple-600 selection:text-white">
        <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md px-6 py-3.5">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-500 to-cyan-400 p-[1.5px] flex items-center justify-center shadow-lg shadow-purple-500/20">
                <div className="h-full w-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                  <span className="text-lg font-black bg-gradient-to-r from-purple-400 to-cyan-300 bg-clip-text text-transparent">
                    A
                  </span>
                </div>
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-base font-bold tracking-tight text-white">AuraPulse AI</span>
                  <span className="text-xs uppercase font-mono px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20 font-semibold">
                    v2.1.0
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Autonomous Multimodal Event Planning & Reactive Contingency Engine
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="hidden md:flex items-center space-x-3 text-xs text-slate-400 font-mono">
                <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800">
                  <span className="h-2 w-2 rounded-full bg-purple-400"></span>
                  Gemini 2.5 Flash & Pro
                </span>
                <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800">
                  <span className="h-2 w-2 rounded-full bg-blue-400"></span>
                  Google Maps & Sheets Fabric
                </span>
              </div>
              <a
                href="https://github.com"
                target="_blank"
                rel="noreferrer"
                className="px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700/60 text-slate-300 transition-colors"
              >
                PromptWars Spec
              </a>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
          {children}
        </main>
      </body>
    </html>
  );
}
