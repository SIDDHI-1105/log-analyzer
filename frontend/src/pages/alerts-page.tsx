import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  Bell,
  Plus,
  Trash2,
  Power,
  History,
  Search,
  Filter,

  FileText,
  Pencil,
  X,

  ChevronRight,
  Clock,
  Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  getAlertRules,
  getAlertHistory,
  createAlertRule,
  deleteAlertRule,
  updateAlertRule,
} from "@/services/alerts";
import type { AlertRule, AlertRuleCreate, AlertRuleUpdate, Severity } from "@/types/alert";

const SEVERITIES: Severity[] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"];

function getSeverityColor(severity: string): "default" | "secondary" | "destructive" | "outline" {
  switch (severity) {
    case "CRITICAL":
    case "ERROR":
      return "destructive";
    case "WARNING":
      return "outline";
    case "INFO":
      return "secondary";
    default:
      return "default";
  }
}

function RuleSkeleton() {
  return (
    <div className="space-y-2">
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-full" />
    </div>
  );
}

function HistorySkeleton() {
  return (
    <div className="space-y-2">
      <Skeleton className="h-14 w-full" />
      <Skeleton className="h-14 w-full" />
      <Skeleton className="h-14 w-full" />
    </div>
  );
}

const emptyRule: AlertRuleCreate = {
  name: "",
  severity: "ERROR",
  threshold: 1,
  time_window_seconds: 60,
  match_pattern: "",
  notification_channels: [],
  is_active: true,
};

