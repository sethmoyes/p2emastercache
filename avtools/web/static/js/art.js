(function () {
    var el = document.getElementById('bg-art');
    if (!el) return;
    var art = ['goblin', 'dragon', 'dungeon', 'combat', 'monster'].map(function (n) {
        return '/static/art/wr_' + n + '.jpg';
    });
    var last = -1;
    function rotate() {
        var i;
        do { i = Math.floor(Math.random() * art.length); } while (i === last && art.length > 1);
        last = i;
        el.style.backgroundImage = "url('" + art[i] + "')";
    }
    rotate();
    setInterval(rotate, 30000);
})();
