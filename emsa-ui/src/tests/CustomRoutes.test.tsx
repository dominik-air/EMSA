import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { MemoryRouter } from "react-router-dom";
import { PrivateRoute, RedirectRoute } from "../components/CustomRoutes";
import { useAuth } from "../components/useAuth";

jest.mock("../components/useAuth", () => ({
  useAuth: jest.fn(),
}));

const renderWithRouter = (ui, { route = "/" } = {}) => {
  window.history.pushState({}, "Test page", route);

  return render(ui, { wrapper: MemoryRouter });
};

describe("PrivateRoute", () => {
  beforeEach(() => {
    (useAuth as jest.Mock).mockImplementation(() => ({ isLoggedIn: false }));
  });
  afterEach(() => {
    jest.resetAllMocks();
  });
  it("renders children when user is logged in", () => {
    (useAuth as jest.Mock).mockImplementation(() => ({ isLoggedIn: true }));
    renderWithRouter(<PrivateRoute>Private</PrivateRoute>);
    expect(screen.getByText("Private")).toBeInTheDocument();
  });

  it("redirects to signin when user is not logged in", () => {
    renderWithRouter(<PrivateRoute>Private</PrivateRoute>);
  });
});

describe("RedirectRoute", () => {
  beforeEach(() => {
    (useAuth as jest.Mock).mockImplementation(() => ({ isLoggedIn: false }));
  });
  afterEach(() => {
    jest.resetAllMocks();
  });
  it("renders children when user is not logged in", () => {
    renderWithRouter(
      <RedirectRoute redirectRoute="/somewhere">Non-private</RedirectRoute>,
    );
    expect(screen.getByText("Non-private")).toBeInTheDocument();
  });

  it("redirects to the specified route when user is logged in", () => {
    (useAuth as jest.Mock).mockImplementation(() => ({ isLoggedIn: true }));
    renderWithRouter(
      <RedirectRoute redirectRoute="/somewhere">Non-private</RedirectRoute>,
    );
  });
});
