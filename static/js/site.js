document.addEventListener("DOMContentLoaded", () => {
  const hero = document.querySelector(".hero");
  const cards = document.querySelectorAll(".card");

  if (hero) {
    gsap.fromTo(hero, { y: 18, opacity: 0 }, { y: 0, opacity: 1, duration: 0.9, ease: "power3.out" });
  }

  if (cards.length) {
    gsap.fromTo(cards,
      { y: 16, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.65, stagger: 0.06, ease: "power2.out", delay: 0.15 }
    );

    cards.forEach((c) => {
      c.addEventListener("mouseenter", () => gsap.to(c, { scale: 1.015, duration: 0.25, ease: "power2.out" }));
      c.addEventListener("mouseleave", () => gsap.to(c, { scale: 1, duration: 0.25, ease: "power2.out" }));
    });
  }
});
