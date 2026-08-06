import { Link, useLocation } from "react-router-dom";
import { LayoutDashboard, ScrollText, Bell, Settings, X } from "lucide-react";
import { cn } from "../../lib/utils.ts";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "../ui/sheet.tsx";
import { Button } from "../ui/button.tsx";

const navItems = [
  { path: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { path: "/logs", label: "Logs", icon: ScrollText },
  { path: "/alerts", label: "Alerts", icon: Bell },
  { path: "/settings", label: "Settings", icon: Settings },
];

interface SidebarProps {
  mobileOpen?: boolean;
  onMobileClose?: () => void;
}

export function Sidebar({ mobileOpen, onMobileClose }: SidebarProps) {
  const location = useLocation();

  // Mobile sheet version
  if (mobileOpen !== undefined) {
    return (
      <Sheet open={mobileOpen} onOpenChange={(open) => !open && onMobileClose?.()}>
        <SheetContent side="left" className="w-[280px] p-0 flex flex-col">
          <SheetHeader className="px-6 py-4 border-b border-border">
            <div className="flex items-center justify-between">
              <SheetTitle className="text-lg font-bold">Log Analyzer</SheetTitle>
              <Button
                variant="ghost"
                size="icon"
                className="size-8"
                onClick={onMobileClose}
              >
                <X className="size-4" />
                <span className="sr-only">Close menu</span>
              </Button>
            </div>
          </SheetHeader>
          <nav className="flex-1 space-y-1 p-4 overflow-y-auto">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={onMobileClose}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors min-h-[44px]",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <Icon className="size-5 shrink-0" />
                  <span className="truncate">{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </SheetContent>
      </Sheet>
    );
  }

  // Desktop sidebar version
  return (
    <aside className="flex w-64 flex-col border-r border-border bg-card h-full">
      <div className="flex h-16 items-center border-b border-border px-6">
        <span className="text-lg font-bold text-card-foreground truncate">
          Log Analyzer
        </span>
      </div>
      <nav className="flex-1 space-y-1 p-4 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors min-h-[40px]",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <Icon className="size-4 shrink-0" />
              <span className="truncate">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
