describe("Order Workflow", () => {
  beforeEach(() => {
    cy.seedDatabase();
    cy.loginAsUser("testuser@example.com", "password123");
  });

  it("builds an order using the restaurant and item selectors", () => {
    cy.visit("/orders");

    // Select restaurant
    cy.get("#restaurantSelect").select("Taste of Italy");

    // Menu item selector should be enabled and populated
    cy.get("#itemSelect").should("not.be.disabled");
    cy.get("#itemSelect").select("1");

    // Set quantity
    cy.get("#qtyInput").clear().type("2");

    // Add note
    cy.get("#notes").type("Please deliver with extra crushed red pepper");

    // Add to order
    cy.get("#addBtn").click();

    // Verify item is present in cart table
    cy.get("#cartTable, #cartSection").should("contain.text", "Margherita Pizza");
  });

  it("successfully places an order via POST /order API and verifies it in profile", () => {
    const today = new Date().toISOString().split("T")[0];

    cy.request({
      method: "POST",
      url: "/order",
      body: {
        restaurant_id: 1,
        delivery_type: "delivery",
        date: today,
        meal: 3,
        tip: 4.5,
        eta_minutes: 30,
        items: [
          { itm_id: 1, qty: 1, notes: "Well done" },
          { itm_id: 2, qty: 2, notes: "Extra spicy" }
        ]
      }
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property("ok", true);
      expect(response.body).to.have.property("ord_id");

      const newOrderId = response.body.ord_id;

      // Visit profile to verify newly placed order appears
      cy.visit("/profile");
      cy.contains("Taste of Italy").should("be.visible");
      cy.contains("Ordered").should("be.visible");
    });
  });

  it("rejects order placement with invalid restaurant or items", () => {
    cy.request({
      method: "POST",
      url: "/order",
      failOnStatusCode: false,
      body: {
        restaurant_id: 9999, // nonexistent
        items: [{ itm_id: 1, qty: 1 }]
      }
    }).then((response) => {
      expect(response.status).to.be.oneOf([400, 404]);
      expect(response.body.ok).to.be.false;
    });
  });
});
