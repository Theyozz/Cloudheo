import { ArrowDownRight, ArrowUpRight, Wallet, type LucideIcon } from "lucide-react";

type StatTileProps = {
  label: string;
  value: string;
  icon?: LucideIcon;
  delta?: {
    text: string;
    direction: "up" | "down";
    isGood: boolean;
  };
};

export function StatTile({ label, value, delta, icon: Icon = Wallet }: StatTileProps) {
  const DeltaIcon = delta?.direction === "up" ? ArrowUpRight : ArrowDownRight;

  return (
    <div
      className="panel flex h-full min-w-0 flex-col items-start"
      style={delta?.isGood ? { backgroundColor: "var(--accent-soft)" } : undefined}
    >
      <div className="flex w-full items-start justify-between gap-4">
        <p className="muted-label min-w-0 pt-2 leading-relaxed [overflow-wrap:anywhere]">{label}</p>
        <span className="icon-box shrink-0" aria-hidden="true">
          <Icon size={18} strokeWidth={1.7} />
        </span>
      </div>
      <p className="mt-5 text-4xl leading-tight font-semibold tracking-[-0.045em] tabular-nums text-[color:var(--foreground)] [overflow-wrap:anywhere]">
        {value}
      </p>
      {delta && (
        <p
          className={`${delta.isGood ? "good-badge" : "soft-badge"} mt-4 inline-flex max-w-full items-center gap-1.5`}
          style={delta.isGood ? undefined : { color: "var(--status-critical, #a34d43)" }}
        >
          <DeltaIcon size={14} className="shrink-0" aria-hidden="true" />
          <span className="min-w-0 whitespace-normal [overflow-wrap:anywhere]">{delta.text}</span>
        </p>
      )}
    </div>
  );
}
