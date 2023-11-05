import React, { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./useAuth";

interface PrivateRouteProps {
  children: ReactNode;
}

export const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const { isLoggedIn } = useAuth();

  if (!isLoggedIn) {
    return <Navigate to="/signin" />;
  }

  return <>{children}</>;
};

interface RedirectRouteProps {
  children: ReactNode;
  redirectRoute: string;
}

export const RedirectRoute: React.FC<RedirectRouteProps> = ({
  children,
  redirectRoute,
}) => {
  const { isLoggedIn } = useAuth();

  if (isLoggedIn) {
    return <Navigate to={redirectRoute} />;
  }
  return <>{children}</>;
};
