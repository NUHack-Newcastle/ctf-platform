# Challenge Constraints
---
*Please note that the platform currently only supports "static" challenges. That is, challenges which consist of a build script to produce a number of challenge files given a certain flag to embed. Challenges which involve connecting to a dedicated per-team server (so, most networking challenges) were planned to be part of the platform, but this was cut to save time.*

*The planned "dynamic" challenge functionality, where challenges can be expressed as Docker images and are automatically deployed to the cloud when a team is created, is mostly not implemented. PRs are welcomed by anyone who would like to complete this implementation.*

---

The basic rule of the platform, and what allows for secure per-team flags, is that challenge designers never choose the flag. Instead, the challenge must be constructed in a way that allows the orchestration (build) server to build the challenge files given a particular flag. Challenges themselves should consist of a build script, which is given the correct flag and should produce all the challenge files customised to that flag, which will then be given to participants.

For this reason, it's not possible to simply add a new challenge with a fixed flag -- the challenge must use the flag the server has created for that challenge/team combination. A workaround for if you *really* want to use existing fixed-flag challenges is that you can have your build script generate a file containing the correct flag encrypted using your fixed flag as a key. Then each team just has to use your fixed flag to decrypt their team's flag from the file. This effectively bypasses the per-team flag system though, and can get annoying for participants, so it shouldn't be used for new challenges.
