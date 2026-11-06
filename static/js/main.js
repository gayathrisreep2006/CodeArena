// Shared JavaScript.
// Let the Tab key insert 4 spaces inside code boxes (instead of leaving the box).
document.querySelectorAll("textarea.code-box").forEach(function (box) {
  box.addEventListener("keydown", function (e) {
    if (e.key === "Tab") {
      e.preventDefault();
      const start = box.selectionStart;
      box.value = box.value.substring(0, start) + "    " + box.value.substring(box.selectionEnd);
      box.selectionStart = box.selectionEnd = start + 4;
    }
  });
});
