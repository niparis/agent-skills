/* StatementSlide.jsx — large two-tone statement on paper; thesis resolves green. */
function StatementSlide({ num, total }) {
  return (
    <Slide num={num} total={total}>
      <SectionLabel>The Principle</SectionLabel>
      <div style={statementSlideStyles.wrap}>
        <div className="t-statement" style={{ fontSize: 30, lineHeight: 1.4 }}>
          A central gateway governs every agent,<br />
          common capabilities are built once,<br />
          and execution stays beside the data it touches.
        </div>
        <div className="t-statement-green" style={{ fontSize: 30, lineHeight: 1.4, marginTop: 18 }}>
          Control is centralised; data and tools are not.
        </div>
      </div>
    </Slide>
  );
}

const statementSlideStyles = {
  wrap: { flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", maxWidth: 880 },
};

Object.assign(window, { StatementSlide });
