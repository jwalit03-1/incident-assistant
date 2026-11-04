import { useEffect, useRef, useState } from "react";

const EXAMPLES = [
  "VPN keeps dropping after the Windows update",
  "Outlook stopped syncing new mail",
  "Printer shows offline for the whole floor",
];

export default function App() {
  const [key, setKey] = useState(() => sessionStorage.getItem("ak") || "");
  const [needKey, setNeedKey] = useState(false);
  const [keyInput, setKeyInput] = useState("");
  const [msgs, setMsgs] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const end = useRef(null);

  useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs, busy]);

  async function send(text) {
    const t = text.trim();
    if (!t || busy) return;
    setMsgs((m) => [...m, { role: "user", text: t }]);
    setInput("");
    setBusy(true);
    try {
      const r = await fetch("/api/chat", {
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
      setMsgs((m) => [...m, { role: "assistant", text: d.reply, sources: d.sources, redactions: d.redactions }]);
    } catch (e) {
      setMsgs((m) => [...m, { role: "error", text: e.message }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Resolution finder</h1>
        <p>Describe a problem. Answers come only from resolved incidents, with links to the source tickets.</p>
      </header>

      <main>
        {msgs.length === 0 && (
          <div className="empty">
            <p>Try one of these, or paste an error message.</p>
            {EXAMPLES.map((x) => (
              <button key={x} className="example" onClick={() => send(x)}>{x}</button>
            ))}
          </div>
        )}

        {msgs.map((m, i) => (
          <article key={i} className={`msg ${m.role}`}>
            <div className="text">{m.text}</div>
            {m.sources?.length > 0 && (
              <ul className="sources">
                {m.sources.map((s) => (
                  <li key={s.number}>
                    <a href={s.url} target="_blank" rel="noreferrer">{s.number}</a>
                    <span>{s.short_description}</span>
                  </li>
                ))}
              </ul>
            )}
            {m.redactions && Object.keys(m.redactions).length > 0 && (
              <div className="redacted">
                <span>Hidden from the model</span>
                {Object.entries(m.redactions).map(([k, n]) => (
                  <b key={k} className="bar">{k} ×{n}</b>
                ))}
              </div>
            )}
          </article>
        ))}

        {busy && <div className="msg assistant"><div className="text dim">Searching resolved incidents…</div></div>}
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

      <footer>
        <textarea
          rows={2}
          value={input}
          placeholder="What is going wrong?"
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input); } }}
        />
        <button onClick={() => send(input)} disabled={busy || !input.trim()}>Find resolutions</button>
      </footer>
    </div>
  );
}
