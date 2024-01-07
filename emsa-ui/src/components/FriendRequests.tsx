import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Box,
  List,
  ListItem,
  Button,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Paper,
} from "@mui/material";

interface Friend {
  name: string;
  mail: string;
}

interface FriendRequest {
  name: string;
  mail: string;
}

interface FriendRequestsProps {
  userEmail: string;
}

const FriendRequests: React.FC<FriendRequestsProps> = ({ userEmail }) => {
  const API_URL = import.meta.env.VITE_API_URL;
  const [friends, setFriends] = useState<Friend[]>([]);
  const [friendRequests, setFriendRequests] = useState<FriendRequest[]>([]);
  const [newFriendEmail, setNewFriendEmail] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const headers = {
    Authorization: `Bearer ${localStorage.getItem("sessionToken")}`,
  };

  const fetchFriendRequests = async () => {
    try {
      const friendRequestsResponse = await axios.get<FriendRequest[]>(
        `${API_URL}/pending_friend_requests`,
        { headers: headers },
      );
      setFriendRequests(friendRequestsResponse.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    if (userEmail) {
      fetchFriendRequests();
    }
  }, []);

  const fetchFriends = async () => {
    try {
      const friendsResponse = await axios.get<Friend[]>(
        `${API_URL}/user_friends`,
        { headers: headers },
      );
      setFriends(friendsResponse.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    if (userEmail) {
      fetchFriends();
    }
  }, []);

  const handleSendRequest = async () => {
    try {
      await axios.post(
        `${API_URL}/create_friend_request`,
        {
          friend_mail: newFriendEmail,
        },
        { headers: headers },
      );
      setIsDialogOpen(false);
      setNewFriendEmail("");
    } catch (error) {
      console.error("Error sending friend request:", error);
    }
  };

  const handleOpenFriendRequestDialog = async () => {
    setIsDialogOpen(true);
    setNewFriendEmail("");
  };

  const handleAcceptRequest = async (friendMail: string) => {
    console.log(`callled with ${friendMail}`);
    try {
      await axios.post(`${API_URL}/add_friend`, { friend_mail: friendMail }, {headers: headers});
      setFriendRequests((prev) => prev.filter((f) => f.mail !== friendMail));
    } catch (error) {
      console.error("Error accepting friend request:", error);
    }
  };

  const handleDeclineRequest = async (friendMail: string) => {
    try {
      await axios.delete(`${API_URL}/decline_friend_request/${123}`)
      setFriendRequests((prev) => prev.filter((f) => f.mail !== friendMail));
    } catch (error) {
      console.error("Error declining friend request:", error);
    }
  };

  const handleRemoveFriend = async (friendEmail: string) => {
    try {
      await axios.delete(
        `${API_URL}/remove_friend/${encodeURIComponent(friendEmail)}`,
        { headers: headers },
      );
      setFriends((prevFriends) =>
        prevFriends.filter((friend) => friend.mail !== friendEmail),
      );
    } catch (error) {
      console.error("Error removing friend:", error);
    }
  };

  return (
    <Box
      sx={{ display: "flex", justifyContent: "space-between", gap: 2, p: 3 }}
    >
      {/* Left side - Friend Requests */}
      <Paper elevation={3} sx={{ width: "100%", p: 2 }}>
        <Typography variant="h6" sx={{ textAlign: "center", mb: 2 }}>
          Friend Requests
        </Typography>
        <Box sx={{ justifyContent: "center", display: "flex" }}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleOpenFriendRequestDialog}
            sx={{ mb: 2 }}
          >
            Send Friend Request
          </Button>
        </Box>

        <List>
          {friendRequests.length > 0 ? (
            friendRequests.map((request) => (
              <ListItem
                key={request.name}
                sx={{ justifyContent: "space-between", display: "flex" }}
              >
                <Typography variant="subtitle1">{request.name}</Typography>
                <Typography variant="subtitle1">{request.mail}</Typography>
                <div>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => {
                      handleAcceptRequest(request.mail);
                    }}
                  >
                    Accept
                  </Button>
                  <Button
                    variant="outlined"
                    color="secondary"
                    sx={{ ml: 1 }}
                    onClick={() => {
                      handleDeclineRequest(request.mail);
                    }}
                  >
                    Decline
                  </Button>
                </div>
              </ListItem>
            ))
          ) : (
            <Typography sx={{ textAlign: "center" }}>No requests</Typography>
          )}
        </List>
      </Paper>

      {/* Right side - Friends List */}
      <Paper elevation={3} sx={{ width: "100%", p: 2 }}>
        <Typography variant="h6" sx={{ textAlign: "center", mb: 2 }}>
          My Friends
        </Typography>
        <List>
          {friends.length > 0 ? (
            friends.map((friend) => (
              <ListItem
                key={friend.name}
                sx={{ justifyContent: "space-between", display: "flex" }}
              >
                <Typography variant="subtitle1">{friend.name}</Typography>
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={() => handleRemoveFriend(friend.mail)}
                >
                  Remove
                </Button>
              </ListItem>
            ))
          ) : (
            <Typography sx={{ textAlign: "center" }}>No friends</Typography>
          )}
        </List>
      </Paper>

      {/* Dialog for sending friend requests */}
      <Dialog open={isDialogOpen} onClose={() => setIsDialogOpen(false)}>
        <DialogTitle>Send Friend Request</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="friend-email"
            label="Friend's Email"
            type="email"
            fullWidth
            value={newFriendEmail}
            onChange={(e) => setNewFriendEmail(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSendRequest}>Send Request</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FriendRequests;
