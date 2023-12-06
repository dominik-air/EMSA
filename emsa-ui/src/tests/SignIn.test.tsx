import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import SignIn from "../components/SignIn";

const mockLogin = jest.fn();
const mockLogout = jest.fn();

jest.mock("../components/useAuth", () => ({
  useAuth: () => ({
    isLoggedIn: false,
    login: mockLogin,
    logout: mockLogout,
  }),
}));

describe("<SignIn />", () => {
  test("renders the sign-in form", () => {
    render(<SignIn />);

    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /sign in/i }),
    ).toBeInTheDocument();
  });

  it("contains a link to the signup page", () => {
    render(<SignIn />);
    const signUpLink = screen.getByText("Don't have an account? Sign Up");
    expect(signUpLink.closest("a")).toHaveAttribute("href", "/signup");
  });
});
