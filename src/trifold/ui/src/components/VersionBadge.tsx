export function VersionBadge({ version }: { version: string }) {
  return (
    <div className="absolute bottom-1 left-1 z-20 font-mono text-xs">
      <span className="text-accent-foreground/50">v{version}</span>
    </div>
  );
}
