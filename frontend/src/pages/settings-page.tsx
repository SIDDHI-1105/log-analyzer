import { useState, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  User,
  Key,
  Palette,
  Copy,
  Check,
  Trash2,
  Plus,
  Sun,
  Moon,
  Monitor,
  Camera,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useAuthStore } from "@/store/auth-store";
import { useTheme } from "@/hooks/use-theme";
import { getCurrentUser, updateCurrentUser } from "@/services/auth";
import { getApiKeys, createApiKey, revokeApiKey } from "@/services/api-keys";
import type { ApiKeyCreate } from "@/types/api-key";

const MAX_FILE_SIZE = 2 * 1024 * 1024; // 2MB

function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

export function SettingsPage() {
  const { user, token, updateUser } = useAuthStore();
  const { theme, setTheme } = useTheme();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { isLoading: profileLoading } = useQuery({
    queryKey: ["current-user"],
    queryFn: getCurrentUser,
    enabled: !!token && !user,
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

  const { data: apiKeys, isLoading: keysLoading } = useQuery({
    queryKey: ["api-keys"],
    queryFn: getApiKeys,
    enabled: !!token,
  });

  const [newKeyName, setNewKeyName] = useState("");
  const [newKeyDialogOpen, setNewKeyDialogOpen] = useState(false);
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [uploading, setUploading] = useState(false);

  const createMutation = useMutation({
    mutationFn: (data: ApiKeyCreate) => createApiKey(data),
    onSuccess: (data) => {
      setCreatedKey(data.key);
      toast.success("API key created successfully");
      queryClient.invalidateQueries({ queryKey: ["api-keys"] });
    },
    onError: () => {
      toast.error("Failed to create API key");
    },
  });

  const revokeMutation = useMutation({
    mutationFn: (id: string) => revokeApiKey(id),
    onSuccess: () => {
      toast.success("API key revoked");
      queryClient.invalidateQueries({ queryKey: ["api-keys"] });
    },
    onError: () => {
      toast.error("Failed to revoke API key");
    },
  });

  const avatarMutation = useMutation({
    mutationFn: updateCurrentUser,
    onSuccess: (updatedUser) => {
      updateUser(updatedUser);
      toast.success("Profile picture updated");
      setUploading(false);
    },
    onError: (error) => {
      console.error("Avatar upload error:", error);
      toast.error("Failed to update profile picture");
      setUploading(false);
    },
  });

  const handleCreateKey = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKeyName.trim()) return;
    createMutation.mutate({ name: newKeyName.trim() });
    setNewKeyName("");
  };

  const handleCopyKey = async () => {
    if (!createdKey) return;
    await navigator.clipboard.writeText(createdKey);
    setCopied(true);
    toast.success("API key copied to clipboard");
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCloseKeyDialog = () => {
    setNewKeyDialogOpen(false);
    setCreatedKey(null);
    setCopied(false);
  };

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      toast.error("Please select an image file");
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      toast.error("Image must be smaller than 2MB");
      return;
    }

    setUploading(true);
    try {
      const base64 = await fileToBase64(file);
      console.log("Base64 length:", base64.length);
      avatarMutation.mutate({ avatar_url: base64 });
    } catch (err) {
      console.error("File processing error:", err);
      toast.error("Failed to process image");
      setUploading(false);
    }

    // Reset input
    e.target.value = "";
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="mt-2 text-muted-foreground">
          Manage your account, API keys, and preferences.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="size-5" />
            Profile
          </CardTitle>
          <CardDescription>Your account information.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {profileLoading && !user ? (
            <p className="text-sm text-muted-foreground">Loading profile...</p>
          ) : user ? (
            <div className="space-y-6">
              {/* Avatar Section */}
              <div className="flex items-center gap-4">
                <div className="relative">
                  <Avatar className="size-20">
                    {user.avatar_url ? (
                      <AvatarImage src={user.avatar_url} alt={user.email} />
                    ) : null}
                    <AvatarFallback className="bg-primary text-primary-foreground text-2xl font-medium">
                      {initials}
                    </AvatarFallback>
                  </Avatar>
                  <button
                    onClick={handleAvatarClick}
                    disabled={uploading}
                    className="absolute -right-1 -bottom-1 flex size-8 items-center justify-center rounded-full bg-secondary border border-border shadow-sm hover:bg-accent transition-colors disabled:opacity-50"
                    title="Change profile picture"
                  >
                    <Camera className="size-4" />
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </div>
                <div>
                  <p className="text-sm font-medium">
                    {user.email.split("@")[0]}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Click the camera icon to upload a new picture
                  </p>
                  {uploading && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Uploading...
                    </p>
                  )}
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label className="text-muted-foreground">Email</Label>
                  <p className="text-sm font-medium">{user.email}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Role</Label>
                  <div className="mt-1">
                    <Badge variant="secondary">{user.role}</Badge>
                  </div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Status</Label>
                  <div className="mt-1">
                    <Badge variant={user.is_active ? "default" : "destructive"}>
                      {user.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                </div>
                <div>
                  <Label className="text-muted-foreground">User ID</Label>
                  <p className="font-mono text-xs text-muted-foreground">{user.id}</p>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Unable to load profile.</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Key className="size-5" />
              API Keys
            </CardTitle>
            <CardDescription>
              Manage API keys for external log ingestion.
            </CardDescription>
          </div>
          <Dialog open={newKeyDialogOpen} onOpenChange={setNewKeyDialogOpen}>
            <DialogTrigger render={<Button size="sm" />}>
              <Plus className="mr-2 size-4" />
              New Key
            </DialogTrigger>
            <DialogContent className="sm:max-w-lg">
              <DialogHeader>
                <DialogTitle>Create API Key</DialogTitle>
                <DialogDescription>
                  Generate a new API key for external systems to push logs.
                </DialogDescription>
              </DialogHeader>

              {createdKey ? (
                <div className="space-y-4">
                  <div className="rounded-md border border-yellow-500/20 bg-yellow-500/10 p-4">
                    <p className="text-sm font-medium text-yellow-600 dark:text-yellow-400">
                      Copy this key now. You won&apos;t be able to see it again.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Input
                      value={createdKey}
                      readOnly
                      className="font-mono text-sm"
                    />
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={handleCopyKey}
                    >
                      {copied ? (
                        <Check className="size-4 text-green-500" />
                      ) : (
                        <Copy className="size-4" />
                      )}
                    </Button>
                  </div>
                  <DialogFooter>
                    <Button onClick={handleCloseKeyDialog}>Done</Button>
                  </DialogFooter>
                </div>
              ) : (
                <form onSubmit={handleCreateKey} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="keyName">Key Name</Label>
                    <Input
                      id="keyName"
                      placeholder="e.g., Production Agent"
                      value={newKeyName}
                      onChange={(e) => setNewKeyName(e.target.value)}
                      required
                    />
                  </div>
                  <DialogFooter>
                    <Button
                      type="submit"
                      disabled={createMutation.isPending}
                    >
                      {createMutation.isPending ? "Creating..." : "Create Key"}
                    </Button>
                  </DialogFooter>
                </form>
              )}
            </DialogContent>
          </Dialog>
        </CardHeader>
        <CardContent>
          {keysLoading ? (
            <p className="text-sm text-muted-foreground">Loading keys...</p>
          ) : apiKeys && apiKeys.length > 0 ? (
            <div className="space-y-2">
              {apiKeys.map((key) => (
                <div
                  key={key.id}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium">{key.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {key.last_used
                        ? `Last used: ${new Date(key.last_used).toLocaleString()}`
                        : "Never used"}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {key.expires_at && (
                      <Badge variant="outline">
                        Expires {new Date(key.expires_at).toLocaleDateString()}
                      </Badge>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        if (confirm("Are you sure you want to revoke this API key?")) {
                          revokeMutation.mutate(key.id);
                        }
                      }}
                      disabled={revokeMutation.isPending}
                      title="Revoke"
                    >
                      <Trash2 className="size-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              No API keys. Create one to enable external log ingestion.
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="size-5" />
            Appearance
          </CardTitle>
          <CardDescription>Customize the look and feel.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4 sm:flex-row">
            {([
              { value: "light", label: "Light", icon: Sun },
              { value: "dark", label: "Dark", icon: Moon },
              { value: "system", label: "System", icon: Monitor },
            ] as const).map((option) => {
              const Icon = option.icon;
              const isActive = theme === option.value;
              return (
                <button
                  key={option.value}
                  onClick={() => setTheme(option.value)}
                  className={`flex flex-1 items-center gap-3 rounded-lg border p-4 text-left transition-colors ${
                    isActive
                      ? "border-primary bg-primary/5"
                      : "border-border hover:bg-accent"
                  }`}
                >
                  <Icon className="size-5" />
                  <div>
                    <p className="text-sm font-medium">{option.label}</p>
                    <p className="text-xs text-muted-foreground">
                      {option.value === "system"
                        ? "Follows your OS preference"
                        : `Always ${option.value} mode`}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
