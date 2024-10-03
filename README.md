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
