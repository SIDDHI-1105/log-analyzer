import { useAuthStore } from "@/store/auth-store";
import { LogOut, User } from "lucide-react";
import { Button } from "@/components/ui/button";

export function TopBar() {
  const clearAuth = useAuthStore((state) => state.clearAuth);

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-card px-6">
      <h2 className="text-sm font-medium text-muted-foreground">Enterprise Observability Platform</h2>
      <div className="flex items-center gap-4">
        <span className="flex items-center gap-2 text-sm text-muted-foreground">
          <User className="size-4" />
          <span className="hidden sm:inline">User</span>
        </span>
        <Button variant="ghost" size="icon" onClick={clearAuth} title="Logout">
          <LogOut className="size-4" />
        </Button>
      </div>
    </header>
  );
}
