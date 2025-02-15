window.MathJax = {
    tex: {
      inlineMath: [["\\(", "\\)"]],           // Inline math delimiters
      displayMath: [["\\[", "\\]"]],          // Display math delimiters
      processEscapes: true,                    // Handle escaped characters
      processEnvironments: true                // Process LaTeX environments
    },
    options: {
      ignoreHtmlClass: ".*|",                 // Ignore all classes by default
      processHtmlClass: "arithmatex"          // Only process elements with this class
    }
  };
  
  document$.subscribe(() => { 
    MathJax.typesetPromise()                  // Render math when document loads
  })