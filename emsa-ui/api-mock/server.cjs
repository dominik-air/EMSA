const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const port = 8000;

app.use(bodyParser.json());
app.use(cors());

let userGroups = [
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

let users = [{
  username: 'demoUser',
  password: 'password123'
}];

app.post('/login', (req, res) => {
  const { username, password } = req.body;

  users.forEach(u => {
    if (username === u.username && password === u.password) {
      res.json({ token: 'some-auth-token' }); 
      return
    }
  });

  res.status(401).json({ error: 'Invalid credentials' });

});

app.post('/signup', (req, res) => {
  const { nickname, email, password } = req.body;

  if (!nickname || !email || !password) {
    return res.status(400).json({ message: 'Missing required fields' });
  }

  const newUser = {
    id: users.length + 1,
    email,
    password: password
  };

  users.push(newUser);

  res.status(201).json({ message: 'User registered successfully', user: newUser });
});

app.listen(port, () => {
  console.log(`Server is listening on port ${port}`);
});
