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

interface Group {
  id: number;
  name: string;
  owner_mail: string;
}

interface GroupListProps {
  userEmail: string;
  onGroupClick: (group: Group) => void;
}

const GroupList: React.FC<GroupListProps> = ({ userEmail, onGroupClick }) => {
  const API_URL = import.meta.env.VITE_API_URL;
  const [open, setOpen] = useState(false);
  const [groups, setGroups] = useState<Group[]>([]);
  const [newGroupName, setNewGroupName] = useState("");
  const headers = {
    Authorization: `Bearer ${localStorage.getItem("sessionToken")}`,
  };

  useEffect(() => {
    fetchUserGroups();
    const interval = setInterval(() => {
      fetchUserGroups();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const fetchUserGroups = () => {
    axios
      .get<Group[]>(`${API_URL}/user_groups`, { headers: headers })
      .then((response) => {
        console.log(response);
        setGroups(response.data);
      })
      .catch((error) => {
        console.error("Error fetching user groups:", error);
        setGroups([{ id: -1, name: "no groups", owner_mail: userEmail }]);
      });
  };

  const handleAddNewGroup = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleGroupClickInternal = (group: Group) => {
    onGroupClick(group);
  };

  const handleCreateGroup = () => {
    const body = {
      owner_mail: userEmail,
      name: newGroupName,
    };

    axios
      .post(`${API_URL}/create_group`, body, { headers: headers })
      .then((response) => {
        console.log("Group created:", response.data);
        setOpen(false);
        fetchUserGroups();
      })
      .catch((error) => {
        console.error("Error creating group:", error);
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
                sx={{ textAlign: "center", justifyContent: "center", border: 1, borderRadius: 2 }}
                onClick={() => handleGroupClickInternal(group)}
              >
                {group.name}
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
