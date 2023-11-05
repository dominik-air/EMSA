import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./components/AuthProvider";
import SignIn from "./components/SignIn";
import SignUp from "./components/SignUp";
import HomePage from "./components/HomePage";
import { PrivateRoute, RedirectRoute } from "./components/CustomRoutes";

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route
            path="/signin"
            element={
              <RedirectRoute redirectRoute="/">
                <SignIn />
              </RedirectRoute>
            }
          />
          <Route
            path="/signup"
            element={
              <RedirectRoute redirectRoute="/">
                <SignUp />
              </RedirectRoute>
            }
          />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <HomePage />
              </PrivateRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
