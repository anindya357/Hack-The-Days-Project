"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bot, Code2, FileCode2, GitCompare, Home, Info, Library, Radar, Settings } from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: Home },
  { href: "/projects", label: "Projects", icon: Library },
  { href: "/crawler", label: "Crawler", icon: Radar },
  { href: "/chat", label: "Chat", icon: Bot },
  { href: "/generate", label: "Generate", icon: FileCode2 },
  { href: "/compare", label: "Compare", icon: GitCompare },
  { href: "/settings", label: "Settings", icon: Settings },
  { href: "/about", label: "About", icon: Info }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-mist">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-64 border-r border-line bg-white px-4 py-5 lg:block">
        <Link href="/" className="mb-8 flex items-center gap-3 rounded-md px-2">
          <span className="grid h-10 w-10 place-items-center rounded-md bg-ink text-white">
            <Code2 size={20} />
          </span>
          <span>
            <span className="block text-base font-semibold">DevDocs AI</span>
            <span className="block text-xs text-slate-500">Universal docs assistant</span>
          </span>
        </Link>
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex h-11 items-center gap-3 rounded-md px-3 text-sm font-medium transition ${
                  active ? "bg-ink text-white" : "text-slate-600 hover:bg-slate-100 hover:text-ink"
                }`}
              >
                <Icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <div className="lg:pl-64">
        <header className="sticky top-0 z-10 border-b border-line bg-white/90 px-4 py-3 backdrop-blur lg:hidden">
          <div className="flex items-center gap-3 overflow-x-auto">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-label={item.label}
                  title={item.label}
                  className={`grid h-10 w-10 shrink-0 place-items-center rounded-md ${
                    active ? "bg-ink text-white" : "bg-slate-100 text-slate-600"
                  }`}
                >
                  <Icon size={18} />
                </Link>
              );
            })}
          </div>
        </header>
        <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
