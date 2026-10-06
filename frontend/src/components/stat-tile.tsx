type StatTileProps = {
  label: string;
  value: string;
  delta?: {
    text: string;
    direction: "up" | "down";
    isGood: boolean;
  };
};

export function StatTile({ label, value, delta }: StatTileProps) {
  const deltaColor = delta
    ? delta.isGood
      ? "var(--status-good)"
      : "var(--status-critical)"
    : undefined;

  return (
    <div className="rounded-lg border border-[color:var(--border-hairline)] bg-[color:var(--surface-1)] p-5">
      <p className="text-sm text-[color:var(--text-secondary)]">{label}</p>
      <p className="mt-2 text-3xl font-semibold tracking-tight">{value}</p>
      {delta && (
        <p className="mt-2 text-sm" style={{ color: deltaColor }}>
          {delta.direction === "up" ? "↑" : "↓"} {delta.text}
        </p>
      )}
    </div>
  );
}
