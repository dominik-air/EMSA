import { useState, useEffect } from "react";
import axios from "axios";
import {
  Box,
  Button,
  AppBar,
  Toolbar,
  InputBase,
  Typography,
} from "@mui/material";
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
import { FilePond, registerPlugin } from "react-filepond";
import "filepond/dist/filepond.min.css";
import "filepond-plugin-image-preview/dist/filepond-plugin-image-preview.css";
import FilePondPluginImagePreview from "filepond-plugin-image-preview";
import FilePondPluginFileValidateType from "filepond-plugin-file-validate-type";
import FilePondPluginFileEncode from "filepond-plugin-file-encode";
import { FilePondFile } from "filepond";

registerPlugin(
  FilePondPluginImagePreview,
  FilePondPluginFileValidateType,
  FilePondPluginFileEncode,
);
interface Meme {
  type: "image" | "link";
  url: string;
  tags: string[];
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

interface ManageMemesProps {
  groupId: number;
  groupName: string;
}

interface AddLinkRequest {
  group_id: number;
  link: string;
  name: string;
  tags: string[];
}

interface MediaInfo {
  id: number;
  group_id: number;
  is_image: boolean;
  image_path: string;
  link: string;
  name: string;
  tags: string[];
}

const ManageMemes: React.FC<ManageMemesProps> = ({ groupId, groupName }) => {
  const API_URL = import.meta.env.VITE_API_URL;
  const [memes, setMemes] = useState<Meme[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [memeSource, setMemeSource] = useState<string>("");
  const [mediaName, setMediaName] = useState<string>("");
  const [file, setFile] = useState<FilePondFile | null>(null);
  const [tags, setTags] = useState<string>("");
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const headers = {
    Authorization: `Bearer ${localStorage.getItem("sessionToken")}`,
  };

  const MediaInfoToMeme = (info: MediaInfo): Meme => {
    return {
      type: info.is_image ? "image" : "link",
      url: info.is_image ? info.image_path : info.link,
      tags: info.tags,
    };
  };

  const fetchMemes = async () => {
    try {
      const response = await axios.get<MediaInfo[]>(
        `${API_URL}/group_content/${groupId}`,
        {
          params: { search_term: searchTerm },
          headers: headers,
        },
      );
      setMemes(response.data.reverse().map((info) => MediaInfoToMeme(info)));
    } catch (error) {
      console.error("Error fetching memes:", error);
    }
  };

  useEffect(() => {
    fetchMemes();
  }, [searchTerm, groupId, API_URL]);

  const handleDialogOpen = () => {
    setIsDialogOpen(true);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setMediaName("");
    setMemeSource("");
    setTags("");
  };

  const handleFileEncode = (file: FilePondFile) => {
    setMediaName(file.filename.split(".")[0]);
    setFile(file);
  };

  const sendMemeSource = async () => {
    const linkData: AddLinkRequest = {
      group_id: groupId,
      link: memeSource,
      name: mediaName,
      tags: tags.split(" "),
    };
    try {
      const response = await axios.post<MediaInfo>(
        `${API_URL}/add_link`,
        linkData,
        { headers: headers },
      );
      console.log(response.data);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error("Error:", error.response?.data || error.message);
      } else {
        console.error("Unexpected error:", error);
      }
    }
  };

  const sendMemeImage = async () => {
    if (!file) {
      return;
    }
    const form = new FormData();
    form.append("group_id", String(groupId));
    form.append("name", mediaName);
    tags.trim().split(" ").forEach((tag) => {
      form.append(`tags`, tag);
    });
    form.append("image", file.file, file.filename);
    const headers = {
      "Content-Type": "multipart/form-data",
      Authorization: `Bearer ${localStorage.getItem("sessionToken")}`,
    };
    try {
      await axios.post<MediaInfo>(
        `${API_URL}/add_image`,
        form,
        { headers: headers },
      );
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error("Error:", error);
      } else {
        console.error("Unexpected error:", error);
      }
    }
  };

  const handleSendMedia = async () => {
    if (file) {
      await sendMemeImage();
    } else if (memeSource) {
      await sendMemeSource();
    } else {
      // TODO: handle empty inputs in the dialog
      console.log("No media!");
    }
    await fetchMemes();
    handleDialogClose();
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography
        variant="h6"
        sx={{ flexGrow: 1, textAlign: "center", margin: 2 }}
      >
        {groupName}
      </Typography>
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
            value={mediaName}
            onChange={(e) => setMediaName(e.target.value)}
          />
          <TextField
            margin="dense"
            id="source"
            label="Source"
            type="text"
            fullWidth
            variant="standard"
            value={memeSource}
            onChange={(e) => setMemeSource(e.target.value)}
          />
          <TextField
            margin="dense"
            id="tags"
            label="Tags"
            type="text"
            fullWidth
            variant="standard"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
          />
          <FilePond
            allowMultiple={false}
            maxFiles={1}
            name="file"
            acceptedFileTypes={["image/*"]}
            labelIdle='Drag & Drop your image or <span class="filepond--label-action">Browse</span>'
            onaddfile={(error, file) => {
              if (error) {
                console.error("Error while uploding file:", error);
              } else {
                handleFileEncode(file);
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button variant="contained" onClick={handleDialogClose}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleSendMedia}>
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ManageMemes;
