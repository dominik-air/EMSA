const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const port = 8000;

app.use(bodyParser.json());
app.use(cors());

let users = [{
  username: 'bob@example.com',
  password: 'password'
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


let friends = {
  "alice@example.com": ["bob@example.com", "charlie@example.com"],
  "bob@example.com": ["alice@example.com"]
};

let groups = {
  1: { name: "Group One", owner: "alice@example.com" },
  2: { name: "Group Two", owner: "bob@example.com" }
};

let groupMembers = {
  1: ["alice@example.com", "bob@example.com"],
  2: ["bob@example.com", "charlie@example.com"]
};

let groupContent = {
  1: [
    { type: "image", url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg", tags: ["funny"] },
    { type: "link", url: "https://cdn1.vectorstock.com/i/1000x1000/60/40/nerd-face-emoji-clever-emoticon-with-glasses-vector-28926040.jpg", tags: ["nerd", "cute"] }
  ],
  2: [
    { type: "image", url: "https://fwcdn.pl/ppo/50/13/55013/449913.2.jpg", tags: ["ryan gosling"] }
  ]
};

let nextGroupId = 3;


app.post('/add_friend', (req, res) => {
  const { user_email, friend_email } = req.body;
  friends[user_email] = friends[user_email] || [];
  friends[user_email].push(friend_email);
  res.status(200).send();
});

app.delete('/remove_friend', (req, res) => {
  const { user_email, friend_email } = req.body;
  friends[user_email] = friends[user_email].filter(email => email !== friend_email);
  res.status(200).send();
});

app.get('/user_friends', (req, res) => {
  const user_email = req.query.user_email;
  res.json(friends[user_email] || []);
});

app.post('/create_group', (req, res) => {
  const { name, owner_mail } = req.body;
  const groupId = nextGroupId++;
  groups[groupId] = { name, owner: owner_mail };
  groupMembers[groupId] = [];
  res.json({ group_id: groupId });
});

app.post('/add_group_members', (req, res) => {
  const { group_id, members } = req.body;
  groupMembers[group_id] = groupMembers[group_id].concat(members);
  res.status(200).send();
});

app.get('/user_groups', (req, res) => {
  const user_mail = req.query.user_mail;
  const userGroups = Object.entries(groups).filter(([id, group]) => group.owner === user_mail || groupMembers[id].includes(user_mail));
  res.json(userGroups.map(([id, group]) => group.name));
});

app.get('/group_members', (req, res) => {
  const group_id = parseInt(req.query.group_id);
  res.json(groupMembers[group_id] || []);
});

app.get('/group_content', (req, res) => {
  const { search_term, group_id } = req.query;
  let content = groupContent[group_id] || [];
  if (search_term) {
    content = content.filter(meme =>
      meme.tags.some(tag => tag.toLowerCase().includes(search_term.toLowerCase()))
    );
  }
  res.json(content);
});



app.listen(port, () => {
  console.log(`Server is listening on port ${port}`);
});


app.get('/friend_requests/:email', (req, res) => {
    const { email } = req.params;
    if (userFriends[email]) {
      res.json(convertToNameObjects(userFriends[email]));
    } else {
      res.status(404).json({ error: 'No friend requests found for this email' });
    }
});