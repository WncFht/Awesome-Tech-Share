(() => {

  const preferToggle = e => {
    if (localStorage.getItem("data-md-prefers-color-scheme") === "true") {
      document.querySelector("body").setAttribute("data-md-color-scheme", (e.matches) ? "slate" : "default")
    }
    var frame = document.querySelector(".giscus-frame")
    var theme = document.querySelector("body").getAttribute("data-md-color-scheme") === "slate" ? "https://gcore.jsdelivr.net/gh/TonyCrane/note/docs/css/giscus.css" : "light"
    frame.contentWindow.postMessage(
      { giscus: { setConfig: { theme } } },
      "https://giscus.app"
    )
  }

/**
 * Sets up the theme for the webpage based on user preferences and system settings.
 *
 * @param {HTMLElement} body - The body element of the webpage.
 *
 * The function performs the following steps:
 * 1. Checks if the browser supports the `prefers-color-scheme` media feature.
 * 2. Retrieves the user's preferred color scheme and preference settings from localStorage.
 * 3. Removes any old version of the color scheme settings from localStorage.
 * 4. Sets default values for the color scheme and preference settings if they are not found in localStorage.
 * 5. Adjusts the color scheme based on the user's preference and system settings.
 * 6. Updates the body element's attributes to reflect the current color scheme and preference settings.
 * 7. Adds an event listener to handle changes in the `prefers-color-scheme` media feature if supported.
 */
  const setupTheme = body => {
    const preferSupported = window.matchMedia("(prefers-color-scheme)").media !== "not all"
    let scheme = localStorage.getItem("data-md-color-scheme")
    let prefers = localStorage.getItem("data-md-prefers-color-scheme")
    let oldversion = localStorage.getItem("/.__palette")

    if (oldversion) {
      localStorage.removeItem("/.__palette")
    }

    if (!scheme) {
      scheme = "slate"
    }
    if (!prefers) {
      prefers = "false"
    }

    if (prefers === "true" && preferSupported) {
      scheme = (window.matchMedia("(prefers-color-scheme: dark)").matches) ? "slate" : "default"
    } else {
      prefers = "false"
    }

    body.setAttribute("data-md-prefers-color-scheme", prefers)
    body.setAttribute("data-md-color-scheme", scheme)

    if (preferSupported) {
      const matchListener = window.matchMedia("(prefers-color-scheme: dark)")
      matchListener.addListener(preferToggle)
    }
  }

  const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
      if (mutation.type === "childList") {
        if (mutation.addedNodes.length) {
          for (let i = 0; i < mutation.addedNodes.length; i++) {
            const el = mutation.addedNodes[i]

            if (el.nodeType === 1 && el.tagName.toLowerCase() === "body") {
              setupTheme(el)
              break
            }
          }
        }
      }
    })
  })

  observer.observe(document.querySelector("html"), {childList: true})
  setupTheme(document.querySelector("body"))
})()

window.toggleScheme = () => {
  const body = document.querySelector("body")
  const preferSupported = window.matchMedia("(prefers-color-scheme)").media !== "not all"
  let scheme = body.getAttribute("data-md-color-scheme")
  let prefer = body.getAttribute("data-md-prefers-color-scheme")

  if (preferSupported && scheme === "default" && prefer !== "true") {
    prefer = "true"
    scheme = (window.matchMedia("(prefers-color-scheme: dark)").matches) ? "slate" : "default"
  } else if (preferSupported && prefer === "true") {
    prefer = "false"
    scheme = "slate"
  } else if (scheme === "slate") {
    prefer = "false"
    scheme = "default"
  } else {
    prefer = "false"
    scheme = "slate"
  }
  localStorage.setItem("data-md-prefers-color-scheme", prefer)
  localStorage.setItem("data-md-color-scheme", scheme)
  body.setAttribute("data-md-prefers-color-scheme", prefer)
  body.setAttribute("data-md-color-scheme", scheme)

  var frame = document.querySelector(".giscus-frame")
  var theme = scheme === "slate" ? "https://gcore.jsdelivr.net/gh/TonyCrane/note/docs/css/giscus.css" : "light"
  frame.contentWindow.postMessage(
    { giscus: { setConfig: { theme } } },
    "https://giscus.app"
  )
}
