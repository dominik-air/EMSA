import { ThemeProvider } from "@mui/material/styles";
import {
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Drawer,
  Button,
  Typography,
} from "@mui/material";
import useCustomTheme from "./Theme";
import { useAuth } from "./useAuth";
import GroupList from "./GroupList";
import MembersList from "./MembersList";
import ManageMemes from "./ManageMemes";
import logo from "../assets/emsa-logo.png";

export default function HomePage() {
  const { logout } = useAuth();
  const drawerWidth = 240;

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
      tags: ["funny", "Radek"],
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
      tags: ["funny", "Igor"],
    },
    {
      type: "image",
      url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg",
      tags: ["funny", "Bartosz"],
    },
    {
      type: "image",
      url: "https://fwcdn.pl/ppo/50/13/55013/449913.2.jpg",
      tags: ["funny", "Dominik"],
    },
  ];

  return (
    <ThemeProvider theme={useCustomTheme()}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, height: 70 }}
      >
        <Toolbar>
          <Box sx={{ flexGrow: 1, display: "flex", alignItems: "center" }}>
            <img
              src={logo}
              alt="EMSA Logo"
              style={{
                width: "70px",
                height: "70px",
                borderRadius: "30%",
                objectFit: "cover",
              }}
            />
          </Box>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Group name
          </Typography>
          <Button color="inherit" onClick={() => handleLogout()}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>
      <Box sx={{ display: "flex" }}>
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            [`& .MuiDrawer-paper`]: {
              width: drawerWidth,
              boxSizing: "border-box",
              bgcolor: "background.paper",
            },
          }}
        >
          <Toolbar />
          <GroupList />
        </Drawer>
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          <ManageMemes memes={memes} />
        </Box>
        <Drawer
          variant="permanent"
          anchor="right"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            [`& .MuiDrawer-paper`]: {
              width: drawerWidth,
              boxSizing: "border-box",
              bgcolor: "background.paper",
            },
          }}
        >
          <Toolbar />
          <MembersList />
        </Drawer>
      </Box>
    </ThemeProvider>
  );
}
