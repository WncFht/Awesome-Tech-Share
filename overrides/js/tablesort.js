document$.subscribe(function() {
    /**
     * Selects all table elements within an article that do not have a class attribute.
     *
     * @type {NodeListOf<HTMLTableElement>}
     */
    var tables = document.querySelectorAll("article table:not([class])")
    tables.forEach(function(table) {
        new Tablesort(table)
    })
})
