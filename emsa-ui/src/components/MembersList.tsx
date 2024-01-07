import React, { useState, useEffect } from "react";
import axios from "axios";
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
  Checkbox,
  FormGroup,
  FormControlLabel,
} from "@mui/material";

interface Member {
  name: string;
  mail: string;
}

interface Friend {
  name: string;
  mail: string;
}

interface MembersListProps {
  groupId: number;
}

const MembersList: React.FC<MembersListProps> = ({ groupId }) => {
  const API_URL = import.meta.env.VITE_API_URL;
  const [open, setOpen] = useState(false);
  const [selectedMember, setSelectedMember] = useState<string | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [friends, setFriends] = useState<Friend[]>([]);
  const [addMemberDialogOpen, setAddMemberDialogOpen] = useState(false);
  const headers = {
    Authorization: `Bearer ${localStorage.getItem("sessionToken")}`,
  };

  useEffect(() => {
    const fetchMembers = async () => {
      const response = await axios.get<Member[]>(
        `${API_URL}/group_members/${groupId}`,
        { headers: headers },
      );
      setMembers(response.data);
    };

    const fetchFriends = async () => {
      const response = await axios.get<Friend[]>(`${API_URL}/user_friends`, {
        headers: headers,
      });
      setFriends(response.data);
    };

    fetchMembers();
    fetchFriends();
  }, [API_URL, groupId]);

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
              onClick={() => handleClickOpen(member.name)}
            >
              {member.name}
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
                label={friend.name}
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
