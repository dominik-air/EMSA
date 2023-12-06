import React from "react";
import Grid from "@mui/material/Grid";
import MemeContainer from "./MemeContainer";

interface Meme {
  type: "image" | "link";
  url: string;
  tags: string[];
}

interface MemeGridProps {
  memes: Meme[];
}

const MemeGrid: React.FC<MemeGridProps> = ({ memes }) => {
  const gridStyle: React.CSSProperties = {
    padding: "20px",
  };
  return (
    <div style={gridStyle}>
      <Grid container spacing={4}>
        {memes.map((meme, index) => (
          <Grid item xs={12} sm={8} md={4} key={index}>
            <MemeContainer meme={meme} />
          </Grid>
        ))}
      </Grid>
    </div>
  );
};

export default MemeGrid;
