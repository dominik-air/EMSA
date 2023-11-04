import React from "react";
import { render, fireEvent, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import SignUp from "../components/SignUp";

describe("<SignUp />", () => {
  test("renders the sign-up form", () => {
    render(<SignUp />);

    expect(screen.getByLabelText(/nickname/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /sign up/i }),
    ).toBeInTheDocument();
  });

  test("allows users to enter input", () => {
    render(<SignUp />);

    fireEvent.change(screen.getByLabelText(/nickname/i), {
      target: { value: "testuser" },
    });
    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "password123" },
    });

    expect(screen.getByLabelText(/nickname/i)).toHaveValue("testuser");
    expect(screen.getByLabelText(/email address/i)).toHaveValue(
      "test@example.com",
    );
    expect(screen.getByLabelText(/password/i)).toHaveValue("password123");
  });
});
