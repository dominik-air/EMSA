import { ThemeProvider } from "@mui/material/styles";
import Button from "@mui/material/Button";
import { Box, Container, CssBaseline, Typography } from "@mui/material";
import theme from "./Theme";
import { useAuth } from "./useAuth";
import MemeGrid from "./MemeGrid";

export default function HomePage() {
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  const memes = [
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "nerd"],
    },
  ];

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
            Your Homepage
          </Typography>
          <MemeGrid memes={memes} />
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
