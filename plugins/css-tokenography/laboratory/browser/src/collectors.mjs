/** Execute all collectors in one browser round trip so their observations are coherent. */
export async function collect(page, requestedCollectors) {
  return page.evaluate((requested) => {
    const rect = (element) => {
      const box = element.getBoundingClientRect();
      return {
        x: Number(box.x.toFixed(3)),
        y: Number(box.y.toFixed(3)),
        width: Number(box.width.toFixed(3)),
        height: Number(box.height.toFixed(3)),
      };
    };
    const target = document.querySelector("[data-lab-target]");
    if (!target) throw new Error("fixture is missing [data-lab-target]");
    const computed = getComputedStyle(target);
    const result = {};

    if (requested.includes("computed-style")) {
      result.computed = {
        display: computed.display,
        backgroundColor: computed.backgroundColor,
        backgroundImage: computed.backgroundImage,
        filter: computed.filter,
        backdropFilter: computed.backdropFilter,
        transform: computed.transform,
        gridTemplateColumns: computed.gridTemplateColumns,
      };
    }
    if (requested.includes("bounding-box")) {
      result.layout = { target: rect(target), named: {} };
      for (const element of document.querySelectorAll("[data-lab-name]")) {
        result.layout.named[element.dataset.labName] = rect(element);
      }
    }
    if (requested.includes("hit-test")) {
      const point = target.dataset.labHitPoint?.split(",").map(Number);
      if (!point || point.length !== 2 || point.some(Number.isNaN)) {
        throw new Error("hit-test fixture requires data-lab-hit-point=x,y");
      }
      result.hitTest = { targetId: document.elementFromPoint(point[0], point[1])?.id ?? null };
    }
    if (requested.includes("selector-matches")) {
      result.selectors = {
        matching: Array.from(document.querySelectorAll("[data-lab-selector-candidate]:nth-child(odd of [data-lab-selector-candidate])"), (element) => element.id),
        targetMatches: target.matches("[data-lab-target]:has(> [data-lab-selector-candidate])"),
      };
    }
    if (requested.includes("feature-support")) {
      result.features = {
        cssInterface: typeof window.CSS === "object",
        matchMedia: typeof window.matchMedia === "function",
        cssGrid: CSS.supports("display", "grid"),
        flexbox: CSS.supports("display", "flex"),
        subgrid: CSS.supports("grid-template-columns", "subgrid"),
        backdropFilter: CSS.supports("backdrop-filter", "blur(1px)"),
        filter: CSS.supports("filter", "blur(1px)"),
        selectorIs: CSS.supports("selector(:is(.one, .two))"),
      };
    }
    if (requested.includes("accessibility")) {
      result.accessibility = {
        role: target.getAttribute("role") ?? target.tagName.toLowerCase(),
        hidden: target.getAttribute("aria-hidden") === "true",
      };
    }
    if (requested.includes("containing-block")) {
      const child = target.querySelector("[data-lab-containing-child]");
      result.containingBlock = {
        position: computed.position,
        childOffsetParent: child?.offsetParent?.id ?? child?.offsetParent?.tagName.toLowerCase() ?? null,
      };
    }
    if (requested.includes("grid-placement")) {
      result.gridPlacement = Array.from(target.children, (element) => {
        const style = getComputedStyle(element);
        return { id: element.id || null, columnStart: style.gridColumnStart, rowStart: style.gridRowStart };
      });
    }
    if (requested.includes("flex-lines")) {
      result.flexLines = Array.from(target.children, (element) => rect(element).y);
    }
    return result;
  }, requestedCollectors);
}
