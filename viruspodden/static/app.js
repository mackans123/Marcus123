/* Viruspodden – spelare, sök, meny och kontaktformulär */
(function () {
  "use strict";

  var store = {
    get: function (k) { try { return window.localStorage.getItem(k); } catch (_) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (_) { /* ignorera */ } }
  };

  /* ---------- Mobilmeny ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    nav.addEventListener("click", function (ev) {
      if (ev.target.closest("a")) { nav.classList.remove("is-open"); toggle.setAttribute("aria-expanded", "false"); }
    });
  }

  /* ---------- Spelare ---------- */
  var player = document.getElementById("player");
  var audio = player && player.querySelector("audio");
  if (player && audio) {
    var els = {
      img: player.querySelector(".player__img"),
      title: player.querySelector(".player__title"),
      cur: player.querySelector("[data-cur]"),
      dur: player.querySelector("[data-dur]"),
      seek: player.querySelector(".player__seek"),
      toggle: player.querySelector("[data-toggle]"),
      speed: player.querySelector("[data-speed]"),
      close: player.querySelector("[data-close]")
    };
    var SPEEDS = [1, 1.25, 1.5, 1.75, 2, 0.75];
    var current = null;
    var seeking = false;
    var lastSave = 0;

    var fmt = function (s) {
      if (!isFinite(s) || s < 0) return "–:–";
      s = Math.floor(s);
      var h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
      var mm = h ? String(m).padStart(2, "0") : String(m);
      return (h ? h + ":" : "") + mm + ":" + String(sec).padStart(2, "0");
    };

    var setPlayingUI = function () {
      var playing = !audio.paused && !audio.ended;
      document.querySelectorAll("[data-play]").forEach(function (b) {
        var isCur = current && b.getAttribute("data-id") === current.id;
        b.classList.toggle("is-playing", Boolean(isCur && playing));
        var label = b.querySelector("span");
        if (label && isCur) {
          if (!b.dataset.label) b.dataset.label = label.textContent;
          label.textContent = playing ? "Pausa" : b.dataset.label;
        } else if (label && b.dataset.label) {
          label.textContent = b.dataset.label;
        }
      });
      els.toggle.classList.toggle("is-playing", playing);
      els.toggle.setAttribute("aria-label", playing ? "Pausa" : "Spela");
    };

    var savePos = function (force) {
      if (!current || !isFinite(audio.currentTime)) return;
      var now = Date.now();
      if (!force && now - lastSave < 4000) return;
      lastSave = now;
      var nearEnd = audio.duration && audio.duration - audio.currentTime < 20;
      store.set("vp-pos-" + current.id, nearEnd ? "0" : String(Math.floor(audio.currentTime)));
    };

    var showPlayer = function () {
      player.hidden = false;
      document.documentElement.style.setProperty("--player-h", player.offsetHeight + "px");
    };

    var load = function (ep) {
      current = ep;
      audio.src = ep.src;
      audio.playbackRate = Number(store.get("vp-speed")) || 1;
      els.speed.textContent = String(audio.playbackRate).replace(".", ",") + "×";
      els.title.textContent = ep.title;
      els.title.href = ep.url;
      els.img.src = ep.image;
      els.cur.textContent = "0:00";
      els.dur.textContent = "–:–";
      els.seek.value = 0;
      var saved = Number(store.get("vp-pos-" + ep.id)) || 0;
      if (saved > 5) {
        audio.addEventListener("loadedmetadata", function once() {
          audio.removeEventListener("loadedmetadata", once);
          if (saved < audio.duration - 5) audio.currentTime = saved;
        });
      }
      if ("mediaSession" in navigator) {
        navigator.mediaSession.metadata = new window.MediaMetadata({
          title: ep.title, artist: "Viruspodden", album: "Viruspodden",
          artwork: [{ src: ep.image, sizes: "512x512" }]
        });
      }
      showPlayer();
    };

    var play = function () {
      var p = audio.play();
      if (p && p.catch) p.catch(function () { setPlayingUI(); });
    };

    document.addEventListener("click", function (ev) {
      var btn = ev.target.closest("[data-play]");
      if (!btn) return;
      var id = btn.getAttribute("data-id");
      if (current && current.id === id) {
        if (audio.paused) play(); else audio.pause();
        return;
      }
      savePos(true);
      load({
        id: id,
        src: btn.getAttribute("data-src"),
        title: btn.getAttribute("data-title"),
        url: btn.getAttribute("data-url"),
        image: btn.getAttribute("data-image")
      });
      play();
    });

    els.toggle.addEventListener("click", function () { if (audio.paused) play(); else audio.pause(); });
    player.querySelectorAll("[data-skip]").forEach(function (b) {
      b.addEventListener("click", function () {
        var t = audio.currentTime + Number(b.getAttribute("data-skip"));
        audio.currentTime = Math.max(0, Math.min(t, audio.duration || t));
      });
    });
    els.speed.addEventListener("click", function () {
      var i = SPEEDS.indexOf(audio.playbackRate);
      var next = SPEEDS[(i + 1) % SPEEDS.length];
      audio.playbackRate = next;
      store.set("vp-speed", String(next));
      els.speed.textContent = String(next).replace(".", ",") + "×";
    });
    els.close.addEventListener("click", function () {
      savePos(true);
      audio.pause();
      player.hidden = true;
      document.documentElement.style.setProperty("--player-h", "0px");
    });

    els.seek.addEventListener("input", function () { seeking = true; els.cur.textContent = fmt(Number(els.seek.value)); });
    els.seek.addEventListener("change", function () { audio.currentTime = Number(els.seek.value); seeking = false; });

    audio.addEventListener("loadedmetadata", function () {
      els.seek.max = Math.floor(audio.duration) || 0;
      els.dur.textContent = fmt(audio.duration);
    });
    audio.addEventListener("timeupdate", function () {
      if (!seeking) { els.seek.value = Math.floor(audio.currentTime); els.cur.textContent = fmt(audio.currentTime); }
      savePos(false);
    });
    ["play", "pause", "ended"].forEach(function (evt) { audio.addEventListener(evt, setPlayingUI); });
    audio.addEventListener("pause", function () { savePos(true); });
    audio.addEventListener("ended", function () { if (current) store.set("vp-pos-" + current.id, "0"); });
    window.addEventListener("pagehide", function () { savePos(true); });
    window.addEventListener("resize", function () { if (!player.hidden) showPlayer(); });

    if ("mediaSession" in navigator) {
      try {
        navigator.mediaSession.setActionHandler("play", play);
        navigator.mediaSession.setActionHandler("pause", function () { audio.pause(); });
        navigator.mediaSession.setActionHandler("seekbackward", function () { audio.currentTime = Math.max(0, audio.currentTime - 15); });
        navigator.mediaSession.setActionHandler("seekforward", function () { audio.currentTime = audio.currentTime + 30; });
      } catch (_) { /* äldre webbläsare */ }
    }

    document.addEventListener("keydown", function (ev) {
      if (player.hidden || ev.target.closest("input, textarea, select, button, a")) return;
      if (ev.code === "Space") { ev.preventDefault(); if (audio.paused) play(); else audio.pause(); }
    });
  }

  /* ---------- Sök i arkivet ---------- */
  var search = document.getElementById("ep-search");
  if (search) {
    var rows = Array.prototype.slice.call(document.querySelectorAll(".ep-row[data-search]"));
    var groups = Array.prototype.slice.call(document.querySelectorAll(".year-group"));
    var count = document.getElementById("search-count");
    var empty = document.getElementById("search-empty");
    var norm = function (s) { return s.toLowerCase().normalize("NFC").trim(); };
    var run = function () {
      var terms = norm(search.value).split(/\s+/).filter(Boolean);
      var shown = 0;
      rows.forEach(function (r) {
        var hay = r.getAttribute("data-search");
        var ok = terms.every(function (t) { return hay.indexOf(t) !== -1; });
        r.hidden = !ok;
        if (ok) shown++;
      });
      groups.forEach(function (g) { g.hidden = !g.querySelector(".ep-row:not([hidden])"); });
      count.textContent = terms.length ? shown + " av " + rows.length + " avsnitt" : "";
      empty.hidden = shown !== 0;
    };
    search.addEventListener("input", run);
    var q = new URLSearchParams(window.location.search).get("q");
    if (q) { search.value = q; run(); }
  }

  /* ---------- Dela ---------- */
  document.querySelectorAll("[data-share]").forEach(function (b) {
    b.addEventListener("click", function () {
      var url = window.location.href.split("#")[0];
      var label = b.querySelector("span");
      var done = function (msg) {
        if (!label) return;
        var old = label.textContent;
        label.textContent = msg;
        setTimeout(function () { label.textContent = old; }, 2000);
      };
      if (navigator.share) {
        navigator.share({ title: b.getAttribute("data-title"), url: url }).catch(function () {});
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function () { done("Länk kopierad"); }, function () { done("Kunde inte kopiera"); });
      } else {
        window.prompt("Kopiera länken:", url);
      }
    });
  });

  /* ---------- Kontaktformulär ---------- */
  var form = document.getElementById("contact-form");
  if (form) {
    var status = form.querySelector(".form-status");
    var submit = form.querySelector('button[type="submit"]');
    var setStatus = function (msg, kind) {
      status.textContent = msg;
      status.className = "form-status" + (kind ? " is-" + kind : "");
    };
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var invalid = null;
      form.querySelectorAll("[required]").forEach(function (f) {
        var bad = !f.value.trim() || (f.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.value.trim()));
        f.setAttribute("aria-invalid", bad ? "true" : "false");
        if (bad && !invalid) invalid = f;
      });
      if (invalid) { setStatus("Fyll i namn, en giltig e-postadress och ett meddelande.", "error"); invalid.focus(); return; }
      if (form.botcheck && form.botcheck.value) return;

      var endpoint = form.getAttribute("data-endpoint");
      var email = form.getAttribute("data-email");
      var data = new FormData(form);

      if (!endpoint) {
        if (!email) { setStatus("Kontaktformuläret är inte aktiverat ännu.", "error"); return; }
        var body = data.get("message") + "\n\n— " + data.get("name") + " (" + data.get("email") + ")";
        window.location.href = "mailto:" + email + "?subject=" + encodeURIComponent("Viruspodden: " + data.get("topic")) + "&body=" + encodeURIComponent(body);
        setStatus("Ditt e-postprogram öppnas med meddelandet ifyllt.", "ok");
        return;
      }

      var subject = "Viruspodden: " + data.get("topic") + " – från " + data.get("name");
      data.set("subject", subject);
      data.set("_subject", subject);
      data.set("_replyto", data.get("email"));
      data.delete("botcheck");
      submit.disabled = true;
      setStatus("Skickar…");
      fetch(endpoint, { method: "POST", body: data, headers: { Accept: "application/json" } })
        .then(function (res) {
          if (!res.ok) throw new Error(String(res.status));
          form.reset();
          setStatus("Tack! Ditt meddelande är skickat – vi återkommer så snart vi kan.", "ok");
        })
        .catch(function () {
          setStatus("Något gick fel. Försök igen" + (email ? " eller mejla " + email : "") + ".", "error");
        })
        .finally(function () { submit.disabled = false; });
    });
  }
})();
