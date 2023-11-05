import { ThemeProvider } from "@mui/material/styles";
import Button from "@mui/material/Button";
import { Box, Container, CssBaseline, Typography } from "@mui/material";
import theme from "./Theme";
import { useAuth } from "./useAuth";

export default function HomePage() {
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <ThemeProvider theme={theme}>
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
          <Typography component="h1" variant="h5">
            Hi!
          </Typography>
          <Button
            type="button"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            onClick={handleLogout}
          >
            Logout
          </Button>
        </Box>
      </Container>
    </ThemeProvider>
  );
}
