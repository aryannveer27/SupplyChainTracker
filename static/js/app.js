document.addEventListener("DOMContentLoaded", () => {
  /* ---------- Desktop & Mobile sidebar toggle ---------- */
  const sidebar = document.getElementById("sctSidebar");
  const backdrop = document.getElementById("sctSidebarBackdrop");
  const mobileToggleBtn = document.getElementById("sctNavToggle");
  const collapseBtn = document.getElementById("sctSidebarCollapseBtn");

  // Mobile
  const openSidebar = () => {
    sidebar && sidebar.classList.add("sct-mobile-open");
    backdrop && backdrop.classList.add("sct-mobile-open");
  };
  const closeSidebar = () => {
    sidebar && sidebar.classList.remove("sct-mobile-open");
    backdrop && backdrop.classList.remove("sct-mobile-open");
  };

  if (mobileToggleBtn) {
    mobileToggleBtn.addEventListener("click", () => {
      sidebar && sidebar.classList.contains("sct-mobile-open") ? closeSidebar() : openSidebar();
    });
  }
  if (backdrop) backdrop.addEventListener("click", closeSidebar);

  // Desktop Collapse
  if (collapseBtn) {
    collapseBtn.addEventListener("click", () => {
      sidebar && sidebar.classList.toggle("sct-collapsed");
    });
  }

  /* ---------- Navbar scroll shadow ---------- */
  const navbar = document.getElementById("sctNavbar");
  const onScroll = () => {
    if (!navbar) return;
    navbar.classList.toggle("sct-scrolled", window.scrollY > 6);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- Ambient floating particles ---------- */
  const field = document.getElementById("sctParticles");
  if (field) {
    const count = window.innerWidth < 700 ? 14 : 28;
    for (let i = 0; i < count; i++) {
      const p = document.createElement("span");
      p.className = "sct-particle";
      p.style.left = Math.random() * 100 + "%";
      p.style.setProperty("--sct-drift", (Math.random() * 60 - 30) + "px");
      p.style.animationDuration = 9 + Math.random() * 10 + "s";
      p.style.animationDelay = Math.random() * 10 + "s";
      p.style.opacity = 0.25 + Math.random() * 0.35;
      field.appendChild(p);
    }
  }

  /* ---------- Interactive Cards Glow Effect ---------- */
  document.querySelectorAll('.sct-stat-card').forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      card.style.setProperty('--mouse-x', `${x}px`);
      card.style.setProperty('--mouse-y', `${y}px`);
    });
  });
});
