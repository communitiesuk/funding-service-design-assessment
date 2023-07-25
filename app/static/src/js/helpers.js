AssessFrontend.removeAttributeValue = function(el, attr, value) {
  let re, m;
  if (el.getAttribute(attr)) {
    if (el.getAttribute(attr) == value) {
      el.removeAttribute(attr);
    } else {
      re = new RegExp('(^|\\s)' + value + '(\\s|$)');
      m = el.getAttribute(attr).match(re);
      if (m && m.length == 3) {
        el.setAttribute(attr, el.getAttribute(attr).replace(re, (m[1] && m[2])?' ':''))
      }
    }
  }
}

AssessFrontend.addAttributeValue = function(el, attr, value) {
  let re;
  if (!el.getAttribute(attr)) {
    el.setAttribute(attr, value);
  }
  else {
    re = new RegExp('(^|\\s)' + value + '(\\s|$)');
    if (!re.test(el.getAttribute(attr))) {
      el.setAttribute(attr, el.getAttribute(attr) + ' ' + value);
    }
  }
};

AssessFrontend.nodeListForEach = function (nodes, callback) {
    if (window.NodeList.prototype.forEach) {
        return nodes.forEach(callback)
    }
    for (let i = 0; i < nodes.length; i++) {
        callback.call(window, nodes[i], i, nodes)
    }
};

document.getElementById("show-tags").addEventListener("change", () => {
    const allTagDetails = Array.from(document.getElementsByClassName("dlhuc-tag-expand"));
    allTagDetails.forEach(tagDetail => {
        tagDetail.open = !tagDetail.open;
    })
})
