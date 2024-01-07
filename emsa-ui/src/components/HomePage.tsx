import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  ThemeProvider,
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Drawer,
  Button,
  Tabs,
  Tab,
} from "@mui/material";
import useCustomTheme from "./Theme";
import { useAuth } from "./useAuth";
import GroupList from "./GroupList";
import ManageMemes from "./ManageMemes";
import MembersList from "./MembersList";
import FriendRequests from "./FriendRequests";
import logo from "../assets/emsa-logo.png";

interface Group {
  id: number;
  name: string;
  owner_mail: string;
}

export default function HomePage() {
  const API_URL = import.meta.env.VITE_API_URL;
  const { logout, email } = useAuth();
  const drawerWidth = 240;
  const [selectedTab, setSelectedTab] = useState(0);
  const [activeGroup, setActiveGroup] = useState<Group | null>(null);
  const headers = {
    Authorization: `Bearer ${localStorage.getItem("sessionToken")}`,
  };

  const callLogout = async () => {
    try {
      const response = await axios.post(
        `${API_URL}/logout`,
        {},
        { headers: headers },
      );
      console.log(response.data);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error("Error:", error.response?.data || error.message);
      } else {
        console.error("Unexpected error:", error);
      }
    }
  };

  const handleLogout = async () => {
    await callLogout();
    logout();
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    event.preventDefault();
    setSelectedTab(newValue);
  };

  const handleGroupClick = (group: Group) => {
    setActiveGroup(group);
  };

  const initActiveGroup = async () => {
    axios
      .get(`${API_URL}/user_groups`, { headers: headers })
      .then((response) => {
        console.log(response);
        setActiveGroup(response.data[0]);
      })
      .catch((error) => {
        console.error("Error fetching user groups:", error);
        setActiveGroup({ id: -1, name: "no groups", owner_mail: email });
      });
  };

  useEffect(() => {
    initActiveGroup();
  }, []);

  return (
    <ThemeProvider theme={useCustomTheme()}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, height: 70 }}
      >
        <Toolbar>
          <Box sx={{ flexGrow: 1, display: "flex", alignItems: "center" }}>
            <img
              src={logo}
              alt="EMSA Logo"
              style={{
                width: "70px",
                height: "70px",
                borderRadius: "30%",
                objectFit: "cover",
              }}
            />
            <Tabs
              value={selectedTab}
              onChange={handleTabChange}
              aria-label="main tabs"
              indicatorColor="secondary"
              textColor="secondary"
              sx={{ marginLeft: 2 }}
            >
              <Tab label="Memes" />
              <Tab label="Friends" />
            </Tabs>
          </Box>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>
      <Box sx={{ display: "flex", pt: 5 }}>
        {selectedTab === 0 && (
          <>
            <Drawer
              variant="permanent"
              sx={{
                width: drawerWidth,
                flexShrink: 0,
                [`& .MuiDrawer-paper`]: {
                  width: drawerWidth,
                  boxSizing: "border-box",
                  bgcolor: "background.paper",
                },
              }}
            >
              <Toolbar />
              <GroupList userEmail={email} onGroupClick={handleGroupClick} />
            </Drawer>
            <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
              <ManageMemes
                groupName={activeGroup?.name ?? "no group"}
                groupId={activeGroup?.id ?? -1}
              />
            </Box>
            <Drawer
              variant="permanent"
              anchor="right"
              sx={{
                width: drawerWidth,
                flexShrink: 0,
                [`& .MuiDrawer-paper`]: {
                  width: drawerWidth,
                  boxSizing: "border-box",
                  bgcolor: "background.paper",
                },
              }}
            >
              <Toolbar />
              <MembersList groupId={activeGroup?.id ?? -1} />
            </Drawer>
          </>
        )}
        {selectedTab === 1 && (
          <Box sx={{ flexGrow: 1, p: 3 }}>
            <FriendRequests userEmail={email} />
          </Box>
        )}
      </Box>
    </ThemeProvider>
  );
}
