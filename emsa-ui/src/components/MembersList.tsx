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
  isOwner: boolean;
}

const MembersList: React.FC<MembersListProps> = ({ groupId, isOwner }) => {
  const API_URL = import.meta.env.VITE_API_URL;
  const [open, setOpen] = useState(false);
  const [selectedMember, setSelectedMember] = useState<Member | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [friends, setFriends] = useState<Friend[]>([]);
  const [selectedFriends, setSelectedFriends] = useState<Friend[]>([]);
  const [addMemberDialogOpen, setAddMemberDialogOpen] = useState(false);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const headers = {
    Authorization: `Bearer ${localStorage.getItem("sessionToken")}`,
  };

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

  useEffect(() => {
    fetchMembers();
    fetchFriends();
  }, [API_URL, groupId]);

  const handleAddNewMember = () => {
    setAddMemberDialogOpen(true);
  };

  const handleCloseAddMemberDialog = () => {
    setAddMemberDialogOpen(false);
  };

  const handleClickOpen = (member: Member) => {
    setSelectedMember(member);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleSelectFriend = (friend: Friend) => {
    setSelectedFriends((prevSelected) => {
      if (prevSelected.includes(friend)) {
        return prevSelected.filter((f) => f !== friend);
      } else {
        return [...prevSelected, friend];
      }
    });
  };

  const addFriendsToGroup = async () => {
    try {
      const response = await axios.post(
        `${API_URL}/add_group_members/${groupId}`,
        { members: selectedFriends.map((f) => f.mail) },
        { headers: headers },
      );
      console.log(response);
      fetchMembers();
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handleAddFriendsToGroup = async () => {
    await addFriendsToGroup();
    handleCloseAddMemberDialog();
  };

  const handleRemoveMember = async (memberMail: string) => {
    console.log(
      `${API_URL}/remove_member/${groupId}/${encodeURIComponent(memberMail)}`,
    );
    try {
      await axios.delete(
        `${API_URL}/remove_member/${groupId}/${encodeURIComponent(memberMail)}`,
        {
          headers: headers,
        },
      );
      setMembers((prev) => prev.filter((m) => m.mail !== memberMail));
    } catch (error) {
      console.error(
        `Error while removing member ${memberMail} from group ${groupId}:`,
        error,
      );
    }
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
            sx={{
              justifyContent: "center",
              display: "flex",
              position: "relative",
              mb: 2,
            }}
            onMouseEnter={() => setHoveredIndex(index)}
            onMouseLeave={() => setHoveredIndex(null)}
          >
            <ListItemButton
              sx={{
                textAlign: "center",
                justifyContent: "center",
                border: 1,
                borderRadius: 2,
                width: "60%",
                mr: 1,
              }}
              onClick={() => handleClickOpen(member)}
            >
              {member.name}
            </ListItemButton>
            {isOwner && hoveredIndex === index && (
              <Button
                variant="contained"
                color="secondary"
                sx={{
                  textAlign: "center",
                  justifyContent: "center",
                  border: 1,
                  borderRadius: 2,
                  width: "39%",
                  ml: 1,
                }}
                onClick={() => handleRemoveMember(member.mail)}
              >
                Remove
              </Button>
            )}
          </ListItem>
        ))}
      </List>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Member Details</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Details for {selectedMember?.name}.
          </DialogContentText>
          <DialogContentText>Email: {selectedMember?.mail}.</DialogContentText>
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
                control={
                  <Checkbox
                    onChange={() => handleSelectFriend(friend)}
                    checked={selectedFriends.includes(friend)}
                  />
                }
                label={friend.name}
              />
            ))}
          </FormGroup>
        </DialogContent>
        <DialogActions>
          <Button variant="contained" onClick={handleCloseAddMemberDialog}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleAddFriendsToGroup}>
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default MembersList;
