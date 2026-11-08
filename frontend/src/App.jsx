import { useEffect, useRef, useState } from "react";

const API_BASE = (import.meta.env.VITE_API_BASE || "").trim().replace(/\/+$/, "");

const P = {
  search: <><circle cx="11" cy="11" r="7" /><path d="M21 21l-4.3-4.3" /></>,
  incident: <><path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z" /><path d="M12 9v4M12 17h.01" /></>,
  doc: <><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" /><path d="M14 3v5h5M9 13h6M9 17h6" /></>,
  shield: <><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z" /><path d="M9 12l2 2 4-4" /></>,
  send: <><path d="M22 2L11 13" /><path d="M22 2l-7 20-4-9-9-4z" /></>,
  out: <path d="M7 17L17 7M8 7h9v9" />,
  check: <path d="M20 6L9 17l-5-5" />,
  info: <><circle cx="12" cy="12" r="9" /><path d="M12 8h.01M11 12h1v5h1" /></>,
  wifi: <path d="M5 12.5a10 10 0 0 1 14 0M8.5 16a5 5 0 0 1 7 0M12 20h.01M2 9a15 15 0 0 1 20 0" />,
  mail: <><rect x="3" y="5" width="18" height="14" rx="2" /><path d="M3 7l9 6 9-6" /></>,
  printer: <><path d="M6 9V3h12v6M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" /><rect x="6" y="14" width="12" height="7" /></>,
  card: <><rect x="2" y="5" width="20" height="14" rx="2" /><path d="M2 10h20" /></>,
};

function Icon({ n, size = 18 }) {
  return (
    <svg viewBox="0 0 24 24" width={size} height={size} fill="none" stroke="currentColor"
         strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{P[n]}</svg>
  );
}

const EXAMPLES = [
  { icon: "wifi", title: "VPN keeps dropping", text: "VPN keeps dropping after the Windows update" },
  { icon: "mail", title: "Mail not syncing", text: "Outlook stopped syncing new mail" },
  { icon: "printer", title: "Printer offline", text: "Printer shows offline for the whole floor" },
  { icon: "card", title: "Refund rejected", text: "Refund rejected with error RF-4021" },
];

const plural = (n, w) => `${n} ${w}${n === 1 ? "" : "s"}`;

