/* ThreeColumnSlide.jsx — the canonical "architecture in one view" layout. */
function ThreeColumnSlide({ num, total }) {
  return (
    <Slide num={num} total={total}>
      <SectionLabel>The Architecture in One View</SectionLabel>
      <H1 style={{ marginTop: 12, marginBottom: 12 }}>Govern centrally, execute where the data lives</H1>
      <Lede style={{ marginBottom: 28 }}>
        A central gateway governs every agent, common capabilities are built once, and
        execution stays beside the data it touches.{" "}
        <span style={{ color: "var(--g-primary)", fontWeight: 600 }}>
          Control is centralised; data and tools are not.
        </span>
      </Lede>

      <div className="three-col" style={{ gap: 14 }}>
        <ColCard header="Central · Control & Capability" title="Governed once, built once">
          Agent gateway with the <strong>policy engine on top</strong>: admission, registry,
          eval gating, kill switch, observability. Plus <strong>shared capabilities</strong> built
          once and reused.
        </ColCard>
        <ColCard header="Federated · Execution" title="Run beside the data">
          Sidecar runtime, state, memory (<strong>Postgres + pgvector</strong>), durable execution
          and tool calls under each app's own identity — central home only by exception.
        </ColCard>
        <ColCard header="Deliberate Boundaries" title="Decide centrally, execute locally">
          The gateway <strong>decides</strong>; the app boundary <strong>enforces and runs</strong>.
          The AI platform is <strong>stateless</strong>. Vendors are implementations, never owners.
        </ColCard>
      </div>

      <div className="pill-row" style={{ marginTop: 22 }}>
        <Pill>Azure AI Foundry → candidate control-plane impl.</Pill>
        <Pill>Databricks / Bedrock → cloud AI platform</Pill>
      </div>
    </Slide>
  );
}

Object.assign(window, { ThreeColumnSlide });
