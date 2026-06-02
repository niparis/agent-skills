/* DecisionTableSlide.jsx — Decision / Why / Alternative Rejected. */
function DecisionTableSlide({ num, total }) {
  return (
    <Slide num={num} total={total}>
      <SectionLabel>The Decisions · And What We Rejected</SectionLabel>
      <H1 style={{ marginTop: 12, marginBottom: 18 }}>Every boundary is a decision we can defend</H1>

      <table className="ds-table" style={{ fontSize: 13 }}>
        <thead>
          <tr>
            <td style={{ width: "26%" }}>Decision</td>
            <td style={{ width: "44%" }}>Why</td>
            <td style={{ width: "30%" }}>Alternative Rejected</td>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Central agent gateway + policy engine</td>
            <td>An immutable core has to be <strong>enforced in-path</strong>, not just declared. Policy and the kill switch must refuse and halt agents.</td>
            <td className="col-rejected">Decentralised policy only. Unenforceable; kill switch becomes theatre.</td>
          </tr>
          <tr>
            <td>Shared agentic capabilities, central</td>
            <td><strong>Build once, reuse</strong>: IDP, routers, summarisers, classification flows. Consistency, speed and quality across applications.</td>
            <td className="col-rejected">Every app rebuilds. Duplication, drift, inconsistent risk posture.</td>
          </tr>
          <tr>
            <td>Tool execution federated at the app boundary</td>
            <td>Gateway <strong>decides</strong>, app <strong>executes</strong> under its own identity. Keeps credentials, residency & segmentation local.</td>
            <td className="col-rejected">Central tool-broker. Honeypot, breaks app identity, residency bleed.</td>
          </tr>
          <tr>
            <td>Sidecar default · central runtime by exception</td>
            <td>Some apps genuinely can't host a sidecar, so give them a <strong>governed central home</strong> rather than forcing workarounds.</td>
            <td className="col-rejected">Sidecar everywhere. Blocks adoption; pushes teams to shadow, ungoverned runtimes.</td>
          </tr>
        </tbody>
      </table>
    </Slide>
  );
}

Object.assign(window, { DecisionTableSlide });
