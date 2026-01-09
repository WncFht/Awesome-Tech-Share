---
hide:
    - date
    - navigation
    - toc
home: true
nostatistics: true
comments: false
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
[:octicons-link-16: Contributors](./links/index.md) / [:octicons-info-16: About Us](https://zhuanlan.zhihu.com/p/12775079036) / [:material-chart-line: Statistics] / [:material-network: 知识图谱](./javascripts/graph.html)(javascript:toggle_statistics();)
</span>

<div id="statistics" markdown="1" class="card" style="width: 27em; border-color: transparent; opacity: 0; margin-left: auto; margin-right: 0; font-size: 110%">
<div style="padding-left: 1em;" markdown="1">
<li>Website Operating Time: <span id="web-time"></span></li>
<li>Total Visitors: <span id="busuanzi_value_site_uv"></span> people</li>
<li>Total Visits: <span id="busuanzi_value_site_pv"></span> times</li>
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
    if (statistics.style.opacity == 0) {
        statistics.style.opacity = 1;
    } else {
        statistics.style.opacity = 0;
    }
}
</script>
