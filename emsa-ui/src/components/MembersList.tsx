import React, { useState } from "react";
import {
  List,
  ListItem,
  Button,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  ListItemButton,
} from "@mui/material";

import { Checkbox, FormGroup, FormControlLabel } from "@mui/material";

const MembersList: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [selectedMember, setSelectedMember] = useState<string | null>(null);
  const members = [
    "member 1",
    "member 2",
    "member 3",
    "member 4",
    "member 5",
    "member 6",
  ];
  const friends = ["friend 1", "friend 2", "friend 3", "friend 4"];

  const [addMemberDialogOpen, setAddMemberDialogOpen] = useState(false);

  const handleAddNewMember = () => {
    setAddMemberDialogOpen(true);
  };

  const handleCloseAddMemberDialog = () => {
    setAddMemberDialogOpen(false);
  };

  const handleClickOpen = (member: string) => {
    setSelectedMember(member);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  return (
    <>
      <List>
        <ListItem>
          <Typography
            variant="h6"
            component="div"
            sx={{ width: "100%", textAlign: "center" }}
          >
            Members
          </Typography>
        </ListItem>
        <ListItem>
          <Button
            variant="contained"
            fullWidth
            onClick={() => handleAddNewMember()}
          >
            Add friends to group
          </Button>
        </ListItem>
        {members.map((member, index) => (
          <ListItem
            key={index}
            sx={{ justifyContent: "center", display: "flex" }}
          >
            <ListItemButton
              sx={{ textAlign: "center", justifyContent: "center" }}
              onClick={() => handleClickOpen(member)}
            >
              {member}
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Member Details</DialogTitle>
        <DialogContent>
          <DialogContentText>Details for {selectedMember}.</DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
      <Dialog open={addMemberDialogOpen} onClose={handleCloseAddMemberDialog}>
        <DialogTitle>Add friend to group</DialogTitle>
        <DialogContent>
          <FormGroup>
            {friends.map((friend, index) => (
              <FormControlLabel
                key={index}
                control={<Checkbox />}
                label={friend}
              />
            ))}
          </FormGroup>
        </DialogContent>
        <DialogActions>
          <Button variant="contained" onClick={handleCloseAddMemberDialog}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleCloseAddMemberDialog}>
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default MembersList;
