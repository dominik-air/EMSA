import React from "react";
import { render, fireEvent, waitFor, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import SignIn from "../components/SignIn";

describe("<SignIn />", () => {
  test("renders the sign-in form", () => {
    render(<SignIn />);

    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /sign in/i }),
    ).toBeInTheDocument();
  });

  test("allows the user to sign in", async () => {
    const { getByLabelText, getByRole } = render(<SignIn />);

    const consoleSpy = jest.spyOn(console, "log");

    const emailInput = getByLabelText(/email address/i);
    fireEvent.change(emailInput, { target: { value: "test@example.com" } });

    const passwordInput = getByLabelText(/password/i);
    fireEvent.change(passwordInput, { target: { value: "password123" } });

    fireEvent.click(getByRole("button", { name: /sign in/i }));

    await waitFor(() =>
      expect(consoleSpy).toHaveBeenCalledWith({
        email: "test@example.com",
        password: "password123",
      }),
    );

    consoleSpy.mockRestore();
  });
});
