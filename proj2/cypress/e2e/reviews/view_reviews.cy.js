describe("View Reviews", () => {
  beforeEach(() => {
    cy.seedDatabase();
  });

  it("views individual submitted review for an order", () => {
    cy.loginAsUser("testuser@example.com", "password123");
    cy.visit("/order/1/review/view");

    cy.contains("Order #1").should("be.visible");
    cy.contains("Outstanding Pizza and Pasta!").should("be.visible");
    cy.contains("Taste of Italy").should("be.visible");
  });

  it("views public restaurant reviews page", () => {
    cy.visit("/restaurant/1/reviews");

    cy.contains("Taste of Italy").should("be.visible");
    cy.contains("Outstanding Pizza and Pasta!").should("be.visible");
  });

  it("shows back link to profile from review view", () => {
    cy.loginAsUser("testuser@example.com", "password123");
    cy.visit("/order/1/review/view");

    cy.get("a").contains(/Profile/i).click();
    cy.location("pathname").should("eq", "/profile");
  });
});
