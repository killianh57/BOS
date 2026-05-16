// ==========================================================
// HYGIE — Script v2
// ==========================================================

document.getElementById("year").textContent = new Date().getFullYear();

const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const isTouch = window.matchMedia("(hover: none)").matches || window.innerWidth < 768;

// ----------------------------------------------------------
// Indicateur de progression scroll
// ----------------------------------------------------------
const scrollProgress = document.getElementById("scrollProgress");
const updateProgress = () => {
  const h = document.documentElement;
  const scrolled = h.scrollTop / (h.scrollHeight - h.clientHeight);
  scrollProgress.style.width = `${Math.min(scrolled * 100, 100)}%`;
};
window.addEventListener("scroll", updateProgress, { passive: true });
updateProgress();

// ----------------------------------------------------------
// Parallax léger sur les éléments [data-parallax]
// ----------------------------------------------------------
if (!prefersReduced) {
  const parallaxEls = document.querySelectorAll("[data-parallax]");
  let parallaxTicking = false;
  const updateParallax = () => {
    const sy = window.scrollY;
    parallaxEls.forEach((el) => {
      const speed = parseFloat(el.dataset.parallax) || 0.3;
      el.style.transform = `translate3d(0, ${sy * speed * -1}px, 0)`;
    });
    parallaxTicking = false;
  };
  window.addEventListener(
    "scroll",
    () => {
      if (!parallaxTicking) {
        requestAnimationFrame(updateParallax);
        parallaxTicking = true;
      }
    },
    { passive: true }
  );
}

// ----------------------------------------------------------
// Word-by-word reveal sur le titre hero
// ----------------------------------------------------------
const splitTitle = (el) => {
  const lines = el.querySelectorAll(".t-line");
  lines.forEach((line, lineIdx) => {
    const html = line.innerHTML;
    // Parse les enfants : du texte + des <em>
    const tmp = document.createElement("div");
    tmp.innerHTML = html;
    const result = [];
    let wordCount = 0;
    const walk = (node, wrapTag) => {
      for (const child of node.childNodes) {
        if (child.nodeType === Node.TEXT_NODE) {
          const words = child.textContent.split(/(\s+)/);
          for (const w of words) {
            if (!w.trim()) {
              result.push(w);
              continue;
            }
            const delay = (lineIdx * 0.08 + wordCount * 0.035).toFixed(3);
            const inner = `<span style="transition-delay:${delay}s">${w}</span>`;
            const wrapped = `<span class="word-anim">${
              wrapTag ? `<${wrapTag}>${inner}</${wrapTag}>` : inner
            }</span>`;
            result.push(wrapped);
            wordCount++;
          }
        } else if (child.nodeType === Node.ELEMENT_NODE) {
          walk(child, child.tagName.toLowerCase());
        }
      }
    };
    walk(tmp, null);
    line.innerHTML = result.join("");
  });
};

const heroTitle = document.querySelector("[data-split]");
if (heroTitle) {
  splitTitle(heroTitle);
  // Animation au load
  requestAnimationFrame(() => {
    setTimeout(() => {
      heroTitle.querySelectorAll(".word-anim").forEach((w) => w.classList.add("in"));
    }, 100);
  });
}

// ----------------------------------------------------------
// Magnetic buttons (desktop only)
// ----------------------------------------------------------
if (!isTouch && !prefersReduced) {
  document.querySelectorAll("[data-magnetic]").forEach((el) => {
    let raf = null;
    let tx = 0, ty = 0, cx = 0, cy = 0;
    const strength = 0.3;
    const lerpVal = 0.18;

    const onMove = (e) => {
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      tx = x * strength;
      ty = y * strength;
      if (!raf) loop();
    };
    const onLeave = () => {
      tx = 0;
      ty = 0;
      if (!raf) loop();
    };
    const loop = () => {
      cx += (tx - cx) * lerpVal;
      cy += (ty - cy) * lerpVal;
      el.style.transform = `translate3d(${cx.toFixed(2)}px, ${cy.toFixed(2)}px, 0)`;
      if (Math.abs(tx - cx) > 0.1 || Math.abs(ty - cy) > 0.1) {
        raf = requestAnimationFrame(loop);
      } else {
        cx = tx;
        cy = ty;
        el.style.transform = `translate3d(${cx}px, ${cy}px, 0)`;
        raf = null;
      }
    };

    el.addEventListener("mousemove", onMove);
    el.addEventListener("mouseleave", onLeave);
  });
}

