const User = require("../models/users");
const argon2 = require("argon2");


exports.postLogin = async (req, res) => {
    const { email, password, rememberMe } = req.body;

    try {
        const user = await User.findOne({ email });

        if (!user) {
            return res.status(404).send("User not found");
        }

        if (user.approved === false) {
            return res.status(401).send("User not approved");
        }

        const passwordValid = await argon2.verify(user.password, password);
        if (!passwordValid) {
            return res.status(401).send("Invalid password");
        }

        req.session.user = {
            id: user._id,
            email: user.email,
            name: user.name,
            surname: user.surname,
            fields : user.fields,
            isSurvey: user.isSurvey

        };
        req.session.loggedIn = true;

        req.session.cookie.maxAge = rememberMe
            ? 30 * 24 * 60 * 60 * 1000
            : 24 * 60 * 60 * 1000;

        await new Promise((resolve, reject) => {
            req.session.save((err) => {
                if (err) reject(err);
                else resolve();
            });
        });

        return res.status(200).json({ session: req.session });

    } catch (err) {
        console.error("Error during login:", err);
        return res.status(500).send("Internal server error");
    }
};

exports.postRegister = async (req, res) => {
  const userEmail = req.body.email;
  const userName = req.body.name;
  const userSurname = req.body.surname;
  const userPassword = req.body.password;


  if (!userEmail || !userName || !userSurname || !userPassword) {
    return res.status(400).send("All fields are required");
  }

  try {
    const existingUser = await User.findOne({ email: userEmail });
    if (existingUser) {
      return res.status(400).send("User already exists");
    }

    const hashedPassword = await argon2.hash(userPassword);

    const newUser = new User({
      email: userEmail,
      name: userName,
      surname: userSurname,
      password: hashedPassword,
    });

    await newUser.save();
    return res.status(201).send("User created");
  } catch (err) {
    console.error("Error during user creation:", err);
    return res.status(500).send("Internal server error");
  }
};

exports.getLogout = (req, res) => {
  if (req.session) {
    req.session.destroy((err) => {
      if (err) {
        console.error("Error during logout:", err);
        return res.status(500).send("Internal server error");
      }
      return res.status(200).send("User logged out");
    });
  } else {
    return res.status(400).send("No active session");
  }
};

exports.isAuth = (req, res) => {
  console.log("req.session", req.session);
  if (req.session && req.session.user) {
      return res.status(200).json({ user: req.session.user });
  } else {
      return res.status(401).json({ message: "Unauthorized" });
  }
};

