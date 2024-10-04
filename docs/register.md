# Registering Participants
The CTF platform is designed for private, invite-only events. As such, the registration process differs from typical platforms.

To register a participant, a platform admin must generate an invite link tied to the participant's email address. This invite link includes a token signed by the platform, allowing the creation of a new account with that email. This approach eliminates the need for activation emails, assuming staff send the link only to the corresponding email address. Participants will not be able to register until the event begins, as the link will only be valid once the event has started. **The platform itself does not send invitation emails;** it only generates the links, which staff are responsible for incorporating into their own invitation format.

This process is both private and secure while remaining flexible. The platform doesn't store any invite records, it relies entirely on the token signature in the link itself to prove that an invite is valid. If staff generate an invite for the wrong email address, they can simply discard/forget the link to practically delete the invite (provided they haven't distributed it already). Admins can generate invite links at any time, even during the event, without needing to update database records. This is particularly useful if participants need help registering after the event has started -- staff can quickly generate new links as needed. You can distribute the links however you like (even on paper, or as a QR code on event tickets), since the platform doesn't require tracking invites or storing personal information ahead of time. This is a great privacy-first approach suitable for events with certain participants may wish to exercise particular care with their personal information.

Invite links can be configured with an early access flag, useful for staff or event helpers who need platform access before the event begins. However, note that the platform assumes participant accounts can only exist after the competition starts. Therefore, if this flag is used, accounts created with it will have immediate access to challenges and can submit flags as soon as they recieve their invite. For this reason, it should not be used for regular participants.

To generate an invite link, visit `/admin` as an admin user, enter the participant email address and submit. The platform will generate a link and display it to be copy/pasted.