// ----------------------------------------------------------
// Tilt 3D sur cards (desktop only)
// ----------------------------------------------------------
if (!isTouch && !prefersReduced) {
  document.querySelectorAll("[data-tilt]").forEach((el) => {
    const maxRot = 4; // degrés max
    const onMove = (e) => {
      const rect = el.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      el.style.transform = `perspective(900px) rotateX(${(-y * maxRot).toFixed(
        2
      )}deg) rotateY(${(x * maxRot).toFixed(2)}deg) translateY(-4px)`;
    };
    const onLeave = () => {
      el.style.transform = "";
    };
    el.addEventListener("mousemove", onMove);
    el.addEventListener("mouseleave", onLeave);
  });
}

// ----------------------------------------------------------
// Nav scroll shadow
// ----------------------------------------------------------
const nav = document.getElementById("nav");
const onScroll = () => {
  if (window.scrollY > 12) nav.classList.add("is-scrolled");
  else nav.classList.remove("is-scrolled");
};
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

// ----------------------------------------------------------
// Curseur custom
// ----------------------------------------------------------
const cursor = document.getElementById("cursor");
if (cursor && window.matchMedia("(hover: hover)").matches) {
  let mx = window.innerWidth / 2;
  let my = window.innerHeight / 2;
  let cx = mx, cy = my;

  window.addEventListener("mousemove", (e) => {
    mx = e.clientX;
    my = e.clientY;
  });

  const lerp = () => {
    cx += (mx - cx) * 0.18;
    cy += (my - cy) * 0.18;
    cursor.style.transform = `translate(${cx}px, ${cy}px) translate(-50%, -50%)`;
    requestAnimationFrame(lerp);
  };
  lerp();

  document.querySelectorAll("[data-hover]").forEach((el) => {
    el.addEventListener("mouseenter", () => cursor.classList.add("is-hover"));
    el.addEventListener("mouseleave", () => cursor.classList.remove("is-hover"));
  });
}

// ----------------------------------------------------------
// Mobile menu
// ----------------------------------------------------------
const burger = document.getElementById("burger");
const mobileMenu = document.getElementById("mobileMenu");
const closeMenu = () => {
  burger.setAttribute("aria-expanded", "false");
  mobileMenu.classList.remove("is-open");
  setTimeout(() => mobileMenu.setAttribute("hidden", ""), 250);
};
const openMenu = () => {
  burger.setAttribute("aria-expanded", "true");
  mobileMenu.removeAttribute("hidden");
  requestAnimationFrame(() => mobileMenu.classList.add("is-open"));
};
burger.addEventListener("click", () => {
  const isOpen = burger.getAttribute("aria-expanded") === "true";
  if (isOpen) closeMenu();
  else openMenu();
});
mobileMenu.querySelectorAll("a").forEach((a) => a.addEventListener("click", closeMenu));

// ----------------------------------------------------------
// Reveal au scroll
// ----------------------------------------------------------
const io = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        io.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12, rootMargin: "0px 0px -80px 0px" }
);
document
  .querySelectorAll(
    ".section__head, .solution-card, .step, .t-card, .match, .ia-demo, .ia-text, .hero__title, .hero__lead, .hero__ctas, .trust-bar, .badge, .contact-block, .contact-form, .jobs, .marquee"
  )
  .forEach((el) => {
    el.classList.add("reveal");
    io.observe(el);
  });

