const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const port = 8000;

app.use(bodyParser.json());
app.use(cors());

const userGroups = [
  {
    email: 'email@example.com',
    groups: ['kociaki', 'bigos', 'baseniarze'],
  },
  {
    email: 'other@example.com',
    groups: ['abcd', '1234'],
  },
];

app.get('/user_groups/:email', (req, res) => {
  const { email } = req.params;
  const userGroup = userGroups.find((group) => group.email === email);
  if (userGroup) {
    res.json({ groups: userGroup.groups });
  } else {
    res.status(404).json({ error: 'User not found' });
  }
});

app.post('/user_groups', (req, res) => {
  const { email, group_name } = req.body;
  const userGroup = userGroups.find((group) => group.email === email);
  if (userGroup) {
    userGroup.groups.push(group_name);
    res.json({ groups: userGroup.groups });
  } else {
    res.status(404).json({ error: 'User not found' });
  }
});


app.listen(port, () => {
  console.log(`Server is listening on port ${port}`);
});
