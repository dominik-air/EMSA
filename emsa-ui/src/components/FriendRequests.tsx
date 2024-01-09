import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Box,
  Button,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Paper,
  Table,
  TableRow,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
} from "@mui/material";

interface Friend {
  name: string;
  mail: string;
}

interface FriendRequest {
  name: string;
  mail: string;
}

const FriendRequests: React.FC = () => {
  const API_URL = import.meta.env.VITE_API_URL;
  const [friends, setFriends] = useState<Friend[]>([]);
  const [sentFriendRequests, setSentFriendRequests] = useState<FriendRequest[]>(
    [],
  );
  const [pendingFriendRequests, setPendingFriendRequests] = useState<
    FriendRequest[]
  >([]);
  const [newFriendEmail, setNewFriendEmail] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const headers = {
    Authorization: `Bearer ${localStorage.getItem("sessionToken")}`,
  };

  const fetchPendingFriendRequests = async () => {
    try {
      const friendRequestsResponse = await axios.get<FriendRequest[]>(
        `${API_URL}/pending_friend_requests`,
        { headers: headers },
      );
      setPendingFriendRequests(friendRequestsResponse.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const fetchSentFriendRequests = async () => {
    try {
      const friendRequestsResponse = await axios.get<FriendRequest[]>(
        `${API_URL}/sent_friend_requests`,
        { headers: headers },
      );
      setSentFriendRequests(friendRequestsResponse.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

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
    fetchPendingFriendRequests();
    fetchSentFriendRequests();
    fetchFriends();
    const interval = setInterval(() => {
      fetchPendingFriendRequests();
      fetchSentFriendRequests();
      fetchFriends();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const handleSendRequest = async () => {
    try {
      await axios.post(
        `${API_URL}/create_friend_request`,
        { friend_mail: newFriendEmail },
        { headers: headers },
      );
      setIsDialogOpen(false);
      setNewFriendEmail("");
      fetchSentFriendRequests();
    } catch (error) {
      console.error("Error sending friend request:", error);
    }
  };

  const handleOpenFriendRequestDialog = async () => {
    setIsDialogOpen(true);
    setNewFriendEmail("");
  };

  const handleAcceptRequest = async (friendMail: string) => {
    console.log(`called with ${friendMail}`);
    try {
      await axios.post(
        `${API_URL}/add_friend`,
        { friend_mail: friendMail },
        { headers: headers },
      );
      setPendingFriendRequests((prev) =>
        prev.filter((f) => f.mail !== friendMail),
      );
      fetchFriends();
    } catch (error) {
      console.error("Error accepting friend request:", error);
    }
  };

  const handleDeclineRequest = async (friendMail: string) => {
    try {
      await axios.delete(
        `${API_URL}/decline_friend_request/${encodeURIComponent(friendMail)}`,
        { headers: headers },
      );
      setPendingFriendRequests((prev) =>
        prev.filter((f) => f.mail !== friendMail),
      );
    } catch (error) {
      console.error("Error declining friend request:", error);
    }
  };

  const handleRemoveRequest = async (friendMail: string) => {
    try {
      await axios.delete(
        `${API_URL}/remove_friend_request/${encodeURIComponent(friendMail)}`,
        { headers: headers },
      );
      setSentFriendRequests((prev) =>
        prev.filter((f) => f.mail !== friendMail),
      );
    } catch (error) {
      console.error("Error removing friend request:", error);
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
      <Paper elevation={3} sx={{ width: "70%", p: 3 }}>
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

        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            gap: 2,
            p: 3,
          }}
        >
          <TableContainer component={Paper}>
            <Typography variant="h6" sx={{ textAlign: "center", mb: 2 }}>
              Pending
            </Typography>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {pendingFriendRequests.length > 0 ? (
                  pendingFriendRequests.map((request) => (
                    <TableRow key={request.name}>
                      <TableCell>{request.name}</TableCell>
                      <TableCell>{request.mail}</TableCell>
                      <TableCell>
                        <Box sx={{ display: "flex", justifyContent: "start" }}>
                          <Button
                            variant="contained"
                            color="primary"
                            onClick={() => handleAcceptRequest(request.mail)}
                          >
                            Accept
                          </Button>
                          <Button
                            variant="contained"
                            color="secondary"
                            sx={{ ml: 1 }}
                            onClick={() => handleDeclineRequest(request.mail)}
                          >
                            Decline
                          </Button>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={3} align="center">
                      No requests
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>

          <TableContainer component={Paper}>
            <Typography variant="h6" sx={{ textAlign: "center", mb: 2 }}>
              Sent
            </Typography>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sentFriendRequests.length > 0 ? (
                  sentFriendRequests.map((request) => (
                    <TableRow key={request.name}>
                      <TableCell>{request.name}</TableCell>
                      <TableCell>{request.mail}</TableCell>
                      <TableCell>
                        <Button
                          variant="contained"
                          color="secondary"
                          onClick={() => handleRemoveRequest(request.mail)}
                        >
                          Remove
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={3} align="center">
                      No requests
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </Paper>
      {/* Right side - Friends List */}
      <Paper elevation={3} sx={{ width: "30%", p: 2 }}>
        <Typography variant="h6" sx={{ textAlign: "center", mb: 2 }}>
          My Friends
        </Typography>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {friends.length > 0 ? (
                friends.map((friend) => (
                  <TableRow key={friend.name}>
                    <TableCell>{friend.name}</TableCell>
                    <TableCell>{friend.mail}</TableCell>
                    <TableCell>
                      <Button
                        variant="contained"
                        color="secondary"
                        onClick={() => handleRemoveFriend(friend.mail)}
                      >
                        Remove
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={3} align="center">
                    No friends
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
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
