import React, { useState, useEffect } from "react";
import {
  List,
  ListItem,
  Button,
  Typography,
  ListItemButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from "@mui/material";
import axios from "axios";

interface GroupListProps {
  userEmail: string;
  onGroupClick: (group: string) => void;
}

const GroupList: React.FC<GroupListProps> = ({ userEmail, onGroupClick }) => {
  const API_URL = import.meta.env.VITE_API_URL;
  const [open, setOpen] = useState(false);
  const [groups, setGroups] = useState<string[]>([]);
  const [newGroupName, setNewGroupName] = useState("");

  useEffect(() => {
    fetchUserGroups();
  }, [userEmail]);

  const fetchUserGroups = () => {
    axios
      .get(`${API_URL}/user_groups/${encodeURIComponent(userEmail)}`)
      .then((response) => {
        setGroups(response.data);
      })
      .catch((error) => {
        console.error("Error fetching user groups:", error);
        setGroups(["no groups!"]);
      });
  };
  

  const handleAddNewGroup = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleGroupClickInternal = (group: string) => {
    onGroupClick(group);
  };

  const handleCreateGroup = () => {
    axios
      .post(`${API_URL}/user_groups`, {
        email: userEmail,
        group_name: newGroupName,
      })
      .then((response) => {
        setGroups(response.data.groups);
        setOpen(false);
      })
      .catch((error) => {
        console.error(error);
      });
  };

  return (
    <>
      <List sx={{ width: "100%", bgcolor: "background.paper" }}>
        <ListItem>
          <Typography
            variant="h6"
            component="div"
            sx={{ width: "100%", textAlign: "center" }}
          >
            My groups
          </Typography>
        </ListItem>
        <ListItem>
          <Button variant="contained" fullWidth onClick={handleAddNewGroup}>
            Create new group
          </Button>
        </ListItem>
        {groups &&
          groups.map((group, index) => (
            <ListItem
              key={index}
              sx={{ justifyContent: "center", display: "flex" }}
            >
              <ListItemButton
                sx={{ textAlign: "center", justifyContent: "center" }}
                onClick={() => handleGroupClickInternal(group)}
              >
                {group}
              </ListItemButton>
            </ListItem>
          ))}
      </List>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Create new group</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="group-name"
            label="Group Name"
            type="text"
            fullWidth
            variant="standard"
            value={newGroupName}
            onChange={(e) => setNewGroupName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button variant="contained" onClick={handleClose}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleCreateGroup}>
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default GroupList;
