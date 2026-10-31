---
hide:
    - date
    - navigation
    - toc
home: true
nostatistics: true
icon: material/home
---

<!-- ezlinks: disable -->

<br><br><br><br><br><br>

<h1 style="text-align: center;">
<span style="font-size:50px;">
Welcome to Awesome Tech Share! 🎉
</span>
</h1>

<span style="display: block; text-align: center; font-size: 18px;">
[:octicons-link-16: Contributors](./links/index.md) / [:octicons-info-16: About Us](https://zhuanlan.zhihu.com/p/12775079036) / <button type="button" id="statistics-toggle" class="statistics-toggle" aria-expanded="false" aria-controls="statistics">:material-chart-line: Statistics</button>
</span>

<div id="statistics" markdown="1" class="card" style="width: min(27em, 100%); border-color: transparent; margin-left: auto; margin-right: auto; font-size: 110%" hidden>
<div style="padding-left: 1em;" markdown="1">
<li>Website Operating Time: <span id="web-time"></span></li>
</div>
</div>

<script>
function updateTime() {
    var date = new Date();
    var now = date.getTime();
    var startDate = new Date("2025/01/01 20:00:00");
    var start = startDate.getTime();
    var diff = now - start;
    var y, d, h, m;
    y = Math.floor(diff / (365 * 24 * 3600 * 1000));
    diff -= y * 365 * 24 * 3600 * 1000;
    d = Math.floor(diff / (24 * 3600 * 1000));
    h = Math.floor(diff / (3600 * 1000) % 24);
    m = Math.floor(diff / (60 * 1000) % 60);
    if (y == 0) {
        document.getElementById("web-time").innerHTML = d + "<span> </span>d<span> </span>" + h + "<span> </span>h<span> </span>" + m + "<span> </span>m";
    } else {
        document.getElementById("web-time").innerHTML = y + "<span> </span>y<span> </span>" + d + "<span> </span>d<span> </span>" + h + "<span> </span>h<span> </span>" + m + "<span> </span>m";
    }
    setTimeout(updateTime, 1000 * 60);
}
updateTime();
function toggle_statistics() {
    var statistics = document.getElementById("statistics");
    var toggle = document.getElementById("statistics-toggle");
    statistics.hidden = !statistics.hidden;
    toggle.setAttribute("aria-expanded", String(!statistics.hidden));
}
document.getElementById("statistics-toggle").addEventListener("click", toggle_statistics);
</script>
