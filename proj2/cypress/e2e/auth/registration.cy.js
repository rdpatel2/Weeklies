describe("User Registration", () => {
  beforeEach(() => {
    cy.seedDatabase();
    cy.visit("/register");
  });

  it("successfully registers a new user with valid details and redirects to login", () => {
    const timestamp = Date.now();
    const email = `newuser_${timestamp}@example.com`;

    cy.get('input[name="fname"]').type("Alice");
    cy.get('input[name="lname"]').type("Wonderland");
    cy.get('input[name="email"]').type(email);
    cy.get('input[name="phone"]').type("9195551234");
    cy.get('input[name="password"]').type("password123");
    cy.get('input[name="confirm_password"]').type("password123");

    // Select an allergy checkbox
    cy.get('input[type="checkbox"][value="Peanuts"]').check();

    // Click a preference bubble
    cy.contains(".bubble", "Vegetarian").click();

    cy.get('#registerForm').submit();

    // After successful registration, user should be redirected to login page
    cy.location("pathname").should("eq", "/login");

    // Verify user can now log in with the new credentials
    cy.get('input[name="email"]').type(email);
    cy.get('input[name="password"]').type("password123");
    cy.get('input[type="submit"]').click();

    // Should arrive on index/calendar page
    cy.location("pathname").should("eq", "/");
    cy.contains("Welcome, Alice Wonderland").should("be.visible");
  });

  it("shows an alert when passwords do not match", () => {
    const stub = cy.stub();
    cy.on("window:alert", stub);

    cy.get('input[name="fname"]').type("Bob");
    cy.get('input[name="lname"]').type("Builder");
    cy.get('input[name="email"]').type("bob@example.com");
    cy.get('input[name="phone"]').type("9195559876");
    cy.get('input[name="password"]').type("password123");
    cy.get('input[name="confirm_password"]').type("mismatched123");

    cy.get('#registerForm').submit().then(() => {
      expect(stub.getCall(0)).to.be.calledWith("Passwords do not match.");
    });
    cy.location("pathname").should("eq", "/register");
  });

  it("shows an error when password is too short", () => {
    cy.get('input[name="fname"]').type("Charlie");
    cy.get('input[name="lname"]').type("Brown");
    cy.get('input[name="email"]').type("charlie@example.com");
    cy.get('input[name="phone"]').type("9195554321");
    cy.get('input[name="password"]').type("12345");
    cy.get('input[name="confirm_password"]').type("12345");

    cy.get('#registerForm').submit();

    cy.get(".flash").should("be.visible").and("contain.text", "at least 6 characters");
  });

  it("shows an error when registering with an already existing email", () => {
    cy.get('input[name="fname"]').type("Duplicate");
    cy.get('input[name="lname"]').type("User");
    cy.get('input[name="email"]').type("testuser@example.com"); // seeded email
    cy.get('input[name="phone"]').type("9195550000");
    cy.get('input[name="password"]').type("password123");
    cy.get('input[name="confirm_password"]').type("password123");

    cy.get('#registerForm').submit();

    cy.get(".flash").should("be.visible").and("contain.text", "Email already registered");
  });

  it("shows an error when first or last name is missing", () => {
    cy.get('input[name="email"]').type("noname@example.com");
    cy.get('input[name="phone"]').type("9195551111");
    cy.get('input[name="password"]').type("password123");
    cy.get('input[name="confirm_password"]').type("password123");

    cy.get('#registerForm').submit();

    cy.get(".flash").should("be.visible").and("contain.text", "First and last name are required");
  });
});
