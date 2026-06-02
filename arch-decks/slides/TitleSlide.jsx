/* TitleSlide.jsx — deck cover. Hero lockup, two-tone, dual bar. */
function TitleSlide({ num, total }) {
  return (
    <Slide num={num} total={total} pad="0 64px">
      <div style={titleSlideStyles.wrap}>
        <div className="t-section-label" style={{ fontSize: 12, marginBottom: 28 }}>
          Standard Chartered · Platform Strategy
        </div>
        <div className="t-hero" style={{ fontSize: 76, lineHeight: 1.0 }}>Agentic</div>
        <div className="t-hero-green" style={{ fontSize: 76, lineHeight: 1.0 }}>Architecture</div>
        <div className="t-body" style={{ fontSize: 17, maxWidth: 560, marginTop: 26 }}>
          Govern centrally, execute where the data lives. One architecture for every
          agentic application across the bank.
        </div>
        <div className="pill-row" style={{ marginTop: 30 }}>
          <PillGhost>Control plane · Central</PillGhost>
          <PillGhost>Execution · Federated</PillGhost>
          <span className="t-mono" style={{ fontSize: 12, color: "var(--text-muted)", alignSelf: "center" }}>
            v1.0 · May 2026
          </span>
        </div>
      </div>
    </Slide>
  );
}

const titleSlideStyles = {
  wrap: { flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" },
};

Object.assign(window, { TitleSlide });
