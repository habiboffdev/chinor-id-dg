// Minimal HTML -> PNG exporter with CSS inlining and scaling
// Usage: exportNodeToPng(node, { filename, scale, cssUrls, beforeSerialize })

async function collectCssText(urls = []){
  try {
    const texts = await Promise.all(
      urls.map(u => fetch(u).then(r => r.ok ? r.text() : '').catch(()=>''))
    );
    return texts.join('\n\n');
  } catch { return ''; }
}

async function exportNodeToPng(node, opts={}){
  const { filename = 'opportuni-card.png', scale = 2, cssUrls = [], beforeSerialize } = opts;
  if (!node) return;
  const clone = node.cloneNode(true);
  if (typeof beforeSerialize === 'function') { try { beforeSerialize(clone); } catch {} }

  // Compute size (fallback if node is detached/hidden)
  const rect = node.getBoundingClientRect ? node.getBoundingClientRect() : { width: 0, height: 0 };
  let width = Math.max(1, Math.round(rect.width || node.offsetWidth || 0));
  let height = Math.max(1, Math.round(rect.height || node.offsetHeight || 0));
  if (width < 2 || height < 2) {
    const temp = document.createElement('div');
    temp.style.cssText = 'position:fixed;left:-10000px;top:-10000px;pointer-events:none;opacity:0;';
    const probe = clone.cloneNode(true);
    temp.appendChild(probe);
    document.body.appendChild(temp);
    const r2 = probe.getBoundingClientRect();
    width = Math.max(900, Math.round(r2.width || 900));
    height = Math.max(600, Math.round(r2.height || 600));
    document.body.removeChild(temp);
  }

  // Inline CSS and sanitize/inline images to avoid canvas taint
  const cssText = await collectCssText(cssUrls);
  await inlineImagesOnClone(clone);
  const xmlContent = new XMLSerializer().serializeToString(clone);
  const content = `<style>${cssText}</style><div class='theme-opportuni'>${xmlContent}</div>`;

  // Wrap in scaled container to increase resolution
  const svgWidth = Math.round(width * scale);
  const svgHeight = Math.round(height * scale);
  const wrapperStyle = `transform: scale(${scale}); transform-origin: top left; width:${width}px; height:${height}px;`;

  const svg = `<?xml version="1.0" encoding="UTF-8"?>\n`+
              `<svg xmlns='http://www.w3.org/2000/svg' width='${svgWidth}' height='${svgHeight}'>`+
              `<foreignObject width='100%' height='100%'>`+
              `<div xmlns='http://www.w3.org/1999/xhtml' style='${wrapperStyle}'>${content}</div>`+
              `</foreignObject></svg>`;

  const url = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
  const img = new Image(); img.crossOrigin='anonymous';
  await new Promise((resolve) => { img.onload = resolve; img.src = url; });

  const canvas = document.createElement('canvas');
  canvas.width = svgWidth; canvas.height = svgHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(img, 0, 0);

  // Prefer toBlob for reliability; fallback to dataURL
  const a = document.createElement('a');
  a.download = filename;
  if (canvas.toBlob) {
    await new Promise((resolve)=>{
      canvas.toBlob((blob)=>{
        try {
          const u = URL.createObjectURL(blob);
          a.href = u;
          document.body.appendChild(a);
          a.click();
          setTimeout(()=>{ URL.revokeObjectURL(u); a.remove(); resolve(); }, 0);
        } catch { resolve(); }
      }, 'image/png');
    });
  } else {
    try {
      a.href = canvas.toDataURL('image/png');
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch {}
  }
}

window.exportNodeToPng = exportNodeToPng;

// Helpers
const TRANSPARENT_PX = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAl8BfV0p7A8AAAAASUVORK5CYII=';

async function toDataUrl(url){
  try {
    const abs = new URL(url, window.location.href);
    // Try CORS first (works if server sets ACAO header)
    let resp = await fetch(abs.href, { mode: 'cors' }).catch(()=>null);
    if (!resp || !resp.ok) {
      // Fallback to same-origin mode when applicable
      if (abs.origin !== window.location.origin) return null;
      resp = await fetch(abs.href, { mode: 'same-origin' }).catch(()=>null);
      if (!resp || !resp.ok) return null;
    }
    const blob = await resp.blob();
    return await new Promise((res)=>{ const fr = new FileReader(); fr.onload = ()=>res(fr.result); fr.readAsDataURL(blob); });
  } catch { return null; }
}

async function inlineImagesOnClone(root){
  const imgs = Array.from(root.querySelectorAll('img'));
  for (const img of imgs){
    const src = img.getAttribute('src') || '';
    if (!src || src.startsWith('data:')) continue;
  const data = await toDataUrl(src);
    if (data) img.setAttribute('src', data);
    else img.setAttribute('src', TRANSPARENT_PX);
  }
}
