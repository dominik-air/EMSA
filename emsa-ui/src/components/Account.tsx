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
  password: string;
}

interface AccountStatistics {
  numberOfFriends: number;
  numberOfGroups: number;
}

const AccountComponent: React.FC = () => {
  const [details, setDetails] = useState<AccountDetails>({
    name: "Dominik",
    mail: "dzurek@comarch.pl",
  });
  const [updateDetails, setUpdateDetails] = useState<AccountUpdate>({
    name: "",
    password: "",
  });
  const [statistics, setStatistics] = useState<AccountStatistics>({
    numberOfFriends: 3,
    numberOfGroups: 1,
  });

  useEffect(() => {
    // Fetch account details and statistics
    axios.get("/api/account/details").then((response) => {
      setDetails(response.data);
    });

    axios.get("/api/account/statistics").then((response) => {
      setStatistics(response.data);
    });
  }, []);

  const handleUpdateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUpdateDetails({ ...updateDetails, [e.target.name]: e.target.value });
  };

  const handleUpdateSubmit = () => {
    axios
      .put("/api/account/update", updateDetails)
      .then((response) => {
        // Handle successful update
        console.log(response);
        alert("Account details updated successfully!");
      })
      .catch((error) => {
        // Handle error
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
          name="password"
          type="password"
          value={updateDetails.password}
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
