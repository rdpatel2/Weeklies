describe("User Authentication & Session", () => {
  beforeEach(() => {
    cy.seedDatabase();
  });

  it("logs in successfully with valid credentials and redirects to home", () => {
    cy.visit("/login");
    cy.get('input[name="email"]').type("testuser@example.com");
    cy.get('input[name="password"]').type("password123");
    cy.get('input[type="submit"]').click();

    cy.location("pathname").should("eq", "/");
    cy.get(".greet, main").should("contain.text", "John Doe");
    cy.get("header nav").should("contain.text", "Profile");
  });

  it("displays an error message with invalid credentials", () => {
    cy.visit("/login");
    cy.get('input[name="email"]').type("testuser@example.com");
    cy.get('input[name="password"]').type("wrongpassword");
    cy.get('input[type="submit"]').click();

    cy.location("pathname").should("eq", "/login");
    cy.get(".flash").should("be.visible").and("contain.text", "Invalid credentials");
  });

  it("displays an error message when email does not exist", () => {
    cy.visit("/login");
    cy.get('input[name="email"]').type("nonexistent@example.com");
    cy.get('input[name="password"]').type("password123");
    cy.get('input[type="submit"]').click();

    cy.location("pathname").should("eq", "/login");
    cy.get(".flash").should("be.visible").and("contain.text", "Invalid credentials");
  });

  it("logs out successfully and terminates the session", () => {
    cy.loginAsUser("testuser@example.com", "password123");
    cy.visit("/");
    cy.get(".greet, main").should("contain.text", "John Doe");

    // Click logout
    cy.get("header nav").contains("Logout").click();
    cy.location("pathname").should("eq", "/login");

    // Attempting to visit protected profile route should redirect back to login
    cy.visit("/profile");
    cy.location("pathname").should("eq", "/login");
  });

  it("redirects unauthenticated users trying to access protected routes", () => {
    cy.visit("/profile");
    cy.location("pathname").should("eq", "/login");

    cy.visit("/orders");
    cy.location("pathname").should("eq", "/login");
  });
});
