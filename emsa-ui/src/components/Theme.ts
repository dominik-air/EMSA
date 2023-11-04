import { createTheme } from "@mui/material/styles";
import purple from "@mui/material/colors/purple";
import orange from "@mui/material/colors/orange";
import grey from "@mui/material/colors/grey";

// TODO: a trained ui engineer should adjust those values
// source: https://mui.com/material-ui/customization/color/

const theme = createTheme({
  palette: {
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

export default theme;
