// Cypress support file
import "./commands";

// Prevent uncaught exceptions from failing tests if triggered by third-party scripts or DOM timing
Cypress.on("uncaught:exception", (err, runnable) => {
  // Returning false here prevents Cypress from failing the test
  return false;
});
