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

const GroupList: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [groups, setGroups] = useState<string[]>([]);
  const [newGroupName, setNewGroupName] = useState("");
  const [email] = useState("email@example.com");

  useEffect(() => {
    fetchUserGroups();
  });

  const fetchUserGroups = () => {
    axios
      .get(`http://localhost:8000/user_groups/${email}`)
      .then((response) => {
        setGroups(response.data.groups);
      })
      .catch((error) => {
        console.error(error);
        setGroups(["no groups!"]);
      });
  };

  const handleAddNewGroup = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleGroupClick = (group: string) => {
    console.log(`Redirecting to the ${group}'s Homepage!`);
  };

  const handleCreateGroup = () => {
    axios
      .post("http://localhost:8000/user_groups", {
        email: email,
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
                onClick={() => handleGroupClick(group)}
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