// ----------------------------------------------------------
// Compteurs animés
// ----------------------------------------------------------
const counterIO = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const target = parseInt(el.dataset.counter, 10);
      const suffix = el.dataset.suffix || "";
      const duration = 1500;
      const start = performance.now();
      const animate = (now) => {
        const t = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - t, 3);
        const val = Math.round(target * eased);
        el.textContent = val.toLocaleString("fr-FR") + suffix;
        if (t < 1) requestAnimationFrame(animate);
      };
      requestAnimationFrame(animate);
      counterIO.unobserve(el);
    });
  },
  { threshold: 0.5 }
);
document.querySelectorAll("[data-counter]").forEach((el) => counterIO.observe(el));

// ----------------------------------------------------------
// MATCH WIDGET — pool de profils & matching simulé
// ----------------------------------------------------------
const matchBtn = document.getElementById("m-run");
const matchResults = document.getElementById("m-results");

const POOL = {
  "Infirmier(e) DE": [
    { n: "Camille L.", x: "8 ans", z: "Paris 13ᵉ" },
    { n: "Mathieu R.", x: "5 ans", z: "Paris 12ᵉ" },
    { n: "Aïcha B.", x: "11 ans", z: "Paris 14ᵉ" },
    { n: "Sarah M.", x: "6 ans", z: "Paris 11ᵉ" },
  ],
  "IDE Bloc": [
    { n: "Élise V.", x: "12 ans", z: "Boulogne" },
    { n: "Jean-Paul T.", x: "9 ans", z: "Paris 15ᵉ" },
    { n: "Léa K.", x: "7 ans", z: "Levallois" },
  ],
  "IBODE": [
    { n: "Maxime D.", x: "10 ans", z: "Paris 9ᵉ" },
    { n: "Nadia O.", x: "8 ans", z: "Saint-Cloud" },
    { n: "Antoine F.", x: "14 ans", z: "Paris 7ᵉ" },
  ],
  "IADE — Anesthésiste": [
    { n: "Pierre G.", x: "15 ans", z: "Paris 5ᵉ" },
    { n: "Inès C.", x: "8 ans", z: "Vincennes" },
    { n: "Hugo S.", x: "11 ans", z: "Paris 16ᵉ" },
  ],
  "Aide-soignant(e)": [
    { n: "Fatou D.", x: "6 ans", z: "Paris 18ᵉ" },
    { n: "Karim B.", x: "4 ans", z: "Saint-Denis" },
    { n: "Mélanie A.", x: "9 ans", z: "Créteil" },
  ],
  "Kinésithérapeute": [
    { n: "Thomas N.", x: "7 ans", z: "Paris 8ᵉ" },
    { n: "Sophie L.", x: "5 ans", z: "Neuilly" },
    { n: "Yann P.", x: "13 ans", z: "Paris 17ᵉ" },
  ],
  "Manipulateur(trice) radio": [
    { n: "Amélie R.", x: "9 ans", z: "Paris 6ᵉ" },
    { n: "Lucas T.", x: "4 ans", z: "Issy" },
    { n: "Mariam H.", x: "10 ans", z: "Paris 19ᵉ" },
  ],
};

if (matchBtn && matchResults) {
  matchBtn.addEventListener("click", () => {
    if (matchBtn.classList.contains("is-loading")) return;
    matchBtn.classList.add("is-loading");
    matchBtn.querySelector(".btn__loader").hidden = false;

    const qual = document.getElementById("m-qual").value;
    const zone = document.getElementById("m-zone").value;
    const type = document.getElementById("m-type").value;

    setTimeout(() => {
      const profiles = (POOL[qual] || POOL["Infirmier(e) DE"]).slice(0, 3);
      const scores = [98, 94, 91];
      matchResults.innerHTML = profiles
        .map(
          (p, i) => `
        <div class="match-result">
          <div class="match-result__left">
            <div class="match-result__avatar">${p.n.charAt(0)}</div>
            <div>
              <div class="match-result__title">${qual} · ${zone}</div>
              <div class="match-result__meta">
                <span>${p.n}</span>
                <span>·</span>
                <span>${p.x} d'expérience</span>
                <span>·</span>
                <span>${p.z}</span>
                <span>·</span>
                <span>${type}</span>
              </div>
            </div>
          </div>
          <div class="match-result__score">
            <span class="match-result__score-num">${scores[i]}</span>
            <span class="match-result__score-label">%</span>
          </div>
        </div>
      `
        )
        .join("");
      matchBtn.classList.remove("is-loading");
      matchBtn.querySelector(".btn__loader").hidden = true;
    }, 1100);
  });
}

