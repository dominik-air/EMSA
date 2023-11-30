import React, { useState } from "react";
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

const GroupList: React.FC = () => {
  const [open, setOpen] = useState(false);
  const groups = ["group 1", "group 2", "group 3", "group 4", "group 5"];

  const handleAddNewGroup = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleGroupClick = (group: string) => {
    console.log(`Redirecting to the ${group}'s Homepage!`);
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
          <Button
            variant="contained"
            fullWidth
            onClick={() => handleAddNewGroup()}
          >
            Create new group
          </Button>
        </ListItem>
        {groups.map((group, index) => (
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
          />
        </DialogContent>
        <DialogActions>
          <Button variant="contained" onClick={handleClose}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleClose}>
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default GroupList;
