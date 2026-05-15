// Année dans le footer
document.getElementById("year").textContent = new Date().getFullYear();

// Nav scroll shadow
const nav = document.getElementById("nav");
const onScroll = () => {
  if (window.scrollY > 12) nav.classList.add("is-scrolled");
  else nav.classList.remove("is-scrolled");
};
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

// Mobile menu
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

// Reveal au scroll
const io = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        io.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12, rootMargin: "0px 0px -60px 0px" }
);
document
  .querySelectorAll(
    ".section__head, .feature, .duo__card, .step, .docs, .quote, .hero__visual, .hero__content, .contact-block, .strip"
  )
  .forEach((el) => {
    el.classList.add("reveal");
    io.observe(el);
  });

// Form submit — ouvre un mailto avec les infos pré-remplies
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
      qualification: data.get("qualification"),
      firstname: data.get("firstname"),
      lastname: data.get("lastname"),
      phone: data.get("phone"),
      email: data.get("email"),
      message: data.get("message") || "",
    };
    const subject = `Inscription Hygie — ${fields.qualification} — ${fields.firstname} ${fields.lastname}`;
    const body = [
      `Civilité : ${fields.title}`,
      `Nom : ${fields.lastname}`,
      `Prénom : ${fields.firstname}`,
      `Qualification : ${fields.qualification}`,
      `Téléphone : ${fields.phone}`,
      `Email : ${fields.email}`,
      ``,
      `Message :`,
      fields.message,
    ].join("\n");
    const href = `mailto:contact@hygie-interim.fr?subject=${encodeURIComponent(
      subject
    )}&body=${encodeURIComponent(body)}`;
    window.location.href = href;

    const success = form.querySelector(".form-success");
    success.hidden = false;
    setTimeout(() => {
      form.querySelectorAll("input, textarea").forEach((el) => (el.value = ""));
      form.querySelectorAll("select").forEach((el) => (el.selectedIndex = 0));
    }, 500);
  });
}
