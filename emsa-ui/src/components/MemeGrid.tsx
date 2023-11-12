import React from "react";
import Grid from "@mui/material/Grid";
import MemeContainer from "./MemeContainer";
import { ThemeProvider } from "@mui/material/styles";
import theme from "./Theme";

interface Meme {
  type: "image" | "link";
  url: string;
  tags: string[];
}

interface MemeGridProps {
  memes: Meme[];
}

const MemeGrid: React.FC<MemeGridProps> = ({ memes }) => {
  const gridStyle = {
    maxHeight: "800px",
    overflowY: "scroll",
    padding: "8px",
  };
  return (
    <ThemeProvider theme={theme}>
      <div style={gridStyle}>
        <Grid container spacing={4}>
          {memes.map((meme, index) => (
            <Grid item xs={12} sm={8} md={4} key={index}>
              <MemeContainer meme={meme} />
            </Grid>
          ))}
        </Grid>
      </div>
    </ThemeProvider>
  );
};

export default MemeGrid;