export function AlertsPage() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<AlertRule | null>(null);
  const [detailRule, setDetailRule] = useState<AlertRule | null>(null);
  const [formData, setFormData] = useState<AlertRuleCreate>(emptyRule);

  const { data: rules, isLoading: rulesLoading } = useQuery({
    queryKey: ["alert-rules"],
    queryFn: getAlertRules,
  });

  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: ["alert-history"],
    queryFn: getAlertHistory,
  });

  // Create map of rule_id -> rule for history display
  const ruleMap = useMemo(() => {
    const map = new Map<string, AlertRule>();
    rules?.forEach((rule) => map.set(rule.id, rule));
    return map;
  }, [rules]);

  // Filter rules
  const filteredRules = useMemo(() => {
    if (!rules) return [];
    return rules.filter((rule) => {
      const matchesSearch = rule.name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesStatus =
        statusFilter === "ALL" ||
        (statusFilter === "ACTIVE" && rule.is_active) ||
        (statusFilter === "INACTIVE" && !rule.is_active);
      return matchesSearch && matchesStatus;
    });
  }, [rules, searchQuery, statusFilter]);

  // History for detail view
  const ruleHistory = useMemo(() => {
    if (!detailRule || !history) return [];
    return history.filter((h) => h.rule_id === detailRule.id);
  }, [detailRule, history]);

  const createMutation = useMutation({
    mutationFn: createAlertRule,
    onSuccess: () => {
      toast.success("Alert rule created successfully");
      queryClient.invalidateQueries({ queryKey: ["alert-rules"] });
      closeDialog();
    },
    onError: () => {
      toast.error("Failed to create alert rule");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: AlertRuleUpdate }) => updateAlertRule(id, data),
    onSuccess: () => {
      toast.success("Alert rule updated");
      queryClient.invalidateQueries({ queryKey: ["alert-rules"] });
      closeDialog();
    },
    onError: () => {
      toast.error("Failed to update alert rule");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAlertRule,
    onSuccess: () => {
      toast.success("Alert rule deleted");
      queryClient.invalidateQueries({ queryKey: ["alert-rules"] });
      setDetailRule(null);
    },
    onError: () => {
      toast.error("Failed to delete alert rule");
    },
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      updateAlertRule(id, { is_active }),
    onSuccess: (_, variables) => {
      toast.success(variables.is_active ? "Alert rule enabled" : "Alert rule disabled");
      queryClient.invalidateQueries({ queryKey: ["alert-rules"] });
    },
    onError: () => {
      toast.error("Failed to update alert rule");
    },
  });

  const openCreateDialog = () => {
    setEditingRule(null);
    setFormData(emptyRule);
    setDialogOpen(true);
  };

  const openEditDialog = (rule: AlertRule) => {
    setEditingRule(rule);
    setFormData({
      name: rule.name,
      severity: rule.severity,
      threshold: rule.threshold,
      time_window_seconds: rule.time_window_seconds,
      match_pattern: rule.match_pattern || "",
      notification_channels: rule.notification_channels,
      is_active: rule.is_active,
    });
    setDialogOpen(true);
  };

  const closeDialog = () => {
    setDialogOpen(false);
    setEditingRule(null);
    setFormData(emptyRule);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingRule) {
      const updateData: AlertRuleUpdate = {};
      if (formData.name !== editingRule.name) updateData.name = formData.name;
      if (formData.severity !== editingRule.severity) updateData.severity = formData.severity;
      if (formData.threshold !== editingRule.threshold) updateData.threshold = formData.threshold;
      if (formData.time_window_seconds !== editingRule.time_window_seconds)
        updateData.time_window_seconds = formData.time_window_seconds;
      if (formData.match_pattern !== (editingRule.match_pattern || ""))
        updateData.match_pattern = formData.match_pattern || null;
      if (formData.is_active !== editingRule.is_active) updateData.is_active = formData.is_active;
      updateMutation.mutate({ id: editingRule.id, data: updateData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const hasActiveFilters = searchQuery !== "" || statusFilter !== "ALL";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Bell className="h-8 w-8 text-primary" />
            Alert Manager
          </h1>
          <p className="text-muted-foreground mt-1">
            Create, manage, and monitor alert rules
          </p>
        </div>
        <Button onClick={openCreateDialog}>
          <Plus className="mr-2 size-4" />
          New Rule
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          {rulesLoading ? (
            <div className="flex gap-4">
              <Skeleton className="h-9 w-[280px]" />
              <Skeleton className="h-9 w-[140px]" />
            </div>
          ) : (
            <div className="flex flex-wrap items-center gap-4">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search rules..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 w-[280px]"
                />
              </div>
              <Select value={statusFilter} onValueChange={(value) => value && setStatusFilter(value)}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ALL">All Status</SelectItem>
                  <SelectItem value="ACTIVE">Active</SelectItem>
                  <SelectItem value="INACTIVE">Inactive</SelectItem>
                </SelectContent>
              </Select>
              {hasActiveFilters && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSearchQuery("");
                    setStatusFilter("ALL");
                  }}
                  className="text-muted-foreground"
                >
                  <X className="h-4 w-4 mr-1" />
                  Clear
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Alert Rules Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="size-5" />
            Alert Rules
            {filteredRules.length > 0 && (
              <Badge variant="secondary" className="ml-2">
                {filteredRules.length}
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {rulesLoading ? (
            <RuleSkeleton />
          ) : filteredRules.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <FileText className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold">No alert rules found</h3>
              <p className="text-muted-foreground mt-1 max-w-md">
                {hasActiveFilters
                  ? "No rules match your current filters. Try adjusting or clearing them."
                  : "No alert rules configured yet. Create your first rule to get started."}
              </p>
              {hasActiveFilters && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSearchQuery("");
                    setStatusFilter("ALL");
                  }}
                  className="mt-4"
                >
                  <X className="h-4 w-4 mr-2" />
                  Clear Filters
                </Button>
              )}
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead className="w-[100px]">Severity</TableHead>
                    <TableHead className="w-[100px]">Threshold</TableHead>
                    <TableHead className="w-[120px]">Window</TableHead>
                    <TableHead className="w-[100px]">Status</TableHead>
                    <TableHead className="w-[140px] text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredRules.map((rule) => (
                    <TableRow
                      key={rule.id}
                      className="cursor-pointer hover:bg-muted/50 transition-colors"
                      onClick={() => setDetailRule(rule)}
                    >
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">
                          {rule.name}
                          <ChevronRight className="h-3 w-3 text-muted-foreground opacity-0 group-hover:opacity-100" />
                        </div>
                        {rule.match_pattern && (
                          <p className="text-xs text-muted-foreground mt-0.5">
                            Pattern: {rule.match_pattern}
                          </p>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge variant={getSeverityColor(rule.severity)}>{rule.severity}</Badge>
                      </TableCell>
                      <TableCell>{rule.threshold}</TableCell>
                      <TableCell>{rule.time_window_seconds}s</TableCell>
                      <TableCell>
                        <Badge variant={rule.is_active ? "default" : "outline"}>
                          {rule.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => {
                              e.stopPropagation();
                              openEditDialog(rule);
                            }}
                            title="Edit"
                          >
                            <Pencil className="size-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleMutation.mutate({
                                id: rule.id,
                                is_active: !rule.is_active,
                              });
                            }}
                            title={rule.is_active ? "Disable" : "Enable"}
                          >
                            <Power
                              className={`size-4 ${
                                rule.is_active ? "text-green-500" : "text-muted-foreground"
                              }`}
                            />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => {
                              e.stopPropagation();
                              if (
                                confirm(
                                  "Are you sure you want to delete this alert rule?"
                                )
                              ) {
                                deleteMutation.mutate(rule.id);
                              }
                            }}
                            title="Delete"
                          >
                            <Trash2 className="size-4 text-destructive" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Alert History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="size-5" />
            Recent Alert History
          </CardTitle>
        </CardHeader>
        <CardContent>
          {historyLoading ? (
            <HistorySkeleton />
          ) : !history || history.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Clock className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold">No alert history</h3>
              <p className="text-muted-foreground mt-1">
                Alerts will appear here when your rules are triggered.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {history.slice(0, 10).map((h) => {
                const rule = ruleMap.get(h.rule_id);
                return (
                  <div
                    key={h.id}
                    className="flex items-center justify-between rounded-lg border p-3 hover:bg-muted/30 transition-colors"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium">
                        {rule?.name || `Rule ${h.rule_id.slice(0, 8)}...`}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(h.triggered_at).toLocaleString()}
                        {h.resolved_at && (
                          <span className="ml-2 text-green-600">
                            Resolved: {new Date(h.resolved_at).toLocaleString()}
                          </span>
                        )}
                      </p>
                      {h.details && Object.keys(h.details).length > 0 && (
                        <p className="text-xs text-muted-foreground mt-1">
                          {JSON.stringify(h.details).slice(0, 100)}
                        </p>
                      )}
                    </div>
                    <Badge variant={getSeverityColor(h.severity)}>{h.severity}</Badge>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>
              {editingRule ? "Edit Alert Rule" : "Create Alert Rule"}
            </DialogTitle>
            <DialogDescription>
              {editingRule
                ? "Update the alert rule configuration."
                : "Configure a new alert rule for your logs."}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Rule Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, name: e.target.value }))
                }
                placeholder="e.g., High Error Rate"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Severity</Label>
                <Select
                  value={formData.severity}
                  onValueChange={(value) =>
                    setFormData((prev) => ({
                      ...prev,
                      severity: value as Severity,
                    }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {SEVERITIES.map((s) => (
                      <SelectItem key={s} value={s}>
                        {s}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="threshold">Threshold</Label>
                <Input
                  id="threshold"
                  type="number"
                  min={1}
                  value={formData.threshold}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      threshold: Number(e.target.value),
                    }))
                  }
                  required
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="timeWindow">Time Window (seconds)</Label>
              <Input
                id="timeWindow"
                type="number"
                min={1}
                value={formData.time_window_seconds}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    time_window_seconds: Number(e.target.value),
                  }))
                }
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="pattern">Match Pattern (regex)</Label>
              <Input
                id="pattern"
                value={formData.match_pattern || ""}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    match_pattern: e.target.value || null,
                  }))
                }
                placeholder="Optional regex pattern"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    is_active: e.target.checked,
                  }))
                }
                className="h-4 w-4 rounded border-gray-300"
              />
              <Label htmlFor="is_active" className="cursor-pointer">
                Rule is active
              </Label>
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={closeDialog}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={createMutation.isPending || updateMutation.isPending}
              >
                {createMutation.isPending || updateMutation.isPending
                  ? "Saving..."
                  : editingRule
                  ? "Update Rule"
                  : "Create Rule"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Rule Detail Dialog */}
      <Dialog open={!!detailRule} onOpenChange={() => setDetailRule(null)}>
        <DialogContent className="sm:max-w-lg max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Rule Details
            </DialogTitle>
          </DialogHeader>
          {detailRule && (
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <Badge variant={getSeverityColor(detailRule.severity)}>
                  {detailRule.severity}
                </Badge>
                <Badge variant={detailRule.is_active ? "default" : "outline"}>
                  {detailRule.is_active ? "Active" : "Inactive"}
                </Badge>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-muted-foreground">
                  Name
                </label>
                <div className="text-sm font-medium">{detailRule.name}</div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-medium text-muted-foreground">
                    Threshold
                  </label>
                  <div className="text-sm">{detailRule.threshold} occurrences</div>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium text-muted-foreground">
                    Time Window
                  </label>
                  <div className="text-sm">{detailRule.time_window_seconds}s</div>
                </div>
              </div>

              {detailRule.match_pattern && (
                <div className="space-y-1">
                  <label className="text-xs font-medium text-muted-foreground">
                    Match Pattern
                  </label>
                  <div className="font-mono text-sm bg-muted rounded px-2 py-1">
                    {detailRule.match_pattern}
                  </div>
                </div>
              )}

              <div className="space-y-1">
                <label className="text-xs font-medium text-muted-foreground">
                  Created
                </label>
                <div className="text-sm">
                  {new Date(detailRule.created_at).toLocaleString()}
                </div>
              </div>

              {/* History for this rule */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Trigger History</label>
                {ruleHistory.length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    No triggers yet for this rule.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {ruleHistory.map((h) => (
                      <div
                        key={h.id}
                        className="flex items-center justify-between rounded-lg border p-3"
                      >
                        <div>
                          <p className="text-xs text-muted-foreground">
                            {new Date(h.triggered_at).toLocaleString()}
                          </p>
                          {h.resolved_at && (
                            <p className="text-xs text-green-600">
                              Resolved: {new Date(h.resolved_at).toLocaleString()}
                            </p>
                          )}
                        </div>
                        <Badge variant={getSeverityColor(h.severity)}>
                          {h.severity}
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setDetailRule(null);
                    openEditDialog(detailRule);
                  }}
                >
                  <Pencil className="h-4 w-4 mr-1" />
                  Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    if (confirm("Delete this rule?")) {
                      deleteMutation.mutate(detailRule.id);
                    }
                  }}
                  className="text-destructive"
                >
                  <Trash2 className="h-4 w-4 mr-1" />
                  Delete
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
