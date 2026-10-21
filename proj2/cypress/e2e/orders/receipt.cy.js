describe("Order PDF Receipt", () => {
  beforeEach(() => {
    cy.seedDatabase();
  });

  it("allows user to download PDF receipt for an order they own", () => {
    cy.loginAsUser("testuser@example.com", "password123");

    cy.request({
      method: "GET",
      url: "/orders/1/receipt.pdf",
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.headers["content-type"]).to.include("application/pdf");
      expect(response.body).to.include("%PDF");
    });
  });

  it("returns 404 for a non-existent order ID", () => {
    cy.loginAsUser("testuser@example.com", "password123");

    cy.request({
      method: "GET",
      url: "/orders/99999/receipt.pdf",
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(404);
    });
  });

  it("forbids accessing an order receipt owned by another user", () => {
    // Log in as second user (Jane Smith) and try to access order 1 (owned by John Doe)
    cy.loginAsUser("seconduser@example.com", "password123");

    cy.request({
      method: "GET",
      url: "/orders/1/receipt.pdf",
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(403);
    });
  });

  it("redirects unauthenticated users trying to download receipts", () => {
    cy.request({
      method: "GET",
      url: "/orders/1/receipt.pdf",
      followRedirect: false,
    }).then((response) => {
      expect(response.status).to.be.oneOf([302, 303]);
      expect(response.headers.location).to.include("/login");
    });
  });
});
