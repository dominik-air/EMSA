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
  id: string;
  name: string;
}

interface FriendRequest {
  id: string;
  name: string;
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

  useEffect(() => {
    const fetchFriendsAndRequests = async () => {
      try {
        const friendsResponse = await axios.get<Friend[]>(
          `${API_URL}/friends/${userEmail}`,
        );
        const friendRequestsResponse = await axios.get<FriendRequest[]>(
          `${API_URL}/friend_requests/${userEmail}`,
        );
        setFriends(friendsResponse.data);
        setFriendRequests(friendRequestsResponse.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchFriendsAndRequests();
  }, [API_URL, userEmail]);

  const handleSendRequest = async () => {
    try {
      await axios.post(`${API_URL}/send_friend_request`, {
        email: newFriendEmail,
      });
      setIsDialogOpen(false);
      setNewFriendEmail("");
    } catch (error) {
      console.error("Error sending friend request:", error);
    }
  };

  const handleAcceptRequest = async (requestId: string) => {
    try {
      await axios.post(`${API_URL}/accept_friend_request`, { id: requestId });
      setFriendRequests((prev) => prev.filter((req) => req.id !== requestId));
    } catch (error) {
      console.error("Error accepting friend request:", error);
    }
  };

  const handleDeclineRequest = async (requestId: string) => {
    try {
      console.log(`Declining request with ID: ${requestId}`);
      setFriendRequests((prev) => prev.filter((req) => req.id !== requestId));
    } catch (error) {
      console.error("Error declining friend request:", error);
    }
  };

  const handleRemoveFriend = async (friendId: string) => {
    try {
      console.log(`Removing friend with ID: ${friendId}`);
      setFriends((prev) => prev.filter((friend) => friend.id !== friendId));
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
        <List>
          {friendRequests.length > 0 ? (
            friendRequests.map((request) => (
              <ListItem
                key={request.id}
                sx={{ justifyContent: "space-between", display: "flex" }}
              >
                <Typography variant="subtitle1">{request.name}</Typography>
                <div>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => {
                      /* handle accept */
                    }}
                  >
                    Accept
                  </Button>
                  <Button
                    variant="outlined"
                    color="secondary"
                    sx={{ ml: 1 }}
                    onClick={() => {
                      /* handle decline */
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
                key={friend.id}
                sx={{ justifyContent: "space-between", display: "flex" }}
              >
                <Typography variant="subtitle1">{friend.name}</Typography>
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={() => {
                    /* handle remove friend */
                  }}
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
