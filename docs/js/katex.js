document$.subscribe(({ body }) => { 
    renderMathInElement(body, {
      delimiters: [
        { left: "$$",  right: "$$",  display: true },   // Display mode equations
        { left: "$",   right: "$",   display: false },  // Inline equations
        { left: "\\(", right: "\\)", display: false },  // Alternative inline
        { left: "\\[", right: "\\]", display: true }    // Alternative display
      ],
    })
  })