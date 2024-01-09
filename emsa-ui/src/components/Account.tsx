import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
} from "@mui/material";

interface AccountDetails {
  name: string;
  mail: string;
}

interface AccountUpdate {
  name: string;
  password_hash: string;
}

interface AccountStatistics {
  numberOfFriends: number;
  numberOfGroups: number;
}

const AccountComponent: React.FC = () => {
  const API_URL = import.meta.env.VITE_API_URL;
  const [details, setDetails] = useState<AccountDetails | null>(null);
  const [updateDetails, setUpdateDetails] = useState<AccountUpdate>({
    name: "",
    password_hash: "",
  });
  const [statistics, setStatistics] = useState<AccountStatistics>({
    numberOfFriends: 0,
    numberOfGroups: 0,
  });
  const headers = {
    Authorization: `Bearer ${localStorage.getItem("sessionToken")}`,
  };

  useEffect(() => {
    axios
      .get<AccountDetails>(`${API_URL}/user_details`, { headers: headers })
      .then((response) => {
        setDetails(response.data);
      });
  }, []);

  const handleUpdateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUpdateDetails({ ...updateDetails, [e.target.name]: e.target.value });
  };

  const fetchAccountDetails = async (): Promise<AccountDetails | null> => {
    try {
      const response = await axios.get<AccountDetails>(
        `${API_URL}/user_details`,
        { headers: headers },
      );
      return response.data;
    } catch (error) {
      console.error("Error while fetching friends count:", error);
      return null;
    }
  };

  const fetchFriendsCount = async (): Promise<number> => {
    try {
      const response = await axios.get<string[]>(`${API_URL}/user_friends`, {
        headers: headers,
      });
      return response.data.length;
    } catch (error) {
      console.error("Error while fetching friends count:", error);
      return 0;
    }
  };

  const fetchGroupsCount = async (): Promise<number> => {
    try {
      const response = await axios.get<[]>(`${API_URL}/user_groups`, {
        headers: headers,
      });
      return response.data.length;
    } catch (error) {
      console.error("Error while fetching groups count:", error);
      return 0;
    }
  };

  const loadStatistics = async () => {
    const friendsCount = await fetchFriendsCount();
    const groupsCount = await fetchGroupsCount();
    setStatistics({
      numberOfFriends: friendsCount,
      numberOfGroups: groupsCount,
    });
  };

  useEffect(() => {
    fetchAccountDetails();
    loadStatistics();
    const interval = setInterval(() => {
      fetchAccountDetails();
      loadStatistics();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const handleUpdateSubmit = () => {
    // TODO: finish after #76 is fixed
    console.log(updateDetails);
    axios
      .put(`${API_URL}/update_account`, updateDetails, { headers: headers })
      .then((response) => {
        console.log(response);
        alert("Account details updated successfully!");
      })
      .catch((error) => {
        console.error(error);
        alert("Failed to update account details.");
      });
  };

  return (
    <Box
      sx={{ display: "flex", justifyContent: "space-between", gap: 2, p: 3 }}
    >
      {/* Left side - Account details && Statistics */}
      <Paper elevation={3} sx={{ width: "100%", p: 2 }}>
        <Typography variant="h6" sx={{ textAlign: "center", mb: 2 }}>
          Account Details
        </Typography>
        {details && (
          <TableContainer component={Paper}>
            <Table>
              <TableBody>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell align="right">{details.name}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Email</TableCell>
                  <TableCell align="right">{details.mail}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        )}
        <Typography variant="h6" sx={{ textAlign: "center", mb: 2, mt: 2 }}>
          Statistics
        </Typography>
        <TableContainer component={Paper}>
          <Table>
            <TableBody>
              <TableRow>
                <TableCell>Number of Friends</TableCell>
                <TableCell align="right">
                  {statistics.numberOfFriends}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Number of Groups</TableCell>
                <TableCell align="right">{statistics.numberOfGroups}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Right side - Account Update */}
      <Paper elevation={3} sx={{ width: "100%", p: 2 }}>
        <Typography variant="h6" sx={{ textAlign: "center", mb: 2 }}>
          Update Account
        </Typography>
        <TextField
          label="New Name"
          name="name"
          value={updateDetails.name}
          onChange={handleUpdateChange}
          fullWidth
          margin="normal"
        />
        <TextField
          label="New Password"
          name="password_hash"
          type="password"
          value={updateDetails.password_hash}
          onChange={handleUpdateChange}
          fullWidth
          margin="normal"
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleUpdateSubmit}
          fullWidth
        >
          Update
        </Button>
      </Paper>
    </Box>
  );
};

export default AccountComponent;