// ----------------------------------------------------------
// Clic sur un métier → pré-remplit le formulaire avec la qualif
// ----------------------------------------------------------
document.querySelectorAll(".job[data-prefill]").forEach((j) => {
  j.addEventListener("click", () => {
    const qual = j.dataset.prefill;
    setTimeout(() => {
      const profileSelect = document.querySelector('.contact-form select[name="profile"]');
      if (profileSelect) {
        profileSelect.value = "Soignant — candidature";
      }
      const msg = document.querySelector('.contact-form textarea[name="message"]');
      if (msg) {
        msg.value = `Bonjour, je suis ${qual} et je souhaite m'inscrire chez Hygie. Disponibilités : `;
        msg.focus();
      }
    }, 600);
  });
});

// ----------------------------------------------------------
// FORM CONTACT
// ----------------------------------------------------------
const form = document.getElementById("contactForm");
if (form) {
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    const data = new FormData(form);
    const fields = {
      title: data.get("title"),
      profile: data.get("profile"),
      firstname: data.get("firstname"),
      lastname: data.get("lastname"),
      phone: data.get("phone"),
      email: data.get("email"),
      message: data.get("message") || "",
    };
    const subject = `Hygie — ${fields.profile} — ${fields.firstname} ${fields.lastname}`;
    const body = [
      `Civilité : ${fields.title}`,
      `Profil : ${fields.profile}`,
      `Nom : ${fields.lastname}`,
      `Prénom : ${fields.firstname}`,
      `Téléphone : ${fields.phone}`,
      `Email : ${fields.email}`,
      ``,
      `Message :`,
      fields.message,
    ].join("\n");
    window.location.href = `mailto:contact@hygie-interim.fr?subject=${encodeURIComponent(
      subject
    )}&body=${encodeURIComponent(body)}`;

    const success = form.querySelector(".form-success");
    success.hidden = false;
    setTimeout(() => {
      form.reset();
    }, 500);
  });
}

// ----------------------------------------------------------
// CHATBOT
// ----------------------------------------------------------
const chatToggle = document.getElementById("chatToggle");
const chat = document.getElementById("chat");
const chatBody = document.getElementById("chatBody");
const chatInput = document.getElementById("chatInput");
const chatClose = document.getElementById("chatClose");

const openChat = () => {
  chat.removeAttribute("hidden");
  requestAnimationFrame(() => {
    chat.classList.add("is-open");
    chatToggle.classList.add("is-open");
  });
};
const closeChat = () => {
  chat.classList.remove("is-open");
  chatToggle.classList.remove("is-open");
  setTimeout(() => chat.setAttribute("hidden", ""), 300);
};
chatToggle.addEventListener("click", () => {
  if (chatToggle.classList.contains("is-open")) closeChat();
  else openChat();
});
chatClose.addEventListener("click", closeChat);

