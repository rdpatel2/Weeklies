describe("Restaurant & Menu Browsing", () => {
  beforeEach(() => {
    cy.seedDatabase();
    cy.loginAsUser("testuser@example.com", "password123");
    cy.visit("/restaurants");
  });

  it("renders the restaurant directory with seeded restaurants", () => {
    cy.get("h1").should("contain.text", "Restaurants");
    cy.get("#restList").should("be.visible");
    cy.contains("Taste of Italy").should("be.visible");
    cy.contains("Green Garden Bistro").should("be.visible");
  });

  it("expands a restaurant accordion to reveal its menu items", () => {
    cy.contains(".accordion-header", "Taste of Italy").click();
    cy.contains("Margherita Pizza").should("be.visible");
    cy.contains("Penne Arrabbiata").should("be.visible");
    cy.contains("$14.99").should("be.visible");
  });

  it("filters restaurants and menu items using the search input", () => {
    cy.get("#searchInput").type("Avocado");
    // Green Garden Bistro should match
    cy.contains("Green Garden Bistro").should("be.visible");
  });

  it("adds a menu item to the cart and displays it in the cart panel", () => {
    cy.contains(".accordion-header", "Taste of Italy").click();
    // Click Add to Cart for Margherita Pizza
    cy.contains(".menu-item", "Margherita Pizza").find("button, .btn").contains(/Add/i).click();

    // Verify cart section updates
    cy.get("#cartSection").should("be.visible");
    cy.get("#cartGroups").should("contain.text", "Margherita Pizza");

    // Clear cart button resets the cart
    cy.get("#clearCartBtn").click();
    cy.get("#cartEmptyMsg").should("be.visible");
  });
});
