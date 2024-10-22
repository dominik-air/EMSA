import React, { useState } from "react";
import Button from "@mui/material/Button";
import CssBaseline from "@mui/material/CssBaseline";
import TextField from "@mui/material/TextField";
import Link from "@mui/material/Link";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import Alert from "@mui/material/Alert";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { ThemeProvider } from "@mui/material/styles";
import axios from "axios";
import logo from "../assets/emsa-logo.png";
import useCustomTheme from "./Theme";
import { useAuth } from "./useAuth";

export default function SignIn() {
  const API_URL = import.meta.env.VITE_API_URL;
  const [loginError, setLoginError] = useState("");

  const loginService = async (email: string, password: string) => {
    try {
      const response = await axios.post(`${API_URL}/login`, {
        mail: email,
        password: password,
      });
      console.log(response);
      return response.data;
    } catch (error) {
      console.error("Error during login service", error);
      throw error;
    }
  };

  const { login } = useAuth();

  const handleLogin = async (email: string, password: string) => {
    try {
      const response = await loginService(email, password);
      console.log(response);
      const { access_token } = response;
      console.log(access_token);

      login(email, access_token);
      setLoginError("");
    } catch (error) {
      console.error("Login error", error);
      setLoginError("Invalid credentials. Please try again.");
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const email = data.get("email");
    const password = data.get("password");

    if (typeof email === "string" && typeof password === "string") {
      await handleLogin(email, password);
    } else {
      console.error("Form data is not valid.");
    }
  };

  return (
    <ThemeProvider theme={useCustomTheme()}>
      <Container component="main" maxWidth="xs">
        <CssBaseline />
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            height: "100vh",
          }}
        >
          <img
            src={logo}
            alt="EMSA Logo"
            style={{
              width: "150px",
              height: "150px",
              marginBottom: "24px",
              borderRadius: "30%",
              objectFit: "cover",
            }}
          />

          <Typography component="h1" variant="h5">
            Sign in
          </Typography>

          {loginError && <Alert severity="error">{loginError}</Alert>}

          <Box
            component="form"
            onSubmit={handleSubmit}
            noValidate
            sx={{ mt: 1 }}
          >
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
            >
              Sign In
            </Button>
            <Grid container>
              <Grid item xs>
                <Link href="#" variant="body2">
                  Forgot password?
                </Link>
              </Grid>
              <Grid item>
                <Link href="/signup" variant="body2">
                  {"Don't have an account? Sign Up"}
                </Link>
              </Grid>
            </Grid>
          </Box>
        </Box>
      </Container>
    </ThemeProvider>
  );
}