function inline(text) {
  return text.split(/(\*\*[^*]+\*\*|`[^`]+`|INC\d{4,12})/g).map((p, i) => {
    if (p.startsWith("**") && p.endsWith("**") && p.length > 4) return <strong key={i}>{p.slice(2, -2)}</strong>;
    if (p.startsWith("`") && p.endsWith("`") && p.length > 2) return <code key={i}>{p.slice(1, -1)}</code>;
    if (/^INC\d{4,12}$/.test(p)) return <span key={i} className="inc">{p}</span>;
    return p;
  });
}

function RichText({ text }) {
  const blocks = [];
  let list = null;
  for (const raw of text.split("\n")) {
    const line = raw.trimEnd();
    const li = line.match(/^\s*(?:[-*\u2022]|\d+[.)])\s+(.*)$/);
    if (li) {
      if (!list) { list = []; blocks.push({ t: "ul", items: list }); }
      list.push(li[1]);
      continue;
    }
    list = null;
    if (!line.trim()) continue;
    const conf = line.match(/^\W*confidence\W*(high|medium|low)\b/i);
    const head = line.match(/^\W*(from past incidents|from documentation|based on)\W*$/i);
    if (conf) blocks.push({ t: "conf", level: conf[1].toLowerCase() });
    else if (head) blocks.push({ t: "h", text: head[1] });
    else blocks.push({ t: "p", text: line });
  }
  return (
    <div className="rich">
      {blocks.map((b, i) =>
        b.t === "ul" ? <ul key={i}>{b.items.map((x, j) => <li key={j}>{inline(x)}</li>)}</ul>
        : b.t === "conf" ? <span key={i} className={`conf ${b.level}`}>Confidence: {b.level}</span>
        : b.t === "h" ? <h4 key={i}>{b.text}</h4>
        : <p key={i}>{inline(b.text)}</p>)}
    </div>
  );
}

function Provenance({ m }) {
  const sources = m.sources || [];
  const inc = sources.filter((s) => s.kind === "incident").length;
  const docs = sources.filter((s) => s.kind === "doc").length;
  let state, icon, text;
  if (m.searched === false) {
    state = "none"; icon = "info";
    text = "This reply did not use your incidents or documentation.";
  } else if (!sources.length) {
    state = "warn"; icon = "incident";
    text = "No matching incidents or documents were found, so this reply is not based on your records. Treat it with caution.";
  } else {
    state = "ok"; icon = "check";
    const parts = [inc && plural(inc, "past incident"), docs && plural(docs, "document")].filter(Boolean);
    text = `Source of information: ${parts.join(" and ")} from your systems.`;
  }
  return <div className={`prov ${state}`}><Icon n={icon} size={16} /><span>{text}</span></div>;
}

function Sources({ sources }) {
  if (!sources?.length) return null;
  return (
    <ul className="srcs">
      {sources.map((s) => {
        const doc = s.kind === "doc";
        const body = (
          <>
            <span className={`sicon ${s.kind}`}><Icon n={doc ? "doc" : "incident"} size={16} /></span>
            <span className="stxt">
              <span className={doc ? "sref" : "sref mono"}>{s.ref}</span>
              {s.label && <span className="slab">{s.label}</span>}
            </span>
            <span className="skind">{doc ? "Doc" : "Incident"}</span>
            {s.url && <Icon n="out" size={14} />}
          </>
        );
        return (
          <li key={`${s.kind}-${s.ref}`}>
            {s.url
              ? <a className="src" href={s.url} target="_blank" rel="noreferrer">{body}</a>
              : <div className="src">{body}</div>}
          </li>
        );
      })}
    </ul>
  );
}

export default function App() {
  const [key, setKey] = useState(() => sessionStorage.getItem("ak") || "");
  const [needKey, setNeedKey] = useState(false);
  const [keyInput, setKeyInput] = useState("");
  const [msgs, setMsgs] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const end = useRef(null);
  const ta = useRef(null);

  useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth", block: "end" }); }, [msgs, busy]);
  useEffect(() => {
    const el = ta.current;
    if (el) { el.style.height = "auto"; el.style.height = Math.min(el.scrollHeight, 160) + "px"; }
  }, [input]);

  async function send(text) {
    const t = text.trim();
    if (!t || busy) return;
    setMsgs((m) => [...m, { role: "user", text: t }]);
    setInput("");
    setBusy(true);
    try {
      const r = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Access-Key": key },
        body: JSON.stringify({
          message: t,
          history: msgs.filter((m) => m.role === "user" || m.role === "assistant").map((m) => ({ role: m.role, content: m.text })),
        }),
      });
      if (r.status === 401) { setNeedKey(true); throw new Error("Enter the access key below, then send again."); }
      if (!r.ok) {
        const e = await r.json().catch(() => ({}));
        throw new Error(e.detail || `Request failed (${r.status})`);
      }
      const d = await r.json();
      setMsgs((m) => [...m, { role: "assistant", text: d.reply, sources: d.sources, redactions: d.redactions, searched: d.searched }]);
    } catch (e) {
      setMsgs((m) => [...m, { role: "error", text: e.message }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="shell">
      <header className="top">
        <div className="brand">
          <span className="mark"><Icon n="search" size={20} /></span>
          <div>
            <h1>Resolution finder</h1>
            <p>Past incidents and documentation, with sources</p>
          </div>
        </div>
        <span className="pill"><Icon n="shield" size={14} />PII filtered</span>
      </header>

      <main>
        {msgs.length === 0 && (
          <section className="hero">
            <h2>What is going wrong?</h2>
            <p>Describe the problem or paste an error message. Every answer shows which incidents and documents it came from.</p>
            <div className="examples">
              {EXAMPLES.map((x) => (
                <button key={x.title} className="example" onClick={() => send(x.text)}>
                  <span className="eicon"><Icon n={x.icon} size={18} /></span>
                  <span><strong>{x.title}</strong><small>{x.text}</small></span>
                </button>
              ))}
            </div>
          </section>
        )}

        {msgs.map((m, i) =>
          m.role === "user" ? (
            <div key={i} className="row user"><div className="bubble">{m.text}</div></div>
          ) : m.role === "error" ? (
            <div key={i} className="row bot">
              <div className="avatar err">!</div>
              <div className="card error">{m.text}</div>
            </div>
          ) : (
            <div key={i} className="row bot">
              <div className="avatar"><Icon n="search" size={16} /></div>
              <div className="card">
                <RichText text={m.text} />
                <Provenance m={m} />
                <Sources sources={m.sources} />
                {m.redactions && Object.keys(m.redactions).length > 0 && (
                  <div className="priv">
                    <Icon n="shield" size={14} />
                    <span>Hidden from the model</span>
                    {Object.entries(m.redactions).map(([k, n]) => <b key={k} className="bar">{k} ×{n}</b>)}
                  </div>
                )}
              </div>
            </div>
          )
        )}

        {busy && (
          <div className="row bot">
            <div className="avatar"><Icon n="search" size={16} /></div>
            <div className="card typing" aria-label="Searching"><i /><i /><i /><span>Searching incidents and documentation</span></div>
          </div>
        )}
        <div ref={end} />
      </main>

      {needKey && (
        <form className="keyform" onSubmit={(e) => {
          e.preventDefault();
          sessionStorage.setItem("ak", keyInput.trim());
          setKey(keyInput.trim()); setNeedKey(false); setKeyInput("");
        }}>
          <input type="password" value={keyInput} placeholder="Access key" onChange={(e) => setKeyInput(e.target.value)} />
          <button type="submit" disabled={!keyInput.trim()}>Save key</button>
        </form>
      )}

      <footer className="composer">
        <div className="box">
          <textarea
            ref={ta}
            rows={1}
            value={input}
            placeholder="Describe the problem…"
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input); } }}
          />
          <button className="send" onClick={() => send(input)} disabled={busy || !input.trim()} aria-label="Send">
            <Icon n="send" size={18} />
          </button>
        </div>
        <small>Enter to send, Shift+Enter for a new line</small>
      </footer>
    </div>
  );
}
