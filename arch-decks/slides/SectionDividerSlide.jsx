/* SectionDividerSlide.jsx — full-bleed navy field divider with green takeaway. */
function SectionDividerSlide({ num, total }) {
  return (
    <Slide num={num} total={total} pad="0" style={{ background: "var(--navy-dark)" }}>
      <div style={sectionDividerStyles.wrap}>
        <div style={sectionDividerStyles.label}>
          <span style={sectionDividerStyles.dash}></span> The Governance Model
        </div>
        <div style={sectionDividerStyles.h}>
          A central gateway governs every agent;<br />
          execution stays beside the data it touches.
        </div>
        <div style={sectionDividerStyles.green}>
          Control is centralised; data and tools are not.
        </div>
      </div>
    </Slide>
  );
}

const sectionDividerStyles = {
  wrap: {
    flex: 1, display: "flex", flexDirection: "column", justifyContent: "center",
    padding: "0 64px",
  },
  label: {
    fontSize: 12, fontWeight: 500, letterSpacing: "0.12em", textTransform: "uppercase",
    color: "rgba(255,255,255,0.55)", display: "flex", alignItems: "center", gap: 10, marginBottom: 26,
  },
  dash: { display: "inline-block", width: 22, height: 1.5, background: "var(--g-light)" },
  h: { fontSize: 34, fontWeight: 600, letterSpacing: "-0.01em", lineHeight: 1.3, color: "#fff", maxWidth: 860 },
  green: { fontSize: 34, fontWeight: 600, letterSpacing: "-0.01em", lineHeight: 1.3, color: "var(--g-light)", marginTop: 14 },
};

Object.assign(window, { SectionDividerSlide });
