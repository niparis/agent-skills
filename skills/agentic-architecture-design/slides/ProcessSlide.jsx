/* ProcessSlide.jsx — numbered request-lifecycle step cards. */
function ProcessSlide({ num, total }) {
  return (
    <Slide num={num} total={total}>
      <SectionLabel>The Request Lifecycle</SectionLabel>
      <H1 style={{ marginTop: 12, marginBottom: 18 }}>One agent call, four governed hops</H1>

      <div className="card-grid" style={{ gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
        <ProcessCard n="01" title="Admission" badge="Decision">
          Gateway and policy engine check: certified, permitted, allowed model set,
          kill switch registered.
        </ProcessCard>
        <ProcessCard n="02" title="Dispatch to runtime" badge="Handoff">
          Once cleared, routed to its sidecar (default), or a central capability or
          exception agent.
        </ProcessCard>
        <ProcessCard n="03" title="Reason + model call" badge="Runtime · AI Platform">
          Runtime calls the model via the stateless AI platform, routed cloud or on-prem
          per jurisdiction.
        </ProcessCard>
        <ProcessCard n="04" title="Tool call" badge="MCP · Local">
          Payments tool invoked at the app boundary under the app's own credentials.
        </ProcessCard>
      </div>

      <div className="pill-row" style={{ marginTop: 24 }}>
        <PillFilled>Non-negotiable first</PillFilled>
        <PillFilled>Kill switch</PillFilled>
        <Pill>Govern centrally</Pill>
        <Pill>Execute where the data lives</Pill>
      </div>
    </Slide>
  );
}

Object.assign(window, { ProcessSlide });
