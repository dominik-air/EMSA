import React from "react";
import { Card, CardMedia, CardContent, Typography } from "@mui/material";

interface MemeContainerProps {
  meme: {
    type: "image" | "link";
    url: string;
    tags: string[];
  };
}

const MemeContainer: React.FC<MemeContainerProps> = ({ meme }) => {
  return (
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
  );
};

export default MemeContainer;
