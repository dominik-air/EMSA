import React, { useState } from "react";
import { Box, Button, AppBar, Toolbar, InputBase } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import MemeGrid from "./MemeGrid";
import { styled, alpha } from "@mui/material/styles";

interface Meme {
  type: "image" | "link";
  url: string;
  tags: string[];
}

interface ManageMemesProps {
  memes: Meme[];
}

const Search = styled("div")(({ theme }) => ({
  position: "relative",
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  "&:hover": {
    backgroundColor: alpha(theme.palette.common.white, 0.25),
  },
  marginLeft: 0,
  width: "100%",
  [theme.breakpoints.up("sm")]: {
    marginLeft: theme.spacing(1),
    width: "auto",
  },
}));

const SearchIconWrapper = styled("div")(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: "100%",
  position: "absolute",
  pointerEvents: "none",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: "inherit",
  "& .MuiInputBase-input": {
    padding: theme.spacing(1, 1, 1, 0),
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create("width"),
    width: "100%",
    [theme.breakpoints.up("sm")]: {
      width: "12ch",
      "&:focus": {
        width: "20ch",
      },
    },
  },
}));

const ManageMemes: React.FC<ManageMemesProps> = ({ memes }) => {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredMemes = memes.filter((meme) =>
    meme.tags.some((tag) =>
      tag.toLowerCase().includes(searchTerm.toLowerCase()),
    ),
  );

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" color="default">
        <Toolbar>
          <Search>
            <SearchIconWrapper>
              <SearchIcon />
            </SearchIconWrapper>
            <StyledInputBase
              placeholder="Search Memes"
              inputProps={{ "aria-label": "search" }}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </Search>
          <Button variant="contained" sx={{ ml: 2 }}>
            Add New Meme
          </Button>
        </Toolbar>
      </AppBar>
      <MemeGrid memes={filteredMemes} />
    </Box>
  );
};

export default ManageMemes;
