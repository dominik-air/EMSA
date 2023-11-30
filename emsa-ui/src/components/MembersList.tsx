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

  const handleAddNewMember = () => {
    console.log(`Opening add new member pop up!`);
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
            Add member to group
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
    </>
  );
};

export default MembersList;
