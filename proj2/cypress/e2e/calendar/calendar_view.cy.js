describe("Calendar & Meal Plan View", () => {
  beforeEach(() => {
    cy.seedDatabase();
    cy.loginAsUser("testuser@example.com", "password123");
  });

  it("renders the interactive meal calendar for the current month", () => {
    cy.visit("/");
    cy.get("h1").should("contain.text", "Menu Calendar");
    cy.get(".greet, main").should("contain.text", "John Doe");
    cy.get(".cal-grid, .calendar-wrap, .day-cell").should("exist");
  });

  it("navigates between months using calendar controls", () => {
    cy.visit("/");

    // Click previous month or next month link
    cy.get("a").filter('[href*="/20"]').first().then(($link) => {
      const targetUrl = $link.attr("href");
      cy.wrap($link).click();
      cy.location("pathname").should("eq", targetUrl);
      cy.get("h1").should("contain.text", "Menu Calendar");
    });
  });

  it("allows navigating to explicit year and month via route params", () => {
    cy.visit("/2026/11");
    cy.get("h1").should("contain.text", "Menu Calendar");
    cy.contains("November").should("be.visible");
  });
});
