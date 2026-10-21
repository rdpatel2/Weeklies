describe("User Profile View", () => {
  beforeEach(() => {
    cy.seedDatabase();
    cy.loginAsUser("testuser@example.com", "password123");
    cy.visit("/profile");
  });

  it("displays user information correctly", () => {
    cy.get(".card-body").first().within(() => {
      cy.contains("John Doe").should("be.visible");
      cy.contains("testuser@example.com").should("be.visible");
      cy.contains("9195550101").should("be.visible");
    });
  });

  it("displays user allergies and preferences", () => {
    cy.get('[aria-label="Allergies"]').should("contain.text", "Peanuts");
    cy.get("#prefBubbles").should("be.visible");
  });

  it("displays order history with details and statuses", () => {
    cy.get("table, .order-list, .meta-grid").should("exist");
    // Verify seeded delivered order appears
    cy.contains("Taste of Italy").should("be.visible");
  });

  it("redirects unauthenticated users to login", () => {
    cy.logoutUser();
    cy.visit("/profile");
    cy.location("pathname").should("eq", "/login");
  });
});
