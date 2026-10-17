/* ============================================================
   SlideKit.jsx — shared primitives for Agentic Architecture slides
   Renders design-system classes from colors_and_type.css + components.css.
   Exposes components on window for the other slide files.
   ============================================================ */

/* Slide shell — flex column, generous pad, signature footer (slide no. + dual bar).
   Do NOT set position/size on <section>; deck-stage positions & scales it. */
function Slide({ children, num, total, pad = "56px 64px 0", style }) {
  return (
    <section className="slide" style={{ ...slideKitStyles.slide, ...style }}>
      <div className="slide-body" style={{ ...slideKitStyles.body, padding: pad }}>
        {children}
      </div>
      <div className="slide-foot" style={slideKitStyles.foot}>
        {num != null && (
          <div style={slideKitStyles.pageNum}>
            {String(num).padStart(2, "0")}{total ? ` / ${String(total).padStart(2, "0")}` : ""}
          </div>
        )}
        <div className="dual-bar"><div className="dual-bar-navy"></div><div className="dual-bar-green"></div></div>
      </div>
    </section>
  );
}

function SectionLabel({ children }) {
  return <div className="t-section-label" style={{ fontSize: 12 }}>{children}</div>;
}

function H1({ children, style }) {
  return <div className="t-h1" style={{ fontSize: 32, ...style }}>{children}</div>;
}

function Lede({ children, style }) {
  return <div className="t-body" style={{ fontSize: 16, maxWidth: 720, ...style }}>{children}</div>;
}

/* Pills / badges */
const Pill = ({ children }) => <span className="pill" style={{ fontSize: 13 }}>{children}</span>;
const PillFilled = ({ children }) => <span className="pill-filled" style={{ fontSize: 11 }}>{children}</span>;
const PillGhost = ({ children }) => <span className="pill-ghost" style={{ fontSize: 11 }}>{children}</span>;
const BadgeLabel = ({ children }) => <span className="badge-label" style={{ fontSize: 10 }}>{children}</span>;
const ArchBadgeCenter = ({ children }) => <span className="arch-badge-center" style={{ fontSize: 10 }}>{children}</span>;
const ArchBadgeFed = ({ children }) => <span className="arch-badge-fed" style={{ fontSize: 10 }}>{children}</span>;

/* Three-column info card */
function ColCard({ header, title, children }) {
  return (
    <div className="col-card">
      <div className="col-card-header" style={{ fontSize: 11 }}>{header}</div>
      <div className="col-card-title" style={{ fontSize: 19 }}>{title}</div>
      <div className="col-card-body" style={{ fontSize: 13 }}>{children}</div>
    </div>
  );
}

/* Numbered process card */
function ProcessCard({ n, title, children, badge }) {
  return (
    <div className="process-card">
      <span className="process-card-num" style={{ fontSize: 11 }}>{n}</span>
      <div className="t-card-title" style={{ fontSize: 14 }}>{title}</div>
      <div className="t-body" style={{ fontSize: 12.5 }}>{children}</div>
      {badge && <div className="process-card-footer"><BadgeLabel>{badge}</BadgeLabel></div>}
    </div>
  );
}

/* Architecture layer row */
function ArchRow({ label, layer, tags = [], badge }) {
  return (
    <div className="arch-row">
      <div className="arch-label" style={{ fontSize: 10 }}>{label}</div>
      <div className="arch-layer" style={{ fontSize: 14 }}>{layer}</div>
      <div className="arch-tags">
        {tags.map((t, i) => (
          <span key={i} className={"arch-tag" + (t.bold ? " arch-tag-bold" : "")} style={{ fontSize: 11 }}>
            {t.label ?? t}
          </span>
        ))}
      </div>
      {badge}
    </div>
  );
}

const slideKitStyles = {
  slide: {
    background: "var(--bg)",
    color: "var(--text)",
    fontFamily: "var(--font)",
    display: "flex",
    flexDirection: "column",
    width: "100%",
    height: "100%",
  },
  body: { flex: 1, display: "flex", flexDirection: "column", minHeight: 0 },
  foot: { padding: "0 64px 22px", marginTop: "auto" },
  pageNum: {
    fontFamily: "var(--mono)", fontSize: 12, color: "var(--text-muted)",
    textAlign: "right", marginBottom: 8,
  },
};

Object.assign(window, {
  Slide, SectionLabel, H1, Lede,
  Pill, PillFilled, PillGhost, BadgeLabel, ArchBadgeCenter, ArchBadgeFed,
  ColCard, ProcessCard, ArchRow,
  slideKitStyles,
});
