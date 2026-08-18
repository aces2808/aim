// Simple SPA router using native View Transitions
(function() {
  // Feature detect View Transitions API
  const supportsViewTransitions = 'startViewTransition' in document;
  
  function navigate(url) {
    if (supportsViewTransitions) {
      document.startViewTransition(() => {
        fetch(url)
          .then(res => res.text())
          .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Update content
            document.body.replaceWith(doc.body);
            
            // Update head elements (title, meta)
            document.title = doc.title;
            
            // Update history
            history.pushState({}, '', url);
            
            // Re-attach router to new content
            attachRouter();
          });
      });
    } else {
      // Fallback to normal navigation
      window.location.href = url;
    }
  }
  
  function attachRouter() {
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a');
      if (!link) return;
      
      const url = new URL(link.href, window.location.origin);
      
      // Only intercept same-origin, non-hash links
      if (url.origin === window.location.origin && 
          !link.hasAttribute('download') &&
          !link.getAttribute('href')?.startsWith('#') &&
          !e.ctrlKey && !e.metaKey && !e.shiftKey) {
        e.preventDefault();
        navigate(url.href);
      }
    }, true); // Use capture to catch early
  }
  
  // Handle back/forward
  window.addEventListener('popstate', () => {
    navigate(window.location.href);
  });
  
  // Initialize
  attachRouter();
})();
