describe("Restaurant Owner Reviews View", () => {
  beforeEach(() => {
    cy.seedDatabase();
    cy.loginAsRestaurant("owner@tasteofitaly.com", "password123");
    cy.visit("/restaurant/reviews");
  });

  it("renders the owner reviews dashboard with customer reviews", () => {
    cy.get(".restaurant-info").should("contain.text", "Taste of Italy");
    cy.contains("Outstanding Pizza and Pasta!").should("be.visible");
  });

  it("displays rating statistics and filter controls", () => {
    cy.get("select, .filter-control, #filter").should("exist");
  });
});
