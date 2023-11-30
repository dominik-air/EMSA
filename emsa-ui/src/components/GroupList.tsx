import React from "react";
import {
  List,
  ListItem,
  Button,
  Typography,
  ListItemButton,
} from "@mui/material";

const GroupList: React.FC = () => {
  const groups = ["group 1", "group 2", "group 3", "group 4", "group 5"];

  const handleAddNewGroup = () => {
    console.log(`Opening add new group pop up!`);
  };

  const handleGroupClick = (group: string) => {
    console.log(`Redirecting to the ${group}'s Homepage!`);
  };

  return (
    <List sx={{ width: "100%", bgcolor: "background.paper" }}>
      <ListItem>
        <Typography
          variant="h6"
          component="div"
          sx={{ width: "100%", textAlign: "center" }}
        >
          My groups
        </Typography>
      </ListItem>
      <ListItem>
        <Button
          variant="contained"
          fullWidth
          onClick={() => handleAddNewGroup()}
        >
          Create new group
        </Button>
      </ListItem>
      {groups.map((group, index) => (
        <ListItem
          key={index}
          sx={{ justifyContent: "center", display: "flex" }}
        >
          <ListItemButton
            sx={{ textAlign: "center", justifyContent: "center" }}
            onClick={() => handleGroupClick(group)}
          >
            {group}
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  );
};

export default GroupList;
