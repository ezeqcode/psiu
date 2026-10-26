# PSIU — launch video plan

**What it is:** a web page to pass passwords and API keys through any chat without exposing them —
encrypted in the browser, only the person who asked can open it.
**For:** devs, ops, anyone who has ever pasted a password into WhatsApp/Slack.
**What sets it apart:** no server, no signup. The request is a link; the answer is a link. Nothing
leaves the browser (enforced by CSP `connect-src 'none'`).
**Most impressive claim (true):** "Nada sai do seu navegador."
**Visual hook:** a chat where a live API key sits in plain text — then it scrambles away.
**Real UI shown:** Pedir → "Link copiado"; Enviar → lock snaps shut → "Link de resposta copiado";
Abrir → "Segredo aberto" with the eye toggle. Graffiti PSIU tag and the cutout-sticker illustrations.
**Tone:** `polished` with a punch — serious about security, confident, clean. Dark theme.
**Share caption:** "Ainda manda senha pelo WhatsApp? Fiz o PSIU: …"

Format: vertical 1080×1920 (Reels / Stories), 30 fps, 22 s. Content kept inside the safe zone (top ~220 px and bottom ~380 px are covered by the platform UI). Language: Portuguese (Brazil).

## Stand-ins
The secret shown (`sk_live_51HxQe8vT2…`) and the contact name ("Ana") are fictional. The reply link
in the chat is a real-looking but throwaway `#rcad1.…` string. No real keys, names or emails.

## Music
120 BPM (beat = 0.5 s, bar = 2 s), A minor: Am – F – C – G per bar. Pad alone during the hook,
drums + bass drop in on the reveal (3.0 s), hats/clap + pluck from 6.5 s, drums out at 20 s, last
chord rings out. Every cut and every UI event (pop, click, snap, reveal) lands on a 0.5 s grid.

## Storyboard (durations sum to 22 s)

| # | Time | Scene | On screen | Sound |
|---|---|---|---|---|
| 1 | 0.0–3.0 | **Hook** | "Senha no chat fica lá pra sempre." Chat: Ana asks "Me passa a chave do Stripe?" (0.5), you answer with the key in plain text (1.5), it gets a "lida" stamp (2.0). | Pad, two message blips on 0.5 / 1.5, riser into 3.0 |
| 2 | 3.0–6.5 | **Reveal** | The key scrambles into dots, the PSIU tag slams in (3.5), "Privado · Seguro · Inviolável · Único" (4.0), "Troque senhas e chaves de API sem expor nada no chat." (4.5) | Impact on 3.0, kick+bass start, tag pop on 3.5 |
| 3 | 6.5–10.5 | **1 · Você pede** | Real Pedir screen; cursor clicks "Criar link de pedido" (8.0); result "Link copiado" + link box (8.5) | Hats/clap enter, click on 8.0, chime on 8.5 |
| 4 | 10.5–14.5 | **2 · A pessoa tranca** | Real Enviar screen; secret typed as •••• (11.0–12.0); click "Trancar e copiar link" (12.5); lock snaps shut; "Link de resposta copiado" (13.0) | Type ticks on 16ths, snap on 12.5 |
| 5 | 14.5–18.0 | **3 · Só você abre** | Chat bubble with the scrambled reply link (15.0); real "Segredo aberto", eye toggles, the key appears (16.5–17.0) | Pop on 15.0, sparkle on 17.0 |
| 6 | 18.0–22.0 | **Punchline** | "Nada sai do seu navegador." (18.0) · big PSIU tag (19.0) + psiu.ezequielmagmorais.workers.dev + "Código aberto · grátis · sem cadastro" (19.5–20.0) — long hold | Drums out on 20.0, final chord rings |

The PSIU tag sits at the top of every walkthrough step (scenes 3–5) so the brand never leaves the screen.

Transitions: old scene out (0.2 s, slight lift) then new scene in (0.35 s) — never a muddy
crossfade between two busy layouts.
