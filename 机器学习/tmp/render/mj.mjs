/**
 * mj.mjs — offline MathJax v3 (tex -> SVG) helper.
 */
import { mathjax } from 'mathjax-full/js/mathjax.js';
import { TeX } from 'mathjax-full/js/input/tex.js';
import { SVG } from 'mathjax-full/js/output/svg.js';
import { liteAdaptor } from 'mathjax-full/js/adaptors/liteAdaptor.js';
import { RegisterHTMLHandler } from 'mathjax-full/js/handlers/html.js';
import { AllPackages } from 'mathjax-full/js/input/tex/AllPackages.js';

export async function initMathJax() {
  const adaptor = liteAdaptor();
  RegisterHTMLHandler(adaptor);
  const tex = new TeX({
    packages: AllPackages,
    inlineMath: [['$', '$']],
    displayMath: [['$$', '$$']],
  });
  const svg = new SVG({ fontCache: 'local' });
  const doc = mathjax.document('', { InputJax: tex, OutputJax: svg });

  return {
    /** @param {{tex:string,display:boolean}[]} items */
    async typesetAll(items) {
      const out = [];
      for (const it of items) {
        try {
          const node = doc.convert(it.tex, { display: it.display, em: 16, ex: 8, containerWidth: 80 * 16 });
          out.push(adaptor.innerHTML(node));
        } catch (e) {
          console.error('[mathjax] failed:', String(e).slice(0, 200), '\n  tex:', it.tex.slice(0, 120));
          out.push(null);
        }
      }
      return out;
    },
  };
}
