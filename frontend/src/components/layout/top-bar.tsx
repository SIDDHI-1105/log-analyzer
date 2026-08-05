import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../store/auth-store.ts";
import {
  LogOut,
  User,
  Settings,
  KeyRound,
  Palette,
  ChevronDown,
  Menu,
} from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar.tsx";
import { Badge } from "../ui/badge.tsx";
import { Button } from "../ui/button.tsx";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu.tsx";

interface TopBarProps {
  onMenuToggle?: () => void;
}

export function TopBar({ onMenuToggle }: TopBarProps) {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const clearAuth = useAuthStore((state) => state.clearAuth);

  const handleLogout = () => {
    clearAuth();
  };

  const initials = user?.email
    ? user.email
        .split("@")[0]
        .split(/[._-]/)
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "U";

  const displayName = user?.email?.split("@")[0] || "User";

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-card px-4 sm:px-6 shrink-0">
      {/* Left side */}
      <div className="flex items-center gap-3 min-w-0 flex-1">
        {/* Hamburger menu - mobile only */}
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden size-9 shrink-0"
          onClick={onMenuToggle}
          aria-label="Open menu"
        >
          <Menu className="size-5" />
        </Button>

        <h2 className="text-xs sm:text-sm font-medium text-muted-foreground truncate hidden sm:block">
          Enterprise Observability Platform
        </h2>
      </div>

      {/* Right side - User dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm hover:bg-accent transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring min-w-0">
          <Avatar size="sm">
            {user?.avatar_url ? (
              <AvatarImage src={user.avatar_url} alt={displayName} />
            ) : null}
            <AvatarFallback className="bg-primary text-primary-foreground text-xs font-medium">
              {initials}
            </AvatarFallback>
          </Avatar>
          <div className="hidden md:flex flex-col items-start min-w-0">
            <span className="text-xs font-medium leading-none truncate max-w-[120px]">
              {displayName}
            </span>
            <span className="text-[10px] text-muted-foreground leading-none mt-0.5 truncate max-w-[120px]">
              {user?.role || "viewer"}
            </span>
          </div>
          <ChevronDown className="size-3 text-muted-foreground hidden md:block shrink-0" />
        </DropdownMenuTrigger>

        <DropdownMenuContent className="w-64 sm:w-72" align="end" sideOffset={8}>
          <DropdownMenuGroup>
            <DropdownMenuLabel className="p-0 font-normal">
              <div className="flex items-center gap-3 px-2 py-2.5">
                <Avatar>
                  {user?.avatar_url ? (
                    <AvatarImage src={user.avatar_url} alt={displayName} />
                  ) : null}
                  <AvatarFallback className="bg-primary text-primary-foreground font-medium">
                    {initials}
                  </AvatarFallback>
                </Avatar>
                <div className="flex flex-col gap-0.5 min-w-0 flex-1">
                  <p className="text-sm font-medium leading-none truncate">
                    {displayName}
                  </p>
                  <p className="text-xs text-muted-foreground leading-none truncate">
                    {user?.email || "user@example.com"}
                  </p>
                  <div className="mt-1">
                    <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                      {user?.role || "viewer"}
                    </Badge>
                  </div>
                </div>
              </div>
            </DropdownMenuLabel>
          </DropdownMenuGroup>

          <DropdownMenuSeparator />

          <DropdownMenuGroup>
            <DropdownMenuItem onClick={() => navigate("/settings")}>
              <User className="mr-2 size-4 shrink-0" />
              <span>My Profile</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => navigate("/settings")}>
              <Settings className="mr-2 size-4 shrink-0" />
              <span>Account Settings</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => navigate("/settings")}>
              <KeyRound className="mr-2 size-4 shrink-0" />
              <span>API Keys</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => navigate("/settings")}>
              <Palette className="mr-2 size-4 shrink-0" />
              <span>Appearance</span>
            </DropdownMenuItem>
          </DropdownMenuGroup>

          <DropdownMenuSeparator />

          <DropdownMenuGroup>
            <DropdownMenuItem
              onClick={handleLogout}
              className="text-destructive focus:text-destructive focus:bg-destructive/10"
            >
              <LogOut className="mr-2 size-4 shrink-0" />
              <span>Log out</span>
            </DropdownMenuItem>
          </DropdownMenuGroup>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
