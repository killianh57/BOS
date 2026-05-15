// Year
document.getElementById("year").textContent = new Date().getFullYear();

// Burger menu (mobile)
const burger = document.querySelector(".nav__burger");
const navLinks = document.querySelector(".nav__links");
if (burger && navLinks) {
  burger.addEventListener("click", () => {
    const open = burger.getAttribute("aria-expanded") === "true";
    burger.setAttribute("aria-expanded", String(!open));
    if (!open) {
      navLinks.style.display = "flex";
      navLinks.style.flexDirection = "column";
      navLinks.style.position = "absolute";
      navLinks.style.top = "72px";
      navLinks.style.left = "0";
      navLinks.style.right = "0";
      navLinks.style.background = "#fff";
      navLinks.style.padding = "20px 24px";
      navLinks.style.gap = "16px";
      navLinks.style.borderBottom = "1px solid rgba(14,23,38,.06)";
      navLinks.style.boxShadow = "0 8px 24px rgba(14,23,38,.06)";
    } else {
      navLinks.style.cssText = "";
    }
  });
}

// Reveal on scroll
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
);

document
  .querySelectorAll(
    ".section__head, .feature, .duo__card, .step, .docs, .quote, .hero__card, .contact-block, .hero__content"
  )
  .forEach((el) => {
    el.classList.add("reveal");
    observer.observe(el);
  });

// Smooth close mobile menu when clicking a nav link
document.querySelectorAll(".nav__links a").forEach((a) => {
  a.addEventListener("click", () => {
    if (window.matchMedia("(max-width: 980px)").matches) {
      navLinks.style.cssText = "";
      burger.setAttribute("aria-expanded", "false");
    }
  });
});
