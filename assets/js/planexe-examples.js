// Examples page: keep the PlanExe version picker in sync with ?version=all|1|2,
// so a filtered view can be linked to. Filtering itself is done in CSS.
(function () {
  var radios = document.querySelectorAll('input[name="planexe-version"]');
  if (!radios.length) return;

  var params = new URLSearchParams(window.location.search);
  var initial = params.get("version");
  radios.forEach(function (radio) {
    if (radio.value === initial) radio.checked = true;
    radio.addEventListener("change", function () {
      var url = new URL(window.location.href);
      if (radio.value === "all") {
        url.searchParams.delete("version");
      } else {
        url.searchParams.set("version", radio.value);
      }
      history.replaceState(null, "", url);
    });
  });
})();
