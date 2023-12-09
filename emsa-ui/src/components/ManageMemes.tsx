import { useState, useEffect } from "react";
import axios from "axios";
import { Box, Button, AppBar, Toolbar, InputBase } from "@mui/material";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import MemeGrid from "./MemeGrid";
import { styled, alpha } from "@mui/material/styles";
import { useDropzone } from "react-dropzone";

interface Meme {
  type: "image" | "link";
  url: string;
  tags: string[];
}

interface FileWithPreview extends File {
  preview: string;
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

const ManageMemes = () => {
  const API_URL = import.meta.env.VITE_API_URL;
  const [memes, setMemes] = useState<Meme[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [files, setFiles] = useState<FileWithPreview[]>([]);

  useEffect(() => {
    const fetchMemes = async () => {
      try {
        const response = await axios.get<Meme[]>(
          `${API_URL}/memes/?searchTerm=${encodeURIComponent(searchTerm)}`,
        );
        setMemes(response.data);
      } catch (error) {
        console.error("Error fetching memes:", error);
      }
    };

    if (searchTerm) {
      fetchMemes();
    }
  }, [searchTerm, API_URL]);

  const onDrop = (acceptedFiles: File[]) => {
    setFiles(
      acceptedFiles.map((file) =>
        Object.assign(file, {
          preview: URL.createObjectURL(file),
        }),
      ),
    );
  };
  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  useEffect(() => {
    files.forEach((file) => URL.revokeObjectURL(file.preview));
  }, [files]);

  const handleDialogOpen = () => {
    setIsDialogOpen(true);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setFiles([]);
  };

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
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </Search>
          <Button variant="contained" sx={{ ml: 2 }} onClick={handleDialogOpen}>
            Add New Meme
          </Button>
        </Toolbar>
      </AppBar>
      <MemeGrid memes={memes} />
      <Dialog open={isDialogOpen} onClose={handleDialogClose}>
        <DialogTitle>Add Meme</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Name"
            type="text"
            fullWidth
            variant="standard"
          />
          <TextField
            margin="dense"
            id="source"
            label="Source"
            type="text"
            fullWidth
            variant="standard"
          />
          <Box
            {...getRootProps()}
            sx={{
              border: "1px dashed gray",
              padding: "20px",
              textAlign: "center",
            }}
          >
            <input {...getInputProps()} />
            <p>Drop your file here, or click to select files</p>
            {files.length > 0 && (
              <Box sx={{ mt: 2 }}>
                {files.map((file) => (
                  <div key={file.name}>
                    <img
                      src={file.preview}
                      style={{ width: "100%" }}
                      alt="Preview"
                    />
                  </div>
                ))}
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button variant="contained" onClick={handleDialogClose}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleDialogClose}>
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ManageMemes;