const KB = {
  "comment m'inscrire": {
    answer:
      "L'inscription se fait à l'agence, sans rendez-vous : 19 Rue Mogador, Paris 9ᵉ, du lundi au vendredi 8h–19h. Apporte tes diplômes, ADELI, pièce d'identité et CV. On t'inscrit en 30 min.",
    next: ["Quels documents apporter ?", "Vous recrutez en CDI ?"],
  },
  "quels documents apporter": {
    answer:
      "Originaux : diplôme d'État, ADELI, pièce d'identité, carte vitale, casier judiciaire B3. Photocopies : justificatif de domicile, carnet de vaccination, CV. Si tu as une fiche d'aptitude médicale ou permis, prends-les aussi.",
    next: ["Comment m'inscrire ?", "Je suis directeur d'établissement"],
  },
  "recrutez-vous en cdi": {
    answer:
      "Oui — Hygie propose de l'intérim, du CDD et du CDI. La majorité des missions démarrent en intérim, certaines évoluent ensuite en CDI selon les besoins et tes envies.",
    next: ["Comment m'inscrire ?", "Quels métiers ?"],
  },
  "je suis directeur": {
    answer:
      "Bienvenue. On peut couvrir vos plannings 24/7 sur toutes les spécialités. Appelez le 01 42 66 03 20 ou laissez vos coordonnées dans le formulaire en bas — un consultant senior vous rappelle dans la journée.",
    next: ["Quels métiers ?", "Vous travaillez où ?"],
  },
  "quels métiers": {
    answer:
      "Toutes les spécialités médicales et paramédicales : IDE, IBODE, IADE, aide-soignant, kiné, manipulateur radio, brancardier, préparateur en pharmacie, et plus. Si ta spé n'est pas listée, on en discute.",
    next: ["Comment m'inscrire ?", "Vous travaillez où ?"],
  },
  "vous travaillez où": {
    answer:
      "Paris intra-muros, petite et grande couronne. On couvre toute l'Île-de-France.",
    next: ["Comment m'inscrire ?", "Je suis directeur d'établissement"],
  },
};

const normalize = (s) =>
  s
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/[?.,!'"]/g, "")
    .trim();

const findAnswer = (q) => {
  const nq = normalize(q);
  for (const [key, val] of Object.entries(KB)) {
    if (nq.includes(normalize(key))) return val;
  }
  return {
    answer:
      "Bonne question ! Pour ce sujet précis, le mieux est d'appeler l'équipe au 01 42 66 03 20 (24/7) ou d'utiliser le formulaire en bas — un consultant te répond rapidement.",
    next: ["Comment m'inscrire ?", "Quels documents apporter ?"],
  };
};

const addBubble = (text, sender = "ai", suggestions = []) => {
  const msg = document.createElement("div");
  msg.className = `chat__msg chat__msg--${sender}`;
  const bubble = document.createElement("div");
  bubble.className = "chat__bubble";
  bubble.textContent = text;
  msg.appendChild(bubble);

  if (suggestions.length) {
    const wrap = document.createElement("div");
    wrap.className = "chat__suggestions";
    suggestions.forEach((s) => {
      const b = document.createElement("button");
      b.className = "chat__suggestion";
      b.type = "button";
      b.dataset.q = s;
      b.textContent = s;
      wrap.appendChild(b);
    });
    bubble.appendChild(wrap);
  }
  chatBody.appendChild(msg);
  chatBody.scrollTop = chatBody.scrollHeight;
};

const addTyping = () => {
  const msg = document.createElement("div");
  msg.className = "chat__msg chat__msg--ai chat__msg--typing";
  msg.innerHTML = `<div class="chat__bubble"><div class="chat__typing"><span></span><span></span><span></span></div></div>`;
  chatBody.appendChild(msg);
  chatBody.scrollTop = chatBody.scrollHeight;
  return msg;
};

const askChat = (q) => {
  addBubble(q, "me");
  const typing = addTyping();
  setTimeout(() => {
    typing.remove();
    const a = findAnswer(q);
    addBubble(a.answer, "ai", a.next);
  }, 700 + Math.random() * 500);
};

chatBody.addEventListener("click", (e) => {
  const s = e.target.closest(".chat__suggestion");
  if (s) askChat(s.dataset.q);
});

chatInput.addEventListener("submit", (e) => {
  e.preventDefault();
  const input = chatInput.querySelector("input");
  const v = input.value.trim();
  if (!v) return;
  input.value = "";
  askChat(v);
});
