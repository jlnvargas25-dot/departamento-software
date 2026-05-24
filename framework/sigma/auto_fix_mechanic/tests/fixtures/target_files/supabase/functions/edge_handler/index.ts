// Fixture: A21-OBS-1b-DENO-CONSOLE (Edge Function Deno)
// Path scope: supabase/functions/**/*.ts — el codemod aplica acá, no en archivos top-level

// En Edge Functions Deno NO hay pino/logger import; el codemod debe envolver
// console.log con JSON.stringify({ level, msg, ...ctx }) (S-6).

Deno.serve(async (req) => {
  const reqId = crypto.randomUUID();

  // A21-OBS-1b-DENO-CONSOLE violation: log plano
  console.log("incoming request", reqId, req.method);

  try {
    const body = await req.json();
    // A21-OBS-1b-DENO-CONSOLE violation
    console.log("body received", body);
    return new Response(JSON.stringify({ ok: true }), { status: 200 });
  } catch (err) {
    // A21-OBS-1b-DENO-CONSOLE violation
    console.error("handler crashed", err);
    return new Response(JSON.stringify({ ok: false }), { status: 500 });
  }
});
