(() => {
  "use strict";

  const nav = document.querySelector(".site-nav");
  const toggle = document.querySelector(".nav-toggle");
  const menu = document.querySelector(".nav-links");
  const links = Array.from(document.querySelectorAll(".nav-link"));

  const closeMenu = () => {
    if (!toggle || !menu) {
      return;
    }

    toggle.setAttribute("aria-expanded", "false");
    menu.classList.remove("open");
  };

  toggle?.addEventListener("click", () => {
    const opening = toggle.getAttribute("aria-expanded") !== "true";
    toggle.setAttribute("aria-expanded", String(opening));
    menu?.classList.toggle("open", opening);
  });

  links.forEach((link) => {
    link.addEventListener("click", closeMenu);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeMenu();
    }
  });

  document.addEventListener("click", (event) => {
    if (
      menu?.classList.contains("open") &&
      !menu.contains(event.target) &&
      !toggle?.contains(event.target)
    ) {
      closeMenu();
    }
  });

  const updateNavShadow = () => {
    nav?.classList.toggle("scrolled", window.scrollY > 24);
  };

  updateNavShadow();
  window.addEventListener("scroll", updateNavShadow, { passive: true });

  const sections = Array.from(document.querySelectorAll("section[id], header[id]"));
  const sectionLinks = new Map(
    links
      .filter((link) => link.dataset.section)
      .map((link) => [link.dataset.section, link]),
  );

  if (sectionLinks.size > 0 && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting && sectionLinks.has(entry.target.id))
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

        if (!visible) {
          return;
        }

        sectionLinks.forEach((link) => link.classList.remove("active"));
        sectionLinks.get(visible.target.id)?.classList.add("active");
      },
      { rootMargin: "-25% 0px -60%", threshold: [0, 0.25, 0.5] },
    );

    sections.forEach((section) => observer.observe(section));
  }
})();
