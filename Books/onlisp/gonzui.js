// -*- mode: c -*-
var spanCache;
var grepCache;
var isInternetExplorer;

function gonzuis () {
    try {
        spans =  document.getElementsByTagName('div');
        for (i = 0; i < spans.length; i++) {
            e = spans[i];
            if (e.name == "index") {
                    e.style.display = "inline";
            }}
    } catch (e) {
        // 正規表現の文法エラーを無視する
    }
}

function initCache () {
    if (navigator.appName.indexOf("Microsoft") >= 0) {
        isInternetExplorer = true;
    } else {
        isInternetExplorer = false;
    }

    spanCache = document.getElementsByTagName("span");
    grepCache = new Array();

    for (i = 0; i < spanCache.length; i++) {
        e = spanCache[i];
        name = e.className;

        if (e.className == "line") {
            line = null;
            if (isInternetExplorer) {
                line = e.innerText;
            } else {
                line = e.innerHTML.replace(/<[^>]+>/g, "");
            }
            pair = new Array();
            pair.push(e);
            pair.push(line);
            grepCache.push(pair);
        }
    }
}

function grep (string) {
if (!grepCache)
{
initCache();
}
    try {
        pattern = new RegExp(string, "i");
        for (i = 0; i < grepCache.length; i++) {
            e = grepCache[i][0];
            line = grepCache[i][1];
            if (line.match(pattern)) {
                e.style.display = "inline";
            } else {
                e.style.display = "none";
            }
        }
    } catch (e) {
        // Ignore errors of invalid regular expressions.
    }
}
