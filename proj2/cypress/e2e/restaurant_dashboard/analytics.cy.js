describe("Restaurant Analytics Dashboard", () => {
  beforeEach(() => {
    cy.seedDatabase();
    cy.loginAsRestaurant("owner@tasteofitaly.com", "password123");
    cy.visit("/restaurant/analytics");
  });

  it("renders the analytics dashboard with key metric cards", () => {
    cy.get(".analytics-header").should("contain.text", "Analytics");
    cy.contains("Taste of Italy").should("be.visible");

    // Metrics grid
    cy.get(".analytics-grid").should("be.visible");
    cy.contains(".metric-label", "Total Orders").should("be.visible");
    cy.contains(".metric-label", "Total Revenue").should("be.visible");
    cy.contains(".metric-label", "Avg Order Value").should("be.visible");
  });

  it("provides back link navigation to the main restaurant dashboard", () => {
    cy.get(".analytics-nav a").contains(/Dashboard/i).click();
    cy.location("pathname").should("eq", "/restaurant/dashboard");
  });
});
