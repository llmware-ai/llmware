/*
 * Includes utility methods for lazy loading media
 */

/**
 * Check if IntersectionObserver is supported
 * @return {boolean} true if window.IntersectionObserver is defined
 */
export function isIntersectionObserverSupported() {
  // Check that 'IntersectionObserver' property is defined on window
  return typeof window === "object" && window.IntersectionObserver;
}

/**
 * Check if native lazy loading is supported
 * @return {boolean} true if 'loading' property is defined for HTMLImageElement
 */
export function isNativeLazyLoadSupported() {
  return typeof HTMLImageElement === "object" && HTMLImageElement.prototype.loading;
}

/**
 * Calls onIntersect() when intersection is detected, or when
 * no native lazy loading or when IntersectionObserver isn't supported.
 * @param {Element} el - the element to observe
 * @param {function} onIntersect - called when the given element is in view
 */
export function detectIntersection(el, onIntersect) {
  try {
    if (isNativeLazyLoadSupported() || !isIntersectionObserverSupported()) {
      // Return if there's no need or possibility to detect intersection
      onIntersect();
      return;
    }

    // Detect intersection with given element using IntersectionObserver
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            onIntersect();
            observer.unobserve(entry.target);
          }
        });
      }, {threshold: [0, 0.01]});
    observer.observe(el);
  } catch (e) {
    onIntersect();
  }
}