import React, { createContext, useState, ReactNode, ReactElement } from "react";

interface AuthContextType {
  isLoggedIn: boolean;
  email: string;
  login: (email: string, token: string) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({
  children,
}): ReactElement => {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(
    Boolean(localStorage.getItem("sessionToken")),
  );
  const [email, setEmail] = useState<string>(
    localStorage.getItem("email") ?? "no email",
  );

  const login = (email: string, token: string) => {
    console.log(`email: ${email}, token: ${token}`);
    localStorage.setItem("sessionToken", token);
    localStorage.setItem("email", email);
    setEmail(email);
    setIsLoggedIn(true);
  };

  const logout = () => {
    localStorage.removeItem("sessionToken");
    localStorage.removeItem("email");
    setEmail("no email");
    setIsLoggedIn(false);
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, login, logout, email }}>
      {children}
    </AuthContext.Provider>
  );
};
