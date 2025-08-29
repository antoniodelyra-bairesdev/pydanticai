import { User } from "@/lib/types/api/iv/auth";

describe("Tela inicial", () => {
  it("Deveria mostrar a tela de login para um usuário não autenticado", () => {
    cy.visit("http://localhost:4000");
    cy.get('[data-test-id="login-heading"]').should(
      "have.text",
      "Acessar sistema",
    );
  });
  it("Deveria mostrar a tela inicial com o nome do usuário no menu lateral", () => {
    const user: User = {
      id: -1,
      nome: "Usuário de Teste",
      email: "usuario@de.teste",
      roles: [],
      devices: [],
    };
    cy.setCookie("user_token", "fakeusertoken", {
      path: "/",
      sameSite: "lax",
      httpOnly: true,
    });
    cy.visit("http://localhost:4000", {
      onBeforeLoad(window) {
        window.localStorage.setItem("iv.user", JSON.stringify(user));
      },
    });
    cy.get('[data-test-id="welcome-heading"]').should(
      "have.text",
      "Bem vindo(a)!",
    );
    cy.get('[data-test-id="navigation-open-zone"]').click();
    cy.get('[data-test-id="side-menu-user-name"]').should(
      "have.text",
      user.nome,
    );
  });
});
