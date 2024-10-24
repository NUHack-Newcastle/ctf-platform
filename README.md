A Python/Flask-based CTF platform built for [NUHack Alpha 2024](https://github.com/NUHack-Newcastle/nuhack-alpha-2024), but which can be used for any CTF event. The platform uses a system where challenges are written as build/compile scripts that adhere to a standard, enabling procedural flag generation. For each challenge-team combination, the server generates a unique flag using an HMAC, embedding it during compilation - this system supports distributed validation across multiple servers, allowing teams to receive different flags while ensuring consistency. Each server can independently verify flags by following the same HMAC-based validation process, ensuring scalable, secure, and consistent flag distribution and validation across different challenges and platforms.

See [/docs](/docs) for further documentation.

# Screenshots
More screenshots can be found in [/docs/screenshots](/docs/screenshots).

![Login page (dark mode)](/docs/screenshots/login_dark.png)
![Dashboard](/docs/screenshots/dashboard.png)
![Challenges list page](/docs/screenshots/challenges_list.png)
![Challenge/flag page](/docs/screenshots/challenge_2.png)
![Avatar Editor](/docs/screenshots/avatar_editor.png)
![Team setup page](/docs/screenshots/team_setup.png)

# Setup

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

At this time, it is necessary to add the first user to your platform database manually. This user should have the `admin` role - subsequent users can be invited to
the platform in a user-friendly manner.

```
INSERT INTO "main"."user"("username","email","password","role","avatar_style","avatar_seed","avatar_options","team","team_pending"
VALUES ('your_username_here','your_email_here','your_password_bcrypt_hash_here','admin','shapes','avatar_random_seed','{}',NULL,0);
```

The **password** field uses a bcrypt hash. You can manually generate one with suitable security parameters at [bcrypt.online](https://bcrypt.online/). The **role**
field should be set to `admin` for platform staff, and left empty for all other users. Other roles may be supported in future versions.
