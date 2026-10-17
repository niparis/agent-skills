/* ArchitectureSlide.jsx — the layered architecture stack with role badges. */
function ArchitectureSlide({ num, total }) {
  return (
    <Slide num={num} total={total}>
      <SectionLabel>The Platform · Layered View</SectionLabel>
      <H1 style={{ marginTop: 12, marginBottom: 18 }}>Five layers, two centres of gravity</H1>

      <div className="stack" style={{ gap: 8 }}>
        <ArchRow
          label="Govern" layer="Agent Gateway"
          tags={[{ label: "Policy engine (on top)", bold: true }, "Registry", "Eval / cert gate", "Kill switch", "Observability aggregation"]}
          badge={<ArchBadgeCenter>Central · Decision Point</ArchBadgeCenter>}
        />
        <ArchRow
          label="Reuse" layer="Agentic Capabilities"
          tags={[{ label: "Intelligent Document Processing", bold: true }, "Routers", "Summarisers", "Classification flows", "built once · reused"]}
          badge={<ArchBadgeCenter>Central · Shared</ArchBadgeCenter>}
        />
        <ArchRow
          label="Author" layer="Paved Road SDK"
          tags={[{ label: "Skills", bold: true }, "Pydantic AI ✦", "Google ADK / MS Agent Framework", "LangGraph", "MCP · tools", "A2A · agents"]}
        />
        <ArchRow
          label="Execute" layer="Execution Plane"
          tags={[{ label: "Sidecar runtime · default", bold: true }, "Central runtime · exception", "State + memory · Postgres + pgvector", "Tool calls @ boundary · MCP"]}
          badge={<ArchBadgeFed>Federated · Enforcement Point</ArchBadgeFed>}
        />
        <ArchRow
          label="Endure" layer="Temporal"
          tags={[{ label: "Durable execution", bold: true }, "Retries & recovery", "Long-running + resumable workflows", "Survives failures & restarts"]}
          badge={<BadgeLabel>Core Primitive</BadgeLabel>}
        />
      </div>

      <div className="legend" style={{ marginTop: 20 }}>
        <div className="legend-item"><div className="dot dot-navy"></div>Central, gateway decides</div>
        <div className="legend-item"><div className="dot dot-green"></div>Federated, edge executes</div>
      </div>
    </Slide>
  );
}

Object.assign(window, { ArchitectureSlide });
