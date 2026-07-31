import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Bell, Plus, Trash2, Power, History } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
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
import { getAlertRules, getAlertHistory, createAlertRule, deleteAlertRule, updateAlertRule } from "@/services/alerts";
import type { AlertRuleCreate, Severity } from "@/types/alert";

const SEVERITIES: Severity[] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"];

export function AlertsPage() {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newRule, setNewRule] = useState<AlertRuleCreate>({
    name: "",
    severity: "ERROR",
    threshold: 1,
    time_window_seconds: 60,
    match_pattern: "",
    notification_channels: [],
    is_active: true,
  });

  const { data: rules, isLoading: rulesLoading } = useQuery({
    queryKey: ["alert-rules"],
    queryFn: getAlertRules,
  });

  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: ["alert-history"],
    queryFn: getAlertHistory,
  });

  const createMutation = useMutation({
    mutationFn: createAlertRule,
    onSuccess: () => {
      toast.success("Alert rule created successfully");
      queryClient.invalidateQueries({ queryKey: ["alert-rules"] });
      setDialogOpen(false);
      setNewRule({
        name: "",
        severity: "ERROR",
        threshold: 1,
        time_window_seconds: 60,
        match_pattern: "",
        notification_channels: [],
        is_active: true,
      });
    },
    onError: () => {
      toast.error("Failed to create alert rule");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAlertRule,
    onSuccess: () => {
      toast.success("Alert rule deleted");
      queryClient.invalidateQueries({ queryKey: ["alert-rules"] });
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

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(newRule);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Alert Manager</h1>
          <p className="mt-2 text-muted-foreground">Manage alert rules and view history</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger render={<Button />}>
            <Plus className="mr-2 size-4" />
            New Rule
          </DialogTrigger>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Create Alert Rule</DialogTitle>
              <DialogDescription>Configure a new alert rule for your logs.</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Rule Name</Label>
                <Input
                  id="name"
                  value={newRule.name}
                  onChange={(e) => setNewRule((prev) => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., High Error Rate"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Severity</Label>
                  <Select
                    value={newRule.severity}
                    onValueChange={(value) => setNewRule((prev) => ({ ...prev, severity: value as Severity }))}
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
                    value={newRule.threshold}
                    onChange={(e) => setNewRule((prev) => ({ ...prev, threshold: Number(e.target.value) }))}
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
                  value={newRule.time_window_seconds}
                  onChange={(e) => setNewRule((prev) => ({ ...prev, time_window_seconds: Number(e.target.value) }))}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="pattern">Match Pattern (regex)</Label>
                <Input
                  id="pattern"
                  value={newRule.match_pattern || ""}
                  onChange={(e) => setNewRule((prev) => ({ ...prev, match_pattern: e.target.value || null }))}
                  placeholder="Optional regex pattern"
                />
              </div>
              <DialogFooter>
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? "Creating..." : "Create Rule"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="size-5" />
            Alert Rules
          </CardTitle>
        </CardHeader>
        <CardContent>
          {rulesLoading ? (
            <p className="text-sm text-muted-foreground">Loading rules...</p>
          ) : rules && rules.length > 0 ? (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Severity</TableHead>
                    <TableHead>Threshold</TableHead>
                    <TableHead>Window</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-[100px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rules.map((rule) => (
                    <TableRow key={rule.id}>
                      <TableCell className="font-medium">{rule.name}</TableCell>
                      <TableCell>
                        <Badge variant={rule.severity === "CRITICAL" || rule.severity === "ERROR" ? "destructive" : "secondary"}>
                          {rule.severity}
                        </Badge>
                      </TableCell>
                      <TableCell>{rule.threshold}</TableCell>
                      <TableCell>{rule.time_window_seconds}s</TableCell>
                      <TableCell>
                        <Badge variant={rule.is_active ? "default" : "outline"}>
                          {rule.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => toggleMutation.mutate({ id: rule.id, is_active: !rule.is_active })}
                            title={rule.is_active ? "Disable" : "Enable"}
                          >
                            <Power className="size-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => {
                              if (confirm("Are you sure you want to delete this alert rule?")) {
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
          ) : (
            <p className="text-sm text-muted-foreground">No alert rules configured.</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="size-5" />
            Alert History
          </CardTitle>
        </CardHeader>
        <CardContent>
          {historyLoading ? (
            <p className="text-sm text-muted-foreground">Loading history...</p>
          ) : history && history.length > 0 ? (
            <div className="space-y-2">
              {history.slice(0, 10).map((h) => (
                <div key={h.id} className="flex items-center justify-between rounded-lg border p-3">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium">Rule ID: {h.rule_id}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(h.triggered_at).toLocaleString()}
                    </p>
                  </div>
                  <Badge variant={h.severity === "CRITICAL" || h.severity === "ERROR" ? "destructive" : "secondary"}>
                    {h.severity}
                  </Badge>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No alert history yet.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
