import React from "react";
import { Card, CardMedia, CardContent, Typography } from "@mui/material";
import { ThemeProvider } from "@mui/material/styles";
import theme from "./Theme";

interface MemeContainerProps {
  meme: {
    type: "image" | "link";
    url: string;
    tags: string[];
  };
}

const MemeContainer: React.FC<MemeContainerProps> = ({ meme }) => {
  return (
    <ThemeProvider theme={theme}>
      <Card>
        {meme.type === "image" ? (
          <CardMedia
            component="img"
            height="140"
            image={meme.url}
            alt="Meme image"
          />
        ) : (
          <CardContent>
            <Typography variant="body2" color="text.secondary">
              Preview for: {meme.url}
            </Typography>
          </CardContent>
        )}
        <CardContent>
          <Typography variant="body2" color="text.secondary">
            Tags: {meme.tags.join(", ")}
          </Typography>
        </CardContent>
      </Card>
    </ThemeProvider>
  );
};

export default MemeContainer;
