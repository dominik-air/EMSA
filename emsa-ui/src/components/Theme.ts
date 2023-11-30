import React from "react";
import { useMediaQuery } from "@mui/material";
import { createTheme } from "@mui/material/styles";
import purple from "@mui/material/colors/purple";
import orange from "@mui/material/colors/orange";
import grey from "@mui/material/colors/grey";

const lightTheme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: purple[500],
      contrastText: grey[50],
    },
    secondary: {
      main: orange[400],
      contrastText: grey[900],
    },
    background: {
      default: grey[50],
      paper: grey[100],
    },
    text: {
      primary: grey[900],
      secondary: grey[700],
    },
  },
  typography: {
    fontFamily: '"Comic Neue", cursive',
    button: {
      textTransform: "none",
    },
  },
});

const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: purple[500],
      contrastText: grey[200],
    },
    secondary: {
      main: orange[500],
      contrastText: grey[300],
    },
    background: {
      default: grey[900],
      paper: grey[800],
    },
    text: {
      primary: grey[50],
      secondary: grey[300],
    },
  },
  typography: {
    fontFamily: '"Comic Neue", cursive',
    button: {
      textTransform: "none",
    },
  },
});

const useCustomTheme = () => {
  const prefersDarkMode = useMediaQuery("(prefers-color-scheme: dark)");

  return React.useMemo(
    () => createTheme(prefersDarkMode ? darkTheme : lightTheme),
    [prefersDarkMode],
  );
};

export default useCustomTheme;
