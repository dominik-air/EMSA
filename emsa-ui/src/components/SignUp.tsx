import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Button from "@mui/material/Button";
import CssBaseline from "@mui/material/CssBaseline";
import TextField from "@mui/material/TextField";
import Link from "@mui/material/Link";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import Alert from "@mui/material/Alert";
import { ThemeProvider } from "@mui/material/styles";
import logo from "../assets/emsa-logo.png";
import useCustomTheme from "./Theme";

export default function SignUp() {
  const [signupSuccess, setSignupSuccess] = useState(false);
  const [signupError, setSignupError] = useState("");

  const HandleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const navigate = useNavigate();
    const data = new FormData(event.currentTarget);

    const signUpData = {
      nickname: data.get("nickname"),
      email: data.get("email"),
      password: data.get("password"),
    };

    try {
      const response = await axios.post(
        "http://localhost:8000/signup",
        signUpData,
      );
      console.log(response);
      if (response.status === 201) {
        setSignupSuccess(true);
        setTimeout(() => navigate("/signin"), 3000);
      }
    } catch (error) {
      console.error("Error during sign up", error);
      setSignupError("Failed to sign up. Please try again.");
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
          {/* Logo */}
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
            Sign up
          </Typography>

          {signupSuccess && (
            <Alert severity="success">
              Signup successful! Redirecting to login...
            </Alert>
          )}
          {signupError && <Alert severity="error">{signupError}</Alert>}

          <Box
            component="form"
            noValidate
            onSubmit={HandleSubmit}
            sx={{ mt: 3 }}
          >
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  id="nickname"
                  label="Nickname"
                  name="nickname"
                  autoComplete="nickname"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  id="email"
                  label="Email Address"
                  name="email"
                  autoComplete="email"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="password"
                  label="Password"
                  type="password"
                  id="password"
                  autoComplete="new-password"
                />
              </Grid>
            </Grid>
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
            >
              Sign Up
            </Button>
            <Grid container justifyContent="flex-end">
              <Grid item>
                <Link href="/signin" variant="body2">
                  Already have an account? Sign in
                </Link>
              </Grid>
            </Grid>
          </Box>
        </Box>
      </Container>
    </ThemeProvider>
  );
}
