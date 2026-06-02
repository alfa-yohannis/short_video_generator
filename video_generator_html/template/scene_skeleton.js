// Skeleton reference scene. Copy this structure when generating scenes from a
// storyboard. A scene is an ES module whose default export is an ASYNC
// build(ctx) (async because Mermaid diagrams render asynchronously):
//
//   ctx = {
//     stage,        // the #stage DOM element to append content to
//     c,            // component kit: c.content, c.titleBar, c.titleText,
//                   //   c.bodyText, c.sectionLabel, c.bulletList, c.codeCard,
//                   //   c.diagram (ASYNC — Mermaid), c.el
//     L,            // L("teks Indonesia", "english text") — picks per language
//     anime,        // anime.js (rarely needed directly; use tl)
//     tl,           // a paused anime.js timeline — add tweens to it (ms units)
//     duration,     // target seconds (the narration length)
//     isPortrait,   // boolean
//   }
//
// Rules:
//   1. Build DOM with the kit; append a c.content() column to stage and the
//      title bar to stage. Let CSS flexbox handle layout/wrapping — no absolute
//      pixel positions for text.
//   2. For any diagram (UML class, flowchart, sequence), use `await c.diagram(
//      mermaidText)` — Mermaid renders clean SVG. For UML use a `classDiagram`.
//   3. Wrap every visible string with L("id", "en").
//   4. Animate ONLY by adding tweens to `tl` (anime.js syntax, times in ms):
//      tl.add({targets: el, opacity:[0,1], translateY:[30,0], duration:600}, offsetMs)
//      Animate opacity / translateX / translateY / scale. The harness seeks `tl`
//      per frame; after it ends the final frame holds (scene may be shorter than
//      `duration`).
//   5. Semantic colors via opts: c.bodyText(txt, {color: 'DANGER'|'OK'|...}).

export default async function build(ctx) {
  const {stage, c, L, tl} = ctx;

  stage.appendChild(c.titleBar(L('Judul', 'Title'), {eyebrow: 'TUTORIAL'}));

  const content = c.content();
  const heading = c.titleText(L('Teks utama.', 'Main text.'));
  const diagram = await c.diagram(`classDiagram
    class AppConfig {
      -instance: AppConfig
      -AppConfig()
      +getInstance() AppConfig
    }`);
  content.append(heading, diagram);
  stage.appendChild(content);

  tl.add({targets: heading, opacity: [0, 1], translateY: [-40, 0], duration: 600}, 0);
  tl.add({targets: diagram, opacity: [0, 1], translateY: [24, 0], duration: 700}, 350);
}